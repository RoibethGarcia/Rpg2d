"""Zoom de presentación: selección inversa, cámara y controles SDL dummy."""
import unittest
from unittest.mock import patch

import pygame

from game.app import LastValveGame
from game.model import Motion
from game.render import WORLD_RECT
from game.camera import ZoomCamera


class CameraTests(unittest.TestCase):
    def test_roundtrip_negative_points_and_integer_crop_at_every_level(self):
        camera = ZoomCamera((24, 96, 968, 528))
        for level in range(3):
            camera.level = level
            camera.follow((573.25, 304.75))
            for point in ((-18.75, -2.25), (24, 96), (573.25, 304.75), (992, 624)):
                actual = camera.source(camera.screen(point))
                for a, b in zip(actual, point):
                    self.assertAlmostEqual(a, b)
            self.assertTrue(all(isinstance(v, int) for v in camera.crop))

    def test_follow_is_bounded_at_all_corners_and_preserves_overview(self):
        camera = ZoomCamera(WORLD_RECT)
        camera.follow((500, 300))
        self.assertEqual(camera.crop, tuple(WORLD_RECT))
        camera.step(2)
        for point in (WORLD_RECT.topleft, (991, 96), (24, 623), (991, 623)):
            camera.follow(point)
            self.assertTrue(WORLD_RECT.contains(pygame.Rect(camera.crop)))
            self.assertTrue(WORLD_RECT.collidepoint(camera.screen(point)))


