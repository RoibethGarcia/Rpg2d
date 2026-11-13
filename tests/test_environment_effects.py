"""Efectos visuales del escenario 1, sin builds ni mutaciones del dominio."""
from copy import deepcopy
from dataclasses import replace
from math import hypot
import unittest
from unittest.mock import patch

import pygame

from game.app import LastValveGame
from game.render import WORLD_RECT


class EnvironmentalEffectsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = LastValveGame(audio_enabled=False)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.game.start_new_game()
        self.scene = self.game.scenes['play']
        self.renderer = self.scene.renderer
        self.art = self.renderer.hondonada
        if getattr(self.art, 'effects', None) is not None:
            fx = self.art.effects
            fx.config = type(fx.config)(**self.art.layout.data['ambient']['settings'])
            fx.reset()

    def effects(self):
        self.assertTrue(hasattr(self.art, 'effects'),
                        'Falta integrar aves, humo y río en La Hondonada')
        self.assertIsNotNone(self.art.effects)
        return self.art.effects

    def test_every_scenario_has_effects_and_defaults_are_subtle(self):
        fx = self.effects()
        self.assertTrue(fx.config.enabled)
        self.assertLessEqual(fx.config.max_birds, 5)
        self.assertGreaterEqual(fx.config.max_birds, 2)
        self.assertLessEqual(fx.config.max_particles, 64)
        self.assertGreater(len(fx.river), 0)
        # Puesto y Planta animan solo agua y aves: sin humo ni vapor propios.
        for map_id in ('puesto', 'planta'):
            other = self.renderer.layered_maps[map_id].effects
            self.assertIsNotNone(other)
            self.assertTrue(other.config.enabled)
            self.assertLessEqual(other.config.max_birds, 5)
            self.assertEqual(other.emitters, ())

    def test_dt_partition_has_same_poses_and_draw_does_not_advance_time(self):
        fx = self.effects()
        fx.update(3.6)
        expected = (fx.bird_poses, fx.smoke_poses)
        fx.reset()
        for _ in range(216):
            fx.update(1 / 60)
        self.assertAlmostEqual(fx.time, 3.6)
        self.assertEqual((fx.bird_poses, fx.smoke_poses), expected)
        for _ in range(3):
            self.renderer.draw(self.game.screen, self.game.state, None)
        self.assertAlmostEqual(fx.time, 3.6)
        for dt in (-1, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                fx.update(dt)

    def test_birds_flap_follow_smooth_outer_lanes_and_have_finite_capacity(self):
        fx = self.effects()
        self.assertGreater(len(fx.bird_poses), 0)
        variants = fx.bird_frames
        self.assertGreater(len({pygame.image.tobytes(f, 'RGBA') for f in variants[0]}), 2)
        previous = fx.bird_poses
        fx.update(.01)
        for before, after in zip(previous, fx.bird_poses):
            self.assertLess(hypot(after[0] - before[0], after[1] - before[1]), 2)
        seen = set()
        for _ in range(1000):
            fx.update(.2)
            self.assertLessEqual(len(fx.bird_poses), fx.config.max_birds)
            for x, y, variant, frame in fx.bird_poses:
                u = (x - WORLD_RECT.x) / WORLD_RECT.w
                self.assertTrue(u < .25 or u > .75, (x, y))
                self.assertTrue(WORLD_RECT.top - 20 <= y <= WORLD_RECT.bottom)
                seen.add((variant, frame))
        self.assertGreater(len(seen), 4)

    def test_smoke_is_translucent_expands_fades_and_stays_near_real_outlets(self):
        fx = self.effects()
        frames = fx.smoke_frames
        self.assertGreater(frames[-1].get_width(), frames[0].get_width())
        self.assertEqual(frames[-1].get_bounding_rect().size, (0, 0))
        self.assertGreater(len(fx.smoke_poses), 0)
        for image in frames:
            self.assertTrue(image.get_masks()[3])
            self.assertEqual(image.get_at((0, 0)).a, 0)
            self.assertLess(max(image.get_at((x, y)).a for x in range(image.get_width())
                                for y in range(image.get_height())), 150)
        for _ in range(1000):
            fx.update(.19)
            self.assertLessEqual(len(fx.smoke_poses), fx.config.max_particles)
            for x, y, stage in fx.smoke_poses:
                self.assertTrue(any(abs(x - self.art.projection.screen(e['point'])[0]) < 35
                                    and -60 < y - self.art.projection.screen(e['point'])[1] <= 1
                                    for e in fx.emitters))
                self.assertTrue(0 <= stage < len(frames))

    def test_disable_and_zero_intensities_are_effective_and_bounded_config_validated(self):
        fx = self.effects()
        fx.config = replace(fx.config, enabled=False)
        before = fx.time
        fx.update(5)
        self.assertEqual(fx.time, before)
        self.assertEqual((fx.bird_poses, fx.smoke_poses), ((), ()))
        surface = pygame.Surface(self.game.screen.get_size(), pygame.SRCALPHA)
        fx.draw_background(surface)
        fx.draw_smoke(surface)
        self.art.blit_ambient(surface, .5)
        self.assertEqual(surface.get_bounding_rect().size, (0, 0))
        fx.config = replace(fx.config, enabled=True, max_birds=0, particle_intensity=0)
        fx.update(.2)
        self.assertEqual((fx.bird_poses, fx.smoke_poses), ((), ()))
        for field, value in (('max_birds', 6), ('max_birds', -1),
                             ('max_birds', 2.5), ('max_particles', 10000),
                             ('water_speed', -1), ('water_speed', float('nan')),
                             ('particle_intensity', 2), ('smoke_frequency', -1)):
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                replace(fx.config, **{field: value})

    def test_frequency_changes_smoke_and_water_speed_controls_existing_sheet(self):
        fx = self.effects()
        fx.config = replace(fx.config, smoke_frequency=0)
        fx.update(1)
        self.assertEqual(fx.smoke_poses, ())
        fx.config = replace(fx.config, water_speed=2)
        with patch.object(self.art.waterfall, 'blit') as draw:
            self.art.blit_ambient(self.game.screen, .3)
        draw.assert_called_once_with(self.game.screen, .6)

    def test_steam_bursts_have_quiet_gaps_and_irregular_intervals(self):
        fx = self.effects()
        fx.config = replace(fx.config, max_particles=64, particle_intensity=1)
        emitter = next(e for e in fx.emitters if e['kind'] == 'steam')
        origin = self.art.projection.screen(emitter['point'])
        starts, was_active = [], False
        for _ in range(900):
            active = any(abs(x - origin[0]) < 35 for x, y, stage in fx.smoke_poses)
            if active and not was_active:
                starts.append(fx.time)
            was_active = active
            fx.update(.1)
        self.assertGreater(len(starts), 4)
        intervals = [b-a for a,b in zip(starts, starts[1:])]
        self.assertGreater(max(intervals) - min(intervals), 1)
        self.assertGreater(min(intervals), 5)

    def test_high_frequency_does_not_recycle_smoke_before_it_fades(self):
        fx = self.effects()
        fx.config = replace(fx.config, max_particles=1, particle_intensity=1,
                            smoke_frequency=3, max_birds=0)
        fx.reset()
        previous = None
        for _ in range(1200):
            stage = fx.smoke_poses[0][2] if fx.smoke_poses else None
            if previous is not None and (stage is None or stage < previous):
                self.assertGreaterEqual(previous, 22, 'La partícula desaparece antes del fade-out')
            previous = stage
            fx.update(.01)

    def test_scene_updates_only_active_map_and_pauses_dialogue_and_menu(self):
        fx = self.effects()
        self.scene.update(.2)
        self.assertAlmostEqual(fx.time, .2)
        self.game.state.active_dialogue = {'id': 'fixture'}
        self.scene.update(.4)
        self.assertAlmostEqual(fx.time, .2)
        self.game.state.active_dialogue = None
        self.game.change_scene('menu')
        initial = (fx.time, fx.bird_poses, fx.smoke_poses)
        self.game.update_game_logic(1)
        self.assertEqual((fx.time, fx.bird_poses, fx.smoke_poses), initial)
        self.game.start_new_game('puesto')
        with patch.object(fx, 'update') as update:
            self.scene.update(.5)
        update.assert_not_called()

    def test_round_trip_and_new_game_reset_effects_without_residual_particles(self):
        fx = self.effects()
        initial = (fx.bird_poses, fx.smoke_poses)
        self.scene.update(2)
        state = self.game.state
        state.player.cell = (4, 10)
        self.assertTrue(state.travel('to_puesto'))
        self.scene.handle_events([])
        self.assertEqual(fx.time, 0)
        state.player.cell = (1, 10)
        self.assertTrue(state.travel('to_hondonada'))
        self.scene.handle_events([])
        self.assertEqual((fx.bird_poses, fx.smoke_poses), initial)
        self.scene.update(3)
        self.game.start_new_game()
        self.assertEqual(fx.time, 0)
        self.assertEqual((fx.bird_poses, fx.smoke_poses), initial)

    def test_cached_alpha_frames_and_draw_order_without_io_or_preparation_per_frame(self):
        fx = self.effects()
        self.scene.draw(self.game.screen)  # Calentar actores, no efectos.
        frame_ids = tuple(id(f) for frames in fx.bird_frames for f in frames)
        order = []
        def wrap(name, original):
            def call(*args, **kwargs):
                order.append(name)
                return original(*args, **kwargs)
            return call
        with (patch.object(fx, 'draw_background', side_effect=wrap('background', fx.draw_background)),
              patch.object(fx, 'draw_smoke', side_effect=wrap('smoke', fx.draw_smoke)),
              patch.object(self.art, 'blit_base', side_effect=wrap('base', self.art.blit_base)),
              patch.object(self.renderer.actors['vera'], 'draw', side_effect=wrap('vera', self.renderer.actors['vera'].draw)),
              patch('pygame.image.load', side_effect=AssertionError('IO por frame')),
              patch('pygame.transform.smoothscale', side_effect=AssertionError('Escala por frame'))):
            self.scene.update(.16)
            self.scene.draw(self.game.screen)
        self.assertLess(order.index('background'), order.index('vera'))
        self.assertLess(order.index('base'), order.index('smoke'))
        self.assertLess(order.index('smoke'), order.index('vera'))
        self.assertEqual(frame_ids, tuple(id(f) for frames in fx.bird_frames for f in frames))

    def test_background_effects_are_fixed_while_smoke_receives_world_zoom(self):
        fx = self.effects()
        with (patch.object(fx, 'draw_background') as background,
              patch.object(fx, 'draw_smoke') as smoke):
            for level in range(3):
                self.renderer.camera.level = level
                self.renderer.draw(self.game.screen, self.game.state, None)
        self.assertEqual(background.call_count, 3)
        self.assertTrue(all(c.args[0] is self.game.screen for c in background.call_args_list))
        self.assertTrue(all(c.args[0] is self.renderer._world_surface for c in smoke.call_args_list))

    def test_river_mask_excludes_banks_frames_loop_and_all_draws_respect_clip(self):
        fx = self.effects()
        for water in fx.river:
            self.assertGreater(len({pygame.image.tobytes(f, 'RGBA') for f in water.frames}), 1)
            self.assertEqual(water.frame_index(0), water.frame_index(len(water.frames) * water.frame_seconds))
            for frame in water.frames:
                self.assertEqual(frame.get_at((0, 0)).a, 0)
        surface = pygame.Surface(self.game.screen.get_size(), pygame.SRCALPHA)
        surface.set_clip((0, 0, 3, 3))  # Ningún efecto pertenece a la UI.
        fx.draw_background(surface)
        fx.draw_smoke(surface)
        self.assertEqual(surface.get_clip(), pygame.Rect(0, 0, 3, 3))
        self.assertEqual(surface.get_bounding_rect().size, (0, 0))

    def test_emitters_do_not_invent_roof_chimneys_and_river_excludes_upper_bank(self):
        fx = self.effects()
        # Inspección de la placa: el pórtico en (505,46) NO es un conducto.
        self.assertEqual({e['id'] for e in fx.emitters}, {'estufa_oeste', 'union_deposito'})
        from game.hondonada import point_in_polygon
        # Orilla pintada, comprobada en el paisaje original a tamaño nativo.
        for placement in self.art.layout.data['ambient']['river']:
            self.assertFalse(point_in_polygon((850, 852), placement['polygon']))

    def test_river_visibly_animates_only_its_mask_after_world_occlusion(self):
        fx = self.effects()
        fx.config = replace(fx.config, max_birds=0, particle_intensity=0)
        fx.update(0)
        self.renderer.draw(self.game.screen, self.game.state, None)
        before = self.game.screen.copy()
        fx.update(.5)
        self.renderer.draw(self.game.screen, self.game.state, None)
        changed = [(x, y) for x in range(WORLD_RECT.left, WORLD_RECT.right)
                   for y in range(WORLD_RECT.top, WORLD_RECT.bottom)
                   if before.get_at((x,y)) != self.game.screen.get_at((x,y))]
        self.assertGreater(len(changed), 5)
        for x, y in changed:
            self.assertTrue(any(pygame.Rect(w.position, w.frames[0].get_size()).collidepoint(x, y)
                                for w in fx.river))

    def test_optional_png_sheet_uses_cached_frames_and_preserves_source(self):
        self.effects()
        from game.ambient import EnvironmentalEffects
        sheet = pygame.Surface((40, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(sheet, (240,230,215,200), (1,1,18,8))
        pygame.draw.ellipse(sheet, (240,230,215,200), (25,2,12,5))
        before = pygame.image.tobytes(sheet, 'RGBA')
        data = deepcopy(self.art.layout.data['ambient'])
        data['river'] = []
        fx = EnvironmentalEffects(data, self.art.projection, None, WORLD_RECT,
                                 sheet, {'grid': [2,1], 'frame_seconds': .2})
        self.assertEqual(fx.bird_count, 2)
        self.assertEqual(len(fx.bird_frames[0]), 16)  # 2 poses × 8 opacidades.
        self.assertEqual(pygame.image.tobytes(sheet, 'RGBA'), before)
        self.assertNotEqual(pygame.image.tobytes(fx.bird_frames[0][-2], 'RGBA'),
                            pygame.image.tobytes(fx.bird_frames[0][-1], 'RGBA'))

    def test_effects_never_mutate_gameplay_or_source_bitmaps(self):
        fx = self.effects()
        state_before = deepcopy(self.game.state.__dict__)
        sources = [self.game.assets.get_image(n) for n in ('hondonada_plate', 'hondonada_background', 'waterfall')]
        pixels = [pygame.image.tobytes(s, 'RGBA') for s in sources]
        for _ in range(10):
            fx.update(.21)
            self.renderer.draw(self.game.screen, self.game.state, None)
        self.assertEqual(self.game.state.__dict__, state_before)
        self.assertEqual(pixels, [pygame.image.tobytes(s, 'RGBA') for s in sources])


if __name__ == '__main__':
    unittest.main()
