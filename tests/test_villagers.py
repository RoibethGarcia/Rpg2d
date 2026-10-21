"""Habitantes de Hondonada: ocupación, conversación y ventana modal."""
from copy import deepcopy
import unittest
from unittest.mock import patch

from game.model import GameState, Motion


class VillagerTests(unittest.TestCase):
    def villagers(self, state):
        npcs = [o for o in state.objects if o['kind'] == 'npc']
        self.assertEqual(len(npcs), 2, 'Faltan los dos habitantes estáticos de Hondonada')
        return npcs

    def approach(self, state, npc):
        state.player.cell = next(c for c in state.grid.neighbors(npc['cell'])
                                 if c not in state.occupied('vera'))

    def test_two_distinct_villagers_use_same_art_without_enemies_or_rewards(self):
        state = GameState.new()
        npcs = self.villagers(state)
        self.assertEqual(len({o['id'] for o in npcs}), 2)
        self.assertEqual({o['sprite'] for o in npcs}, {'villager'})
        self.assertFalse(state.enemies)
        occupied = state.occupied('vera')
        self.assertTrue(all(o['blocking'] and o['cell'] in occupied for o in npcs))
        for npc in npcs:
            self.assertTrue(any(state.grid.find_path(state.player.cell, c, occupied)
                                for c in state.grid.neighbors(npc['cell']) if c not in occupied))
        self.assertTrue(state.grid.find_path(state.player.cell, (4,10), occupied))
        self.assertTrue(state.grid.find_path(state.player.cell, (2,11), occupied))

    def test_walking_into_npc_does_not_move_or_start_combat_or_dialogue(self):
        state = GameState.new()
        npc = self.villagers(state)[0]
        self.approach(state, npc)
        before = (state.player.cell, state.player.hp, state.player.ap, state.medkits)
        self.assertFalse(state.preview_path(npc['cell']))
        delta = next(d for d, c in state.grid.step_directions[state.player.cell].items() if c == npc['cell'])
        self.assertFalse(state.move_direction(delta))
        self.assertEqual((state.player.cell, state.player.hp, state.player.ap, state.medkits), before)
        self.assertEqual(state.mode, 'exploration')
        self.assertIsNone(state.active_dialogue)
        self.assertFalse(state.motions)

    def test_neighbor_e_opens_pages_and_repeating_does_not_change_resources(self):
        state = GameState.new()
        npc = self.villagers(state)[0]
        self.approach(state, npc)
        resources = (state.player.hp, state.player.ap, state.medkits, state.credential)
        for _ in range(2):
            self.assertTrue(state.interact())
            self.assertEqual(state.active_dialogue.npc_id, npc['id'])
            self.assertEqual(state.active_dialogue.pages, tuple(npc['dialogue']))
            self.assertEqual(state.active_dialogue.index, 0)
            for index in range(len(npc['dialogue'])):
                self.assertEqual(state.active_dialogue.index, index)
                self.assertTrue(state.advance_dialogue())
            self.assertIsNone(state.active_dialogue)
        self.assertEqual(state.world.talked_to, {npc['id']})
        self.assertEqual((state.player.hp, state.player.ap, state.medkits, state.credential), resources)

    def test_dialogue_freezes_simulation_and_rejects_gameplay_commands(self):
        state = GameState.new()
        npc = self.villagers(state)[0]
        self.approach(state, npc)
        self.assertTrue(state.interact())
        before = deepcopy({k:v for k,v in vars(state).items() if k != 'message'})
        for command in (lambda: state.move_direction((1,0)), lambda: state.set_destination((4,10)),
                        state.attack, state.heal, state.end_turn, state.interact,
                        lambda: state.travel('to_puesto'), state.cancel_route):
            self.assertFalse(command())
        state.update(5)
        self.assertEqual({k:v for k,v in vars(state).items() if k != 'message'}, before)
        self.assertTrue(state.close_dialogue())
        self.assertIsNone(state.active_dialogue)

    def test_far_same_cell_and_busy_contexts_cannot_start_dialogue(self):
        for reason in ('far','same','motion','route','pending','combat','victory','defeat'):
            state = GameState.new()
            npc = self.villagers(state)[0]
            self.approach(state, npc)
            if reason == 'far': state.player.cell = (0,0)
            elif reason == 'same': state.player.cell = npc['cell']
            elif reason == 'motion': state.motions['vera'] = Motion(state.player.cell, npc['cell'])
            elif reason == 'route': state.route = [npc['cell']]
            elif reason == 'pending': state._pending_direction = (1,0)
            else: state.mode = reason
            self.assertFalse(state.interact(), reason)
            self.assertIsNone(state.active_dialogue)

    def test_talk_history_is_independent_persistent_and_reset_on_new_game(self):
        state = GameState.new()
        npcs = self.villagers(state)
        for npc in npcs:
            self.approach(state, npc)
            self.assertTrue(state.interact())
            self.assertTrue(state.close_dialogue())
            self.assertIn(npc['id'], state.world.talked_to)
        history = set(state.world.talked_to)
        state.player.cell = (4,10)
        self.assertTrue(state.travel('to_puesto'))
        state.player.cell = (1,10)
        self.assertTrue(state.travel('to_hondonada'))
        self.assertEqual(state.world.talked_to, history)
        clean = GameState.new()
        self.assertFalse(clean.world.talked_to)
        self.assertIsNone(clean.active_dialogue)

    def test_both_villagers_are_reachable_and_talkable_by_public_commands(self):
        state = GameState.new()
        for npc in self.villagers(state):
            goal = next(c for c in state.grid.neighbors(npc['cell']) if c not in state.occupied('vera'))
            self.assertTrue(state.set_destination(goal))
            for _ in range(3000):
                state.update(.02)
                if not state.motions and not state.route:
                    break
            self.assertEqual(state.player.cell,goal)
            self.assertTrue(state.interact())
            while state.active_dialogue:
                self.assertTrue(state.advance_dialogue())
        self.assertTrue(state.set_destination((4,10)))
        for _ in range(3000):
            state.update(.02)
            if not state.motions and not state.route:
                break
        self.assertEqual(state.player.cell,(4,10))
        self.assertTrue(state.travel('to_puesto'))
        self.assertEqual((state.map_id,state.player.hp,state.player.ap,state.medkits),('puesto',30,6,1))

    def test_new_parties_do_not_share_npc_dialogue_lists_or_history(self):
        first, second = GameState.new(), GameState.new()
        a,b = self.villagers(first)[0], self.villagers(second)[0]
        a['dialogue'][0] = 'Texto cambiado solo en esta partida'
        first.world.talked_to.add(a['id'])
        self.assertNotEqual(a['dialogue'][0],b['dialogue'][0])
        self.assertFalse(second.world.talked_to)


