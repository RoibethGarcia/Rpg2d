"""Planta ilustrada: suelo conectado, encuentros persistentes y válvula final."""
from copy import deepcopy
import unittest
from unittest.mock import patch

from game.model import GameState, Motion


def enter_planta():
    state = GameState.new()
    state.player.cell = (4, 10)
    assert state.travel('to_puesto')
    state.player.cell = (6, 8)
    assert state.interact()
    state.player.cell = (9, 8)
    assert state.travel('to_planta')
    return state


class PlantaTests(unittest.TestCase):
    def test_authored_ground_has_three_guards_boss_two_kits_and_reachable_objects(self):
        state = enter_planta()
        self.assertTrue(state.grid.adjacency, 'Planta necesita navegación sobre su ilustración')
        self.assertEqual(set(state.enemies), {'guard3', 'guard4', 'guard5', 'boss'})
        self.assertEqual([(u.hp, u.damage) for u in state.enemies.values()],
                         [(16, 3), (16, 3), (16, 3), (48, 4)])
        self.assertEqual({o['id'] for o in state.objects if o['kind'] == 'medkit'}, {'kit2', 'kit3'})
        occupied = {u.cell for u in state.enemies.values()}
        for obj in state.objects:
            self.assertTrue(state.grid.walkable(obj['cell']), obj)
            self.assertTrue(any(c == state.player.cell or state.grid.find_path(state.player.cell, c, occupied)
                                for c in state.grid.neighbors(obj['cell']) if c not in occupied), obj)
        for uid, patrol in state.patrols.items():
            cells = [tuple(c) for c in patrol['cells']]
            self.assertNotIn(state.enemies[uid].cell, state.world.reserved_spawns)
            self.assertTrue(all(state.grid.can_step(a, b) for a, b in zip(cells, cells[1:] + cells[:1])))

    def test_two_kits_are_unique_do_not_heal_and_survive_round_trip(self):
        state = enter_planta()
        state.player.hp = 19
        for oid in ('kit2', 'kit3'):
            obj = next(o for o in state.objects if o['id'] == oid)
            state.player.cell = obj['cell']
            self.assertTrue(state.interact())
            self.assertIn(oid, state.collected)
        self.assertEqual((state.medkits, state.player.hp), (3, 19))
        state.player.cell = (9, 8)
        self.assertTrue(state.travel('to_puesto'))
        self.assertTrue(state.travel('to_planta'))
        for oid in ('kit2', 'kit3'):
            state.player.cell = next(o['cell'] for o in state.objects if o['id'] == oid)
            self.assertFalse(state.interact())
        self.assertEqual((state.medkits, state.player.hp), (3, 19))

    def test_final_valve_uses_real_graph_neighbor_not_numeric_labels(self):
        state = enter_planta()
        panel = next(o for o in state.objects if o['kind'] == 'panel')
        # Un vecino autorado no tiene por qué diferir en una unidad numérica.
        approach = next(c for c in state.grid.neighbors(panel['cell'])
                        if sum(abs(a-b) for a, b in zip(c, panel['cell'])) != 1)
        state.player.cell = approach
        before = (state.player.hp, state.player.ap, state.medkits, deepcopy(state.opened))
        self.assertFalse(state.interact())
        self.assertEqual((state.player.hp, state.player.ap, state.medkits, state.opened), before)
        state.credential = True
        self.assertTrue(state.interact())
        self.assertEqual(state.mode, 'victory')
        self.assertIn('panel', state.opened)
        self.assertFalse(state.move_direction((1, 0)))
        self.assertFalse(state.attack())

    def test_valve_rejects_busy_far_same_cell_and_combat_atomically(self):
        for reason in ('motion', 'patrol_motion', 'route', 'pending', 'combat', 'far', 'same_cell'):
            state = enter_planta()
            panel = next(o for o in state.objects if o['kind'] == 'panel')
            state.player.cell = next(iter(state.grid.neighbors(panel['cell'])))
            state.credential = True
            if reason == 'motion':
                state.motions['vera'] = Motion(state.player.cell, panel['cell'])
            elif reason == 'patrol_motion':
                enemy = state.enemies['guard3']
                state.motions[enemy.id] = Motion(enemy.cell, tuple(state.patrols[enemy.id]['cells'][1]))
            elif reason == 'route':
                state.route = [panel['cell']]
            elif reason == 'pending':
                state._pending_direction = (1, 0)
            elif reason == 'combat':
                state._begin_combat(state.enemies['boss'])
            elif reason == 'far':
                state.player.cell = (5, 5)
            else:
                state.player.cell = panel['cell']
            before = deepcopy({k: v for k, v in vars(state).items() if k != 'message'})
            self.assertFalse(state.interact(), reason)
            self.assertEqual({k: v for k, v in vars(state).items() if k != 'message'}, before, reason)

    def test_boss_death_grants_credential_not_victory_and_persists_on_return(self):
        state = enter_planta()
        boss = state.enemies['boss']
        state.player.cell = next(iter(state.grid.neighbors(boss.cell)))
        state._begin_combat(boss)
        boss.hp = 7
        self.assertTrue(state.attack(True))
        self.assertEqual((state.mode, state.credential, boss.hp), ('exploration', True, 0))
        resources = (state.player.hp, state.medkits)
        state.player.cell = (9, 8)
        self.assertTrue(state.travel('to_puesto'))
        self.assertTrue(state.travel('to_planta'))
        self.assertIs(state.enemies['boss'], boss)
        self.assertEqual((boss.hp, state.credential, state.player.hp, state.medkits), (0, True, *resources))

    def test_each_planta_patrol_initiates_only_its_duel_and_freezes_other_maps(self):
        for uid in ('guard3', 'guard4', 'guard5', 'boss'):
            state = enter_planta()
            state.player.cell = tuple(state.patrols[uid]['cells'][1])
            for other in state.enemies:
                state._patrol_wait[other] = 100
            state._patrol_wait[uid] = 0
            state.update(.02)
            self.assertEqual((state.mode, state.active_enemy_id, state.player.ap), ('combat', uid, 6))
            timers = deepcopy(state._patrol_wait)
            inactive = {m: deepcopy(state.maps[m]) for m in ('hondonada', 'puesto')}
            state.update(3)
            self.assertEqual(state._patrol_wait, timers)
            self.assertEqual({m: state.maps[m] for m in inactive}, inactive)
            self.assertFalse(state.motions)

    def test_distribution_and_register_explain_story_without_resource_rewards(self):
        state = enter_planta()
        before = (state.player.hp, state.player.ap, state.medkits, state.credential)
        for oid, text in (('distribution', 'depósitos'), ('register', 'protocolo')):
            obj = next(o for o in state.objects if o['id'] == oid)
            state.player.cell = obj['cell']
            self.assertTrue(state.interact())
            self.assertIn(text, state.message)
            self.assertEqual((state.player.hp, state.player.ap, state.medkits, state.credential), before)