class ZoomTests(unittest.TestCase):
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

    def click_zoom(self, text):
        button = next((b for b in self.scene.buttons if b.text == text), None)
        self.assertIsNotNone(button, f'Falta botón {text}')
        self.scene.handle_events([pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, pos=button.rect.center, button=1)])

    def test_zoom_buttons_levels_and_clicks_do_not_reach_domain(self):
        with patch.object(self.game.state, 'set_destination') as move:
            self.click_zoom('Zoom +')
            self.assertEqual(self.renderer.camera.zoom, 1.25)
            self.click_zoom('Zoom +')
            self.click_zoom('Zoom +')
            self.assertEqual(self.renderer.camera.zoom, 1.5)
            for _ in range(3):
                self.click_zoom('Zoom −')
            self.assertEqual(self.renderer.camera.zoom, 1)
        move.assert_not_called()

    def test_click_selection_all_maps_levels_and_camera_positions(self):
        for map_id in ('hondonada', 'puesto', 'planta'):
            self.game.start_new_game(map_id)
            state = self.game.state
            for level in range(3):
                self.renderer.camera.level = level
                for cell in self.renderer.projection.layout.nodes:
                    state.player.cell = cell
                    self.scene._refresh_camera()
                    point = self.renderer.camera.screen(self.renderer.projection.center(cell))
                    self.assertTrue(WORLD_RECT.collidepoint(point))
                    self.assertEqual(self.renderer.pick(point), cell, (map_id, level, cell))
                target = state.player.cell
                point = self.renderer.camera.screen(self.renderer.projection.center(target))
                with patch.object(state, 'set_destination') as move:
                    move.return_value.ok = True
                    self.scene.handle_events([pygame.event.Event(
                        pygame.MOUSEBUTTONDOWN, pos=point, button=1)])
                move.assert_called_once_with(target)
            for point in ((23, 300), (992, 300), (500, 95), (500, 624)):
                self.assertIsNone(self.renderer.pick(point))

    def test_camera_follows_interpolated_foot_and_refreshes_stationary_hover(self):
        for map_id in ('hondonada', 'puesto', 'planta'):
            self.game.start_new_game(map_id)
            state = self.game.state
            projection = self.renderer.projection
            self.renderer.camera.level = 2
            # Seleccionar un tramo interior donde el seguimiento no se limite.
            candidates = [(cell, neighbor) for cell in state.grid.neighbors(state.player.cell)
                          for neighbor in state.grid.neighbors(cell)]
            start, end = candidates[0]
            state.player.cell = end
            state.motions[state.player.id] = Motion(start, end, elapsed=.07, duration=.14)
            self.scene._pointer_pos = WORLD_RECT.center
            self.scene.draw(self.game.screen)
            a, b = projection.center(start), projection.center(end)
            foot = tuple((x+y)/2 for x, y in zip(a, b))
            expected = ZoomCamera(WORLD_RECT)
            expected.level = 2
            expected.follow(foot)
            self.assertEqual(self.renderer.camera.crop, expected.crop)
            self.assertEqual(self.renderer.actors[state.player.id].foot, foot)
            self.assertEqual(self.scene.hover_cell, self.renderer.pick(WORLD_RECT.center))
            state.motions[state.player.id].elapsed = .14
            self.scene.draw(self.game.screen)
            self.assertEqual(self.scene.hover_cell, self.renderer.pick(WORLD_RECT.center))
            self.assertEqual(state.player.cell, end)

    def test_reset_new_game_and_map_transition(self):
        self.click_zoom('Zoom +')
        state = self.game.state
        state.player.cell = (4, 10)
        self.assertTrue(state.travel('to_puesto'))
        self.scene.handle_events([])
        self.assertEqual(self.renderer.camera.zoom, 1.25)
        self.assertIs(self.renderer.projection, self.renderer.puesto.projection)
        self.assertEqual(self.renderer.pick(self.renderer.camera.screen(
            self.renderer.projection.center(state.player.cell))), state.player.cell)
        self.scene.reset()
        self.assertEqual(self.renderer.camera.zoom, 1)
        self.click_zoom('Zoom +')
        self.game.start_new_game()
        self.assertEqual(self.renderer.camera.zoom, 1)
        self.assertIsNone(self.scene.hover_cell)
        self.assertIsNone(self.scene._pointer_pos)

    def test_composition_uses_reusable_buffer_and_keeps_panel_pixels_fixed(self):
        self.scene.draw(self.game.screen)
        before = self.game.screen.subsurface((1008, 0, 272, 800)).copy()
        # Calentar actores una vez; el zoom no vuelve a preparar recursos.
        self.click_zoom('Zoom +')
        original_scale = pygame.transform.smoothscale
        with (patch('pygame.image.load') as load,
              patch('pygame.transform.smoothscale', wraps=original_scale) as scale):
            for _ in range(3):
                self.scene.draw(self.game.screen)
        load.assert_not_called()
        self.assertEqual(scale.call_count, 3)
        for call in scale.call_args_list:
            self.assertIs(call.args[2], self.renderer._zoom_surface)
        self.assertEqual(pygame.image.tobytes(before, 'RGB'), pygame.image.tobytes(
            self.game.screen.subsurface((1008, 0, 272, 800)), 'RGB'))

    def test_exit_markers_are_drawn_into_world_before_zoom(self):
        self.click_zoom('Zoom +')
        with patch.object(self.renderer.type, 'text', wraps=self.renderer.type.text) as text:
            self.scene.draw(self.game.screen)
        calls = [c for c in text.call_args_list if str(c.args[1]).startswith('E: ')]
        self.assertTrue(calls)
        self.assertTrue(all(c.args[0] is self.renderer._world_surface for c in calls))

    def test_dialogue_captures_zoom_click(self):
        state = self.game.state
        state.active_dialogue = {'id': 'test'}
        self.click_zoom('Zoom +')
        self.assertEqual(self.renderer.camera.zoom, 1)
        state.active_dialogue = None

    def test_world_render_preserves_callers_clip_at_all_levels(self):
        screen = self.game.screen
        clip = pygame.Rect(400, 300, 60, 50)
        for level in range(3):
            screen.set_clip(None)
            screen.fill((255, 0, 255))
            screen.set_clip(clip)
            self.renderer.camera.level = level
            self.renderer.draw(screen, self.game.state, None)
            self.assertEqual(screen.get_clip(), clip)
            self.assertEqual(pygame.image.tobytes(screen.subsurface((24, 96, 300, 528)), 'RGB'),
                             bytes((255, 0, 255)) * (300 * 528))
        screen.set_clip(None)


if __name__ == '__main__':
    unittest.main()
