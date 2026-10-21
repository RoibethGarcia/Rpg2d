"""Ataques: hechos del dominio, clips sin callbacks y presentación SDL dummy."""
import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
import pygame
from game.app import LastValveGame
from game.model import GameState, Unit
from game.world import GridMap

ROOT = Path(__file__).resolve().parents[1]


def combat(*, boss=False):
    state = GameState(GridMap(24, 16), Unit('vera', 'Vera', (2, 3), 30, 30),
                      {'enemy': Unit('enemy', 'Custodia', (3, 3), 40, 40, boss=boss)})
    state.move_direction((1, 0))
    return state


class AttackSignalTests(unittest.TestCase):
    def test_valid_attack_records_one_fact_after_applying_cost_and_damage(self):
        state = combat()
        self.assertTrue(state.attack())
        self.assertTrue(hasattr(state, 'last_attacks'), 'Falta señal de ataque válido para presentación')
        self.assertEqual(set(state.last_attacks), {'vera'})
        action = state.last_attacks['vera']
        self.assertEqual((action.attacker_id, action.target_cell), ('vera', (3, 3)))
        self.assertEqual((state.player.ap, state.enemies['enemy'].hp), (4, 36))
        state.update(1)
        self.assertEqual((state.player.ap, state.enemies['enemy'].hp), (4, 36))
        self.assertIs(state.last_attacks['vera'], action)


class AttackAssetTests(unittest.TestCase):
    def test_three_local_attack_sheets_have_explicit_frame_contracts(self):
        manifest = json.loads((ROOT / 'assets/manifest.json').read_text())
        for role in ('vera', 'guard', 'boss'):
            name = f'{role}_attack'
            self.assertIn(name, manifest['images'], 'Falta hoja de ataques integrada')
            record = manifest['images'][name]
            self.assertEqual(record['size'], [2172, 724])
            self.assertEqual(record['source_type'], 'user_supplied')
            self.assertEqual(record['redistribution_status'], 'pending_confirmation')
            self.assertNotIn('license', record)
            path = ROOT / record['path']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record['sha256'])
            image = pygame.image.load(path)
            self.assertEqual(image.get_at((0, 0)).a, 0)
            self.assertEqual(len(record['frames']), 4)
            self.assertAlmostEqual(sum(f['duration'] for f in record['frames']), .20)
            self.assertGreater(record['body_height'], 0)
            for frame in record['frames']:
                rect = pygame.Rect(frame['rect'])
                self.assertTrue(image.get_rect().contains(rect))
                self.assertGreater(frame['duration'], 0)
                self.assertTrue(0 <= frame['anchor'][0] <= rect.width)
                self.assertTrue(0 <= frame['anchor'][1] <= rect.height)
                self.assertTrue(all(0 <= x < rect.width and 0 <= y < rect.height
                                    for x, y in frame['isolation_polygon']))


