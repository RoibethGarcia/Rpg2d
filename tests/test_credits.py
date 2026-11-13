"""Créditos de victoria con SDL dummy: no certifican audio físico ni partida manual."""
import hashlib
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

import pygame
from game.app import LastValveGame
from game.scenes import VictoryScene
from game.render import Typography

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA256 = 'ec5f1a41fa76d887baf13f699d0256d76eb97b8715267dd441325d562a64598e'


class CreditsTests(unittest.TestCase):
    def setUp(self):
        self.game = LastValveGame(audio_enabled=False)

    def tearDown(self):
        pygame.quit()

    def click(self, pos, button=1):
        self.game.handle_specific_events(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, pos=pos, button=button))

    def test_original_is_registered_without_modifying_image_bytes(self):
        self.assertIn('credits', self.game.manifest['images'])
        entry = self.game.manifest['images']['credits']
        self.assertEqual(hashlib.sha256((ROOT / entry['path']).read_bytes()).hexdigest(), SOURCE_SHA256)
        self.assertEqual(entry['size'], [1645, 956])
        self.assertEqual(entry['menu_button'], [671, 839, 299, 60])
        self.assertEqual(entry['original_path'], 'Pantalla de créditos en ruinas pixel art.png')
        self.assertEqual(entry['source_type'], 'user_supplied')
        self.assertEqual(entry['redistribution_status'], 'pending_confirmation')

    def test_image_button_not_the_former_new_game_button_returns_to_menu(self):
        self.game.change_scene('victory')
        self.click((640, 492))  # Antigua posición de Nueva partida: ahora solo imagen.
        self.assertIs(self.game.current_scene, self.game.scenes['victory'])
        with patch.object(self.game, 'sound') as sound:
            self.click((638, 704))  # Centro del nuevo botón pintado, con bandas.
        self.assertIs(self.game.current_scene, self.game.scenes['menu'])
        sound.assert_called_once_with('back')

    def test_image_is_complete_proportional_centered_and_cached(self):
        scene = self.game.scenes['victory']
        self.assertTrue(hasattr(scene, 'image_rect'), 'Falta imagen de créditos proporcional')
        source = self.game.assets.get_image('credits')
        expected = source.get_rect().fit(self.game.screen.get_rect())
        expected.center = self.game.screen.get_rect().center
        self.assertEqual(scene.image_rect, expected)
        self.assertAlmostEqual(expected.width / expected.height, 1645 / 956, delta=.003)
        with patch.object(self.game.assets, 'load_image') as load, \
                patch.object(pygame.transform, 'smoothscale') as scale:
            scene.draw(self.game.screen)
            scene.draw(self.game.screen)
        load.assert_not_called()
        scale.assert_not_called()
        self.assertEqual(self.game.screen.get_at((0, 0))[:3], (0, 0, 0))
        self.assertEqual(pygame.image.tobytes(self.game.screen.subsurface(expected), 'RGB'),
                         pygame.image.tobytes(scene.image, 'RGB'))

    def test_new_art_is_rendered_without_overlays_or_source_mutation(self):
        source = self.game.assets.get_image('credits')
        before = pygame.image.tobytes(source, 'RGBA')
        with patch.object(Typography, 'text', autospec=True, side_effect=Typography.text) as text:
            scene = VictoryScene(self.game)
        text.assert_not_called()
        original = pygame.transform.smoothscale(source.convert(), scene.image_rect.size)
        self.assertEqual(pygame.image.tobytes(scene.image, 'RGB'),
                         pygame.image.tobytes(original, 'RGB'))
        self.assertEqual(pygame.image.tobytes(source, 'RGBA'), before)

    def test_hitbox_follows_letterboxing_in_taller_viewport(self):
        game = SimpleNamespace(screen=pygame.Surface((640, 800)), assets=self.game.assets,
                               manifest=self.game.manifest, sound=lambda name: None,
                               change_scene=lambda name: None, start_new_game=lambda: None,
                               audio_enabled=False)
        scene = VictoryScene(game)
        self.assertTrue(hasattr(scene, 'return_rect'), 'Falta zona clicable del botón ilustrado')
        self.assertEqual(scene.image_rect.center, game.screen.get_rect().center)
        self.assertTrue(scene.image_rect.contains(scene.return_rect))
        x, y = scene.image_rect.topleft
        w, h = scene.image_rect.size
        self.assertEqual(scene.return_rect, pygame.Rect(
            x + round(671 * w / 1645), y + round(839 * h / 956),
            round(299 * w / 1645), round(60 * h / 956)))

    def test_escape_and_enter_return_without_restarting_state(self):
        self.game.start_new_game()
        state = self.game.state
        for key in (pygame.K_ESCAPE, pygame.K_RETURN):
            self.game.change_scene('victory')
            self.game.handle_specific_events(pygame.event.Event(pygame.KEYDOWN, key=key))
            self.assertIs(self.game.current_scene, self.game.scenes['menu'])
            self.assertIs(self.game.state, state)

    def test_background_and_nonleft_clicks_do_not_navigate(self):
        self.game.change_scene('victory')
        for pos, button in (((640, 20), 1), ((10, 400), 1), ((640, 714), 3)):
            self.click(pos, button)
            self.assertIs(self.game.current_scene, self.game.scenes['victory'])

    def test_global_quit_still_works_in_credits(self):
        self.game.change_scene('victory')
        self.game.running = True
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        self.game._handle_events()
        self.assertFalse(self.game.running)

    def test_valve_activation_reaches_credits_and_leaves_gameplay_frozen(self):
        self.game.start_new_game('planta')
        state = self.game.state
        panel = next(o for o in state.objects if o['kind'] == 'panel')
        state.player.cell = next(iter(state.grid.neighbors(panel['cell'])))
        state.credential = True
        self.game.handle_specific_events(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
        self.game.update_game_logic(0)
        self.assertEqual(state.mode, 'victory')
        self.assertIs(self.game.current_scene, self.game.scenes['ending'])
        self.game.change_scene('victory')
        scene = self.game.current_scene
        self.assertIs(scene, self.game.scenes['victory'])
        self.assertTrue(hasattr(scene, 'image'), 'La victoria todavía no muestra los créditos')
        before = (state.player.cell, state.player.hp, state.player.ap, state.turn)
        self.game.handle_specific_events(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))
        self.game.update_game_logic(1)
        self.assertEqual((state.player.cell, state.player.hp, state.player.ap, state.turn), before)


if __name__ == '__main__':
    unittest.main()