class DialogueWindowTests(unittest.TestCase):
    def setUp(self):
        import pygame
        from game.app import LastValveGame
        self.pygame = pygame
        self.game = LastValveGame(audio_enabled=False)
        self.game.start_new_game()
        self.scene = self.game.scenes['play']

    def tearDown(self):
        self.pygame.quit()

    def open_dialogue(self):
        state = self.game.state
        npcs = [o for o in state.objects if o['kind'] == 'npc']
        self.assertEqual(len(npcs), 2, 'Faltan NPC interactivos')
        state.player.cell = state.grid.neighbors(npcs[0]['cell'])[0]
        self.scene.handle_events([self.pygame.event.Event(self.pygame.KEYDOWN,key=self.pygame.K_e)])
        self.assertIsNotNone(state.active_dialogue)

    def test_modal_captures_clicks_buttons_and_keys_and_escape_closes(self):
        self.open_dialogue()
        state = self.game.state
        position = state.player.cell
        self.scene.handle_events([
            self.pygame.event.Event(self.pygame.MOUSEBUTTONDOWN,button=1,pos=(1100,750)),
            self.pygame.event.Event(self.pygame.KEYDOWN,key=self.pygame.K_w),
            self.pygame.event.Event(self.pygame.MOUSEBUTTONDOWN,button=1,pos=(550,300))])
        self.assertIs(self.game.current_scene, self.scene)
        self.assertEqual(state.player.cell, position)
        self.assertFalse(state.motions or state.route)
        self.scene.handle_events([self.pygame.event.Event(self.pygame.KEYDOWN,key=self.pygame.K_ESCAPE)])
        self.assertIsNone(state.active_dialogue)
        self.assertFalse(state.motions or state.route)

    def test_continue_button_and_keyboard_advance_without_click_through(self):
        self.open_dialogue()
        self.assertTrue(hasattr(self.scene, 'dialogue_view'), 'Falta ventana con arte propio')
        state = self.game.state
        self.scene.handle_events([self.pygame.event.Event(self.pygame.MOUSEBUTTONDOWN,button=1,
                                                        pos=self.scene.dialogue_view.continue_rect.center)])
        self.assertEqual(state.active_dialogue.index, 1)
        self.scene.handle_events([self.pygame.event.Event(self.pygame.KEYDOWN,key=self.pygame.K_RETURN),
                                  self.pygame.event.Event(self.pygame.KEYDOWN,key=self.pygame.K_w)])
        self.assertIsNone(state.active_dialogue)
        self.assertFalse(state.motions or state.route)

    def test_modal_does_not_duplicate_dialogue_in_regular_message_strip(self):
        self.open_dialogue()
        text = self.game.state.active_dialogue.text
        with patch.object(self.scene.type,'wrapped',wraps=self.scene.type.wrapped) as wrapped:
            self.game.draw_game_elements()
        self.assertNotIn(text,[call.args[1] for call in wrapped.call_args_list])

    def test_talk_hint_matches_one_or_two_navigable_steps_and_hides_when_unavailable(self):
        state = self.game.state
        npc = next(o for o in state.objects if o['id'] == 'villager_plaza')
        occupied = state.occupied('vera')
        for steps in (1, 2, 3, 0):
            with self.subTest(steps=steps):
                state.player.cell = (npc['cell'] if steps == 0 else
                                     next(c for c in state.grid.adjacency if c not in occupied
                                          and len(state.grid.find_path(c, npc['cell'], occupied, True)) == steps))
                with patch.object(self.scene.renderer.type, 'text', wraps=self.scene.renderer.type.text) as text:
                    self.game.draw_game_elements()
                hints = [call for call in text.call_args_list if call.args[1] == 'E: Hablar']
                self.assertEqual(bool(hints), steps in (1, 2))
        state.player.cell = next(c for c in state.grid.adjacency if c not in occupied
                                 and len(state.grid.find_path(c, npc['cell'], occupied, True)) == 2)
        self.assertTrue(state.interact())
        with patch.object(self.scene.renderer.type, 'text', wraps=self.scene.renderer.type.text) as text:
            self.game.draw_game_elements()
        self.assertNotIn('E: Hablar', [call.args[1] for call in text.call_args_list])

    def test_every_page_fits_declared_regions_and_exterior_alpha_is_preserved(self):
        self.open_dialogue()
        state = self.game.state
        view = self.scene.dialogue_view
        self.assertEqual(view.skin.get_at((0,0)).a,0)
        for npc in [o for o in state.objects if o['kind']=='npc']:
            state.close_dialogue()
            state.player.cell = state.grid.neighbors(npc['cell'])[0]
            self.assertTrue(state.interact())
            while state.active_dialogue:
                self.game.draw_game_elements()
                self.assertTrue(all(line.get_width() <= view.regions['body'].width for line in view._lines))
                self.assertLessEqual(len(view._lines)*(view.body_font.get_linesize()+3),view.regions['body'].height)
                self.assertLessEqual(view._name.get_width(),view.regions['name'].width)
                self.assertLessEqual(view._hint.get_width(),view.regions['hint'].width)
                self.assertLessEqual(view._button.get_width(),view.continue_rect.width)
                state.advance_dialogue()

    def test_world_npcs_and_dialogue_skin_are_cached_and_render_without_domain_changes(self):
        self.open_dialogue()
        state = self.game.state
        before = deepcopy(vars(state))
        self.assertIn('villager', self.game.manifest['images'])
        self.assertIn('dialogue_frame', self.game.manifest['images'])
        with patch.object(self.game.assets,'get_image',side_effect=AssertionError('IO por frame')):
            self.game.draw_game_elements()
            self.game.draw_game_elements()
        self.assertEqual(vars(state), before)
        self.assertEqual(len(self.scene.renderer.villagers), 2)
        self.assertTrue(all(actor.image.get_height() < 45 for actor in self.scene.renderer.villagers.values()))

    def test_villager_silhouettes_stay_visible_and_cache_clears_on_travel(self):
        from game.render import WorldVillager
        real_draw = WorldVillager.draw
        expected = {}
        def draw(actor,surface):
            real_draw(actor,surface)
            expected[actor.npc['id']] = surface.copy()
        with patch.object(WorldVillager,'draw',draw):
            self.game.draw_game_elements()
        renderer = self.scene.renderer
        self.assertEqual(len(renderer.villagers),2)
        for uid, actor in renderer.villagers.items():
            visible = opaque = 0
            for x in range(actor.image.get_width()):
                for y in range(actor.image.get_height()):
                    if actor.image.get_at((x,y)).a >= 128:
                        opaque += 1
                        p = (actor.rect.x+x,actor.rect.y+y)
                        visible += self.game.screen.get_at(p) == expected[uid].get_at(p)
            self.assertGreater(visible/opaque,.65,uid)
        state = self.game.state
        state.player.cell = (4,10)
        self.assertTrue(self.scene.command('travel','to_puesto'))
        self.assertFalse(renderer.villagers)
        self.game.draw_game_elements()
        self.assertFalse(renderer.villagers)

