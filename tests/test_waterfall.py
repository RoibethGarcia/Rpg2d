"""Cascada ambiental del pueblo: reloj, recortes, caché y composición SDL dummy."""
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

import pygame
from game.app import LastValveGame
from game.render import WORLD_RECT

ROOT = Path(__file__).resolve().parents[1]


class WaterfallTests(unittest.TestCase):
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

    def effect(self):
        self.assertTrue(hasattr(self.art, 'waterfall'), 'Falta la cascada ambiental del pueblo')
        self.assertIsNotNone(self.art.waterfall)
        return self.art.waterfall

    def render(self):
        self.renderer.draw(self.game.screen, self.game.state, None)
        return self.game.screen.copy()

    def test_water_changes_while_village_and_gameplay_stay_fixed(self):
        before_state = (self.game.state.player.cell, self.game.state.player.hp,
                        self.game.state.player.ap, self.game.state.turn, self.game.state.medkits)
        before = self.render()
        self.scene.update(.11)
        after = self.render()
        # Rectángulo de autoría que rodea SOLO la caída de agua al sudeste.
        x, y = self.art.projection.screen((1168, 833))
        area = pygame.Rect(round(x), round(y), 28, 52)
        self.assertNotEqual(pygame.image.tobytes(before.subsurface(area), 'RGB'),
                            pygame.image.tobytes(after.subsurface(area), 'RGB'),
                            'El agua sigue estática al avanzar el reloj')
        self.assertEqual(before_state, (self.game.state.player.cell, self.game.state.player.hp,
                         self.game.state.player.ap, self.game.state.turn, self.game.state.medkits))
        # El resto del mundo no cambia por activar esta animación.
        before.fill('black', area)
        after.fill('black', area)
        self.assertEqual(pygame.image.tobytes(before, 'RGB'), pygame.image.tobytes(after, 'RGB'))

    def test_original_sheet_and_pending_provenance_are_registered(self):
        self.assertIn('waterfall', self.game.manifest['images'], 'Falta registrar el recurso local')
        record = self.game.manifest['images']['waterfall']
        self.assertEqual(record['size'], [1774, 887])
        self.assertEqual(record['grid'], [4, 2])
        self.assertEqual(record['source_type'], 'user_supplied')
        self.assertEqual(record['redistribution_status'], 'pending_confirmation')
        self.assertNotIn('license', record)
        path = ROOT / record['path']
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record['sha256'])
        self.assertTrue((ROOT / record['provenance_file']).is_file())
        image = self.game.assets.get_image('waterfall')
        self.assertEqual(image.get_at((0, 0)).a, 0)

    def test_odd_sheet_uses_integer_boundaries_and_one_fixed_crop(self):
        effect = self.effect()
        self.assertEqual(len(effect.frames), 8)
        self.assertEqual(len({image.get_size() for image in effect.frames}), 1)
        record = self.game.manifest['images']['waterfall']
        crop = pygame.Rect(record['crop'])
        for i, rect in enumerate(effect.source_rects):
            row, col = divmod(i, 4)
            self.assertEqual(rect, pygame.Rect(col * 1774 // 4 + crop.x,
                                              row * 887 // 2 + crop.y, crop.w, crop.h))
            self.assertTrue(self.game.assets.get_image('waterfall').get_rect().contains(rect))
        # No auto-trimming de la silueta en cada pose: mantiene el mismo anclaje.
        self.assertEqual(effect.position, tuple(round(v) for v in self.art.projection.screen((1168, 833))))
        self.assertGreater(len({pygame.image.tobytes(f, 'RGBA') for f in effect.frames}), 1)

    def test_seconds_loop_at_ten_fps_and_sampling_does_not_advance_clock(self):
        effect = self.effect()
        for time, expected in ((0, 0), (.099, 0), (.1, 1), (.7, 7), (.8, 0), (.91, 1), (80.31, 3)):
            self.assertEqual(effect.frame_index(time), expected)
            self.assertEqual(effect.frame_index(time), expected)
        for time in (float('nan'), float('inf'), -1):
            with self.assertRaises(ValueError):
                effect.frame_index(time)

    def test_clock_is_frame_rate_independent_and_resets_with_new_game(self):
        effect = self.effect()
        self.scene.update(.31)
        index = effect.frame_index(self.game.state.elapsed)
        self.game.start_new_game()
        for _ in range(31):
            self.scene.update(.01)
        self.assertEqual(effect.frame_index(self.game.state.elapsed), index)
        self.assertEqual(index, 3)
        self.game.state.active_dialogue = {'id': 'fixture'}
        time = self.game.state.elapsed
        self.scene.update(.4)
        self.assertEqual(self.game.state.elapsed, time)
        self.game.start_new_game()
        self.assertEqual(effect.frame_index(self.game.state.elapsed), 0)

    def test_other_maps_have_no_waterfall_and_remain_static(self):
        self.effect()
        for map_id in ('puesto', 'planta'):
            self.game.start_new_game(map_id)
            art = self.renderer.layered_maps[map_id]
            self.assertIsNone(art.waterfall)
            # Comparar render sin simular patrullas: solo reloj visual.
            before = self.render()
            self.game.state._simulation_time += .11
            after = self.render()
            self.assertEqual(pygame.image.tobytes(before, 'RGB'), pygame.image.tobytes(after, 'RGB'))

    def test_mask_preserves_pipe_and_rocks_and_draw_respects_external_clip(self):
        effect = self.effect()
        surface = pygame.Surface(self.game.screen.get_size())
        surface.fill('magenta')
        effect.blit(surface, .1)
        x, y = self.art.projection.screen((1180, 815))  # Boca de caño: NO se anima.
        self.assertEqual(surface.get_at((round(x), round(y)))[:3], (255, 0, 255))
        polygon = self.art.layout.data['waterfall']['polygon']
        from game.hondonada import point_in_polygon
        changed = 0
        for px in range(effect.frames[0].get_width()):
            for py in range(effect.frames[0].get_height()):
                point = (effect.position[0] + px, effect.position[1] + py)
                if surface.get_at(point)[:3] != (255, 0, 255):
                    changed += 1
                    # Redondeo de máscara a pantalla: admitir hasta 2px de autoría.
                    source = self.art.projection.source(point)
                    self.assertTrue(any(point_in_polygon((source[0]+dx, source[1]+dy), polygon)
                                        for dx in (-2, 0, 2) for dy in (-2, 0, 2)))
        self.assertGreater(changed, 0)
        surface.fill('magenta')
        clip = pygame.Rect(400, 300, 20, 20)
        surface.set_clip(clip)
        effect.blit(surface, .2)
        self.assertEqual(surface.get_clip(), clip)
        self.assertEqual(surface.get_at(effect.position)[:3], (255, 0, 255))

    def test_animation_is_cached_and_composed_before_camera_zoom(self):
        effect = self.effect()
        self.renderer.draw(self.game.screen, self.game.state, None)  # Preparar actor.
        self.renderer.camera.level = 2
        with (patch.object(effect, 'blit', wraps=effect.blit) as draw,
              patch('pygame.image.load') as load,
              patch('pygame.transform.smoothscale', wraps=pygame.transform.smoothscale) as scale):
            self.scene.update(.12)
            self.renderer.draw(self.game.screen, self.game.state, None)
        load.assert_not_called()
        self.assertEqual(scale.call_count, 1)  # Solo escala la composición de zoom.
        draw.assert_called_once_with(self.renderer._world_surface, self.game.state.elapsed)
        self.assertIs(scale.call_args.args[2], self.renderer._zoom_surface)


if __name__ == '__main__':
    unittest.main()