class PlantaRenderingTests(unittest.TestCase):
    def setUp(self):
        import pygame
        from game.app import LastValveGame
        self.pygame = pygame
        self.game = LastValveGame(audio_enabled=False)
        self.game.state = enter_planta()
        self.game.scenes['play'].reset()
        self.renderer = self.game.scenes['play'].renderer

    def tearDown(self):
        self.pygame.quit()

    def test_lower_access_follows_stair_from_south_landing_and_crane_is_foreground(self):
        from game.hondonada import AuthoredLayout
        layout = AuthoredLayout.load('planta')
        stair = layout.stairs['escalera_patio']
        self.assertEqual(layout.nodes[stair[0]]['center'], [385,548])
        self.assertEqual(layout.nodes[stair[-1]]['center'], [451,487])
        self.assertIn('grua_acceso', {l['id'] for l in layout.data['layers']})

    def test_every_ground_center_is_selectable_and_edges_avoid_foregrounds(self):
        from game.hondonada import point_in_polygon
        self.assertTrue(hasattr(self.renderer.projection, 'layout'), 'Falta planta por capas')
        projection = self.renderer.projection
        layout = projection.layout
        self.assertGreaterEqual(len(layout.stairs), 3)
        for cell in layout.nodes:
            self.assertEqual(projection.pick(*projection.center(cell)), cell)
        for a, b in layout.data['edges']:
            start, end = (layout.nodes[tuple(c)]['center'] for c in (a, b))
            for i in range(21):
                point = tuple(x + (y-x)*i/20 for x, y in zip(start, end))
                self.assertFalse(any(point_in_polygon(point, l['polygon']) for l in layout.data['layers']
                                     if not l.get('route_behind')), (a,b,point))
        for point in ((30, 30), (735, 820), (1160, 190), (695, 545), (490, 780)):
            self.assertEqual(projection.pick(*projection.screen(point)), (-1, -1), point)

    def test_cached_plate_five_actors_valve_and_proportional_boss_without_domain_mutation(self):
        from game.render import WorldActor
        self.assertIn('planta', self.renderer.layered_maps)
        state = self.game.state
        before = deepcopy(vars(state))
        calls = []
        real_draw = WorldActor.draw
        def draw(actor, surface):
            calls.append(actor.unit.id)
            real_draw(actor, surface)
        with patch.object(self.game.assets, 'get_image', side_effect=AssertionError('IO por frame')):
            with patch.object(self.renderer, 'tile', side_effect=AssertionError('Suelo ficticio')):
                with patch.object(WorldActor, 'draw', draw):
                    self.renderer.draw(self.game.screen, state, None)
        self.assertCountEqual(calls, ['vera', 'guard3', 'guard4', 'guard5', 'boss'])
        self.assertEqual(vars(state), before)
        self.assertGreater(self.renderer.actors['boss'].image.get_height(),
                           self.renderer.actors['guard3'].image.get_height())

    def test_initial_actors_keep_visible_silhouettes_and_stairs_interpolate_feet(self):
        from game.render import WorldActor
        expected = {}
        real_draw = WorldActor.draw
        def draw(actor, surface):
            real_draw(actor, surface)
            expected[actor.unit.id] = surface.copy()
        with patch.object(WorldActor, 'draw', draw):
            self.renderer.draw(self.game.screen, self.game.state, None)
        for uid, actor in self.renderer.actors.items():
            visible = opaque = 0
            for x in range(actor.image.get_width()):
                for y in range(actor.image.get_height()):
                    if actor.image.get_at((x,y)).a >= 128:
                        opaque += 1
                        point = (actor.rect.x+x, actor.rect.y+y)
                        visible += self.game.screen.get_at(point) == expected[uid].get_at(point)
            self.assertGreater(visible/opaque, .65, (uid, visible/opaque))
        state = self.game.state
        stair = self.renderer.planta.layout.stairs['escalera_patio']
        state.player.cell = stair[0]
        state.motions['vera'] = Motion(stair[0], stair[1], elapsed=.07, duration=.14)
        self.renderer.draw(self.game.screen, state, None)
        a,b = (self.renderer.projection.center(c) for c in stair[:2])
        self.assertEqual(self.renderer.actors['vera'].foot, tuple((x+y)/2 for x,y in zip(a,b)))
        self.assertEqual(state.player.cell, stair[0])