class AttackPresentationTests(unittest.TestCase):
    def setUp(self):
        self.game = LastValveGame(audio_enabled=False)
        self.scene = self.game.scenes['play']
        self.use_state(combat())

    def tearDown(self):
        pygame.quit()

    def use_state(self, state):
        self.game.state = state
        self.game.change_scene('play')
        self.scene.reset()

    def draw_actor(self, uid='vera'):
        self.game.draw_game_elements()
        return self.scene.renderer.actors[uid]

    def test_valid_attack_changes_image_once_and_returns_to_idle_without_callbacks(self):
        idle = self.draw_actor().image
        self.assertTrue(self.scene.command('attack'))
        actor = self.draw_actor()
        self.assertIsNot(actor.image, idle, 'El ataque sigue mostrando la pose estática')
        first = actor.image
        self.game.update_game_logic(.07)
        self.assertIsNot(self.draw_actor().image, first)
        self.game.update_game_logic(.13)
        self.assertIs(self.draw_actor().image, idle)
        self.assertEqual((self.game.state.player.ap, self.game.state.enemies['enemy'].hp), (4, 36))
        self.game.update_game_logic(5)
        self.assertIs(self.draw_actor().image, idle)
        self.assertEqual((self.game.state.player.ap, self.game.state.enemies['enemy'].hp), (4, 36))

    def test_repeated_ui_attack_is_rejected_during_clip_but_new_order_after_idle_works(self):
        state = self.game.state
        self.assertTrue(self.scene.command('attack'))
        action = state.last_attacks['vera']
        self.assertFalse(self.scene.command('attack'), 'La UI permite repetir ataque durante one-shot')
        self.assertIs(state.last_attacks['vera'], action)
        self.assertEqual((state.player.ap, state.enemies['enemy'].hp), (4, 36))
        self.game.update_game_logic(.20)
        self.assertTrue(self.scene.command('attack', True))
        self.assertEqual((state.player.ap, state.enemies['enemy'].hp), (1, 29))

    def test_menu_cancels_visuals_even_while_attack_is_active(self):
        self.scene.command('attack')
        self.game.handle_specific_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                           pos=(1130, 755), button=1))
        self.assertIs(self.game.current_scene, self.game.scenes['menu'])
        self.assertFalse(self.game.state.last_attacks, 'Una salida de escena conserva ataques pendientes')

    def test_player_attack_starts_at_continuous_command_time_not_previous_tick(self):
        self.game.update_game_logic(.019)
        self.scene.command('attack')
        self.assertAlmostEqual(self.game.state.last_attacks['vera'].occurred_at,
                               self.game.state.elapsed)

    def test_both_vera_attacks_use_supplied_clip_but_preserve_distinct_cost_and_damage(self):
        for power, cost, damage in ((False, 2, 4), (True, 3, 7)):
            self.use_state(combat())
            self.assertTrue(self.scene.command('attack', power))
            actor = self.draw_actor()
            clip = self.scene.renderer.attack_clips['legacy', 'vera']
            self.assertIs(actor.image, clip.right[0][0])
            self.assertEqual((self.game.state.player.ap, self.game.state.enemies['enemy'].hp),
                             (6-cost, 40-damage))

    def test_enemy_and_boss_use_their_clip_without_altering_existing_cadence(self):
        for boss in (False, True):
            with self.subTest(boss=boss):
                self.use_state(combat(boss=boss))
                state = self.game.state
                self.assertTrue(state.end_turn())
                self.game.update_game_logic(.22)
                action = state.last_attacks['enemy']
                actor = self.draw_actor('enemy')
                clip = self.scene.renderer.attack_clips['legacy', 'boss' if boss else 'guard']
                self.assertIs(actor.image, clip.left[0][0])
                self.assertEqual((state.player.hp, state.enemies['enemy'].ap), (27, 4))
                self.game.update_game_logic(.20)
                self.assertIs(self.draw_actor('enemy').image, actor.directions['front'])
                self.assertEqual(state.player.hp, 27)
                self.game.update_game_logic(.02)
                self.assertIsNot(state.last_attacks['enemy'], action)
                self.assertEqual((state.player.hp, state.enemies['enemy'].ap), (24, 2))
                self.assertIs(self.draw_actor('enemy').image, clip.left[0][0])

    def test_facing_and_mirrored_anchor_follow_projection_not_grid_indices(self):
        state = self.game.state
        for left in (False, True):
            state.player.cell = (4, 3) if left else (2, 3)
            state.last_attacks.clear()
            state.player.ap = 6
            self.assertTrue(self.scene.command('attack'))
            actor = self.draw_actor()
            clip = self.scene.renderer.attack_clips['legacy', 'vera']
            image, anchor = (clip.left if left else clip.right)[0]
            self.assertIs(actor.image, image)
            self.assertEqual(actor.foot, self.scene.renderer.projection.center(state.player.cell))
            self.assertEqual(actor.rect.topleft,
                             (round(actor.foot[0]-anchor[0]), round(actor.foot[1]-anchor[1])))
            if left:
                original, original_anchor = clip.right[0]
                self.assertEqual(anchor, (image.get_width()-original_anchor[0], original_anchor[1]))
                self.assertEqual(pygame.image.tobytes(image, 'RGBA'),
                                 pygame.image.tobytes(pygame.transform.flip(original, True, False), 'RGBA'))

    def test_chunked_and_large_dt_sample_same_attack_frame_and_logical_results(self):
        def run(chunks):
            self.use_state(combat())
            state = self.game.state
            state.end_turn()
            for dt in chunks:
                self.game.update_game_logic(dt)
            actor = self.draw_actor('enemy')
            return ((state.player.hp, state.enemies['enemy'].ap, state.turn,
                     state.last_attacks['enemy']), pygame.image.tobytes(actor.image, 'RGBA'))
        self.assertEqual(run([.50]), run([.02]*25))
        self.assertEqual(run([1.50]), run([.02]*75))

    def test_dt_zero_holds_frame_and_negative_dt_is_rejected(self):
        self.scene.command('attack')
        first = self.draw_actor().image
        self.game.update_game_logic(0)
        self.assertIs(self.draw_actor().image, first)
        with self.assertRaises(ValueError):
            self.game.update_game_logic(-.01)

    def test_no_resource_io_scaling_reflection_or_masks_during_playback(self):
        self.scene.command('attack')
        self.draw_actor()
        with (patch('pygame.image.load') as load,
              patch('pygame.transform.smoothscale') as scale,
              patch('pygame.transform.flip') as flip,
              patch('game.render.isolate_attack_frames') as isolate):
            for _ in range(8):
                self.game.update_game_logic(.04)
                self.draw_actor()
        load.assert_not_called()
        scale.assert_not_called()
        flip.assert_not_called()
        isolate.assert_not_called()

    def test_tactical_input_is_blocked_not_menu_or_global_quit(self):
        state = self.game.state
        self.scene.command('attack')
        for name, args in (('move_direction', ((0, -1),)), ('set_destination', ((2, 2),)),
                           ('heal', ()), ('end_turn', ())):
            self.assertFalse(self.scene.command(name, *args))
        self.assertFalse(state.motions or state.route)
        self.assertEqual((state.player.ap, state.enemies['enemy'].hp), (4, 36))
        self.game.running = True
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        self.game._handle_events()
        self.assertFalse(self.game.running)
        self.assertFalse(state.last_attacks, 'QUIT conserva señales de ataque')

    def test_reset_context_terminal_and_new_game_cancel_without_late_damage(self):
        for transition in ('reset', 'context', 'victory', 'defeat', 'new'):
            with self.subTest(transition=transition):
                self.use_state(combat())
                old = self.game.state
                self.scene.command('attack')
                if transition == 'reset':
                    self.scene.reset()
                elif transition == 'context':
                    old.context_revision += 1
                    self.game.draw_game_elements()
                elif transition == 'new':
                    self.game.start_new_game()
                else:
                    old.mode = transition
                    self.game.update_game_logic(.02)
                if transition != 'new':
                    self.assertFalse(old.last_attacks)
                else:
                    self.assertFalse(self.game.state.last_attacks)
                    self.assertIsNot(self.game.state, old)
                self.game.update_game_logic(1)
                self.assertEqual((old.player.ap, old.enemies['enemy'].hp), (4, 36))

    def test_lethal_hit_cancels_clip_immediately_instead_of_deferring_combat_close(self):
        state = self.game.state
        state.enemies['enemy'].hp = 4
        self.assertTrue(self.scene.command('attack'))
        actor = self.draw_actor()
        self.assertEqual(state.mode, 'exploration')
        self.assertFalse(state.last_attacks)
        self.assertIs(actor.image, actor.directions['front'])
        self.assertFalse(self.scene.renderer.attack_active(state))


class AttackContractTests(unittest.TestCase):
    def test_invalid_attacks_do_not_create_or_replace_signals(self):
        for invalid in ('range', 'ap', 'turn', 'moving', 'dead', 'dialogue'):
            with self.subTest(invalid=invalid):
                state = combat()
                if invalid == 'range':
                    state.player.cell = (1, 1)
                elif invalid == 'ap':
                    state.player.ap = 1
                elif invalid == 'turn':
                    state.turn = 'enemy'
                elif invalid == 'moving':
                    state.move_direction((0, -1))
                elif invalid == 'dead':
                    state.enemies['enemy'].hp = 0
                else:
                    state.active_dialogue = object()
                before = (state.player.ap, state.enemies['enemy'].hp)
                self.assertFalse(state.attack())
                self.assertEqual(state.last_attacks, {})
                self.assertEqual((state.player.ap, state.enemies['enemy'].hp), before)
        state = combat()
        state.attack()
        action = state.last_attacks['vera']
        state.player.ap = 1
        self.assertFalse(state.attack())
        self.assertIs(state.last_attacks['vera'], action)

    def test_travel_cancels_signals_and_does_not_change_costs_or_damage(self):
        from game.model import AttackAction
        state = GameState.new()
        state.player.cell = (4, 10)
        state.last_attacks['vera'] = AttackAction('vera', (5, 10), state.elapsed)
        before = (state.player.ap, state.player.hp)
        self.assertTrue(state.travel('to_puesto'))
        self.assertFalse(state.last_attacks)
        state.update(.1)
        self.assertEqual((state.player.ap, state.player.hp), before)

    def test_last_ap_turn_switch_does_not_wait_for_animation_completion(self):
        state = combat()
        state.player.ap = 2
        state.attack()
        self.assertEqual((state.turn, state.player.ap, state.enemies['enemy'].hp), ('enemy', 0, 36))
        state.update(.22)
        self.assertEqual((state.player.hp, state.enemies['enemy'].ap), (27, 4))
        self.assertEqual(set(state.last_attacks), {'vera', 'enemy'})

    def test_clip_boundaries_are_one_shot_and_never_wrap_on_large_dt(self):
        from game.animation import AttackClip
        clip = AttackClip((.06, .05, .04, .05), tuple(range(4)), tuple(range(4, 8)))
        for elapsed, expected in ((0, 0), (.059, 0), (.06, 1), (.11, 2), (.15, 3),
                                  (.199, 3), (.20, None), (100, None), (-.01, None)):
            self.assertEqual(clip.frame_index(elapsed), expected)
        self.assertEqual(clip.sample(.11, mirrored=True), 6)

    def test_source_masks_remove_neighbor_boots_but_preserve_interior_rgba_and_black(self):
        from game.animation import isolate_attack_frames
        manifest = json.loads((ROOT / 'assets/manifest.json').read_text())
        for role in ('vera', 'guard', 'boss'):
            record = manifest['images'][role+'_attack']
            sheet = pygame.image.load(ROOT / record['path'])
            frames = isolate_attack_frames(sheet, record)
            for frame, meta in zip(frames, record['frames']):
                self.assertGreater(pygame.mask.from_surface(frame).count(), 50000)
                # Las cuatro esquinas de las cajas no contienen relleno opaco.
                self.assertEqual(frame.get_at((0, 0)).a, 0)
                x, y, w, h = meta['rect']
                # Un píxel interior corporal conserva TODOS sus canales, incluso negros.
                px, py = meta['anchor'][0], round(h*.6)
                self.assertEqual(frame.get_at((px, py)), sheet.get_at((x+px, y+py)))
                self.assertTrue(any(frame.get_at((px, py)).a > 0 and
                                    max(frame.get_at((px, py))[:3]) < 35
                                    for px in range(0, w, 5) for py in range(0, h, 5)))
        record = manifest['images']['vera_attack']
        frames = isolate_attack_frames(pygame.image.load(ROOT / record['path']), record)
        # La bota izquierda de la tercera pose caería dentro del rect de la segunda.
        x, y, _, _ = record['frames'][1]['rect']
        self.assertEqual(frames[1].get_at((1090-x, 660-y)).a, 0)
        x, y, _, _ = record['frames'][2]['rect']
        self.assertGreater(frames[2].get_at((1090-x, 660-y)).a, 0)

    def test_invalid_metadata_is_rejected_instead_of_silent_fallback(self):
        from copy import deepcopy
        from game.animation import isolate_attack_frames
        manifest = json.loads((ROOT / 'assets/manifest.json').read_text())
        record = manifest['images']['vera_attack']
        sheet = pygame.image.load(ROOT / record['path'])
        for kind in ('rect', 'duration', 'anchor', 'polygon'):
            bad = deepcopy(record)
            if kind == 'rect':
                bad['frames'][0]['rect'][0] = -1
            elif kind == 'duration':
                bad['frames'][0]['duration'] = 0
            elif kind == 'anchor':
                bad['frames'][0]['anchor'][0] = -1
            else:
                bad['frames'][0]['isolation_polygon'] = [[-1, 0], [10, 10], [0, 10]]
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                isolate_attack_frames(sheet, bad)


class AttackWorldContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = LastValveGame(audio_enabled=False)
        cls.scene = cls.game.scenes['play']

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_authored_maps_use_projection_facing_and_same_body_scale_as_static(self):
        for map_id in ('puesto', 'planta'):
            self.game.start_new_game(map_id)
            state = self.game.state
            state.patrols = {}
            enemies = [next(u for u in state.enemies.values() if not u.boss)]
            if map_id == 'planta':
                enemies.append(next(u for u in state.enemies.values() if u.boss))
            for enemy in enemies:
                for neighbor in state.grid.neighbors(enemy.cell):
                    with self.subTest(map_id=map_id, enemy=enemy.id, neighbor=neighbor):
                        state.last_attacks.clear()
                        state.player.cell = neighbor
                        state.mode, state.turn, state.active_enemy_id = 'combat', 'player', enemy.id
                        state.player.ap = 6
                        enemy.hp = enemy.max_hp
                        self.assertTrue(self.scene.command('attack'))
                        self.game.draw_game_elements()
                        actor = self.scene.renderer.actors['vera']
                        clip = self.scene.renderer.attack_clips[map_id, 'vera']
                        left = self.scene.renderer.projection.center(enemy.cell)[0] < actor.foot[0]
                        image, anchor = (clip.left if left else clip.right)[0]
                        self.assertIs(actor.image, image)
                        self.assertEqual(actor.rect.topleft,
                                         (round(actor.foot[0]-anchor[0]), round(actor.foot[1]-anchor[1])))
                        role = 'boss' if enemy.boss else 'guard'
                        actor = self.scene.renderer.actors[enemy.id]
                        record = self.game.manifest['images'][role+'_attack']
                        clip = self.scene.renderer.attack_clips[map_id, role]
                        # Una escala corporal fija por clip, idéntica al cuerpo estático del mapa.
                        factor = actor.directions['front'].get_height() / record['body_height']
                        for frame, meta in zip(clip.right, record['frames']):
                            self.assertEqual(frame[0].get_size(),
                                             tuple(max(1, round(v*factor)) for v in meta['rect'][2:]))

    def test_missing_rear_cycle_uses_existing_rear_static_not_mirrored_front_attack(self):
        from game.model import Motion
        self.game.state = combat()
        self.game.change_scene('play')
        self.scene.reset()
        state = self.game.state
        self.scene.command('attack')
        self.game.update_game_logic(.20)
        state.motions['vera'] = Motion(state.player.cell, (1, 3), elapsed=.07)
        self.game.draw_game_elements()
        actor = self.scene.renderer.actors['vera']
        self.assertEqual(actor.facing, 'rear')
        self.assertIs(actor.image, actor.directions['rear'])

    def test_subtick_roundoff_at_attack_start_does_not_hide_first_frame(self):
        clip = self.scene.renderer.attack_clips['legacy', 'vera']
        self.assertEqual(clip.frame_index(-1e-16), 0)
