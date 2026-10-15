"""Contratos del motor derivados del notebook, con SDL dummy explícito."""
import inspect
import json
from pathlib import Path
import tempfile
import unittest
import wave
from unittest.mock import Mock, patch

import pygame

from engine.asset_manager import AssetManager
from engine.game_loop import GameLoop
from engine.game_object import GameObject
from engine.spritesheet import Spritesheet
from engine.ui import Button, Scene


class EngineTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((80, 60))

    def tearDown(self):
        pygame.quit()

    def frames(self):
        return [pygame.Surface((8, 8)), pygame.Surface((8, 8))]

    def test_animation_uses_seconds_not_number_of_updates(self):
        actor = GameObject(10, 20, self.frames())
        actor.update(0.2)
        self.assertEqual(actor.current_frame, 1)
        self.assertEqual(actor.rect.center, (10, 20))

    def test_animation_preserves_fractional_remainder(self):
        actor = GameObject(0, 0, self.frames())
        actor.update(0.25)
        actor.update(0.07)
        self.assertEqual(actor.current_frame, 1)
        actor.update(0.02)
        self.assertEqual(actor.current_frame, 0)

    def test_scene_and_loop_publish_dt_contract(self):
        self.assertIn('dt', inspect.signature(Scene.update).parameters)
        self.assertIn('dt', inspect.signature(GameLoop.update_game_logic).parameters)

    def test_loop_converts_milliseconds_once(self):
        game = GameLoop(80, 60, 'Prueba', 60)
        game.clock = Mock()
        game.clock.tick.return_value = 125
        received = []
        def update(dt=None):
            received.append(dt)
            game.running = False
        game.update_game_logic = update
        with patch('pygame.event.get', return_value=[]):
            game.run()
        self.assertEqual(received, [0.125])
        self.assertFalse(pygame.get_init())

    def test_quit_does_not_update_or_draw(self):
        game = GameLoop(80, 60, 'Prueba', 60)
        game.update_game_logic = Mock()
        game.draw_game_elements = Mock()
        with patch('pygame.event.get', return_value=[pygame.event.Event(pygame.QUIT)]):
            game.run()
        game.update_game_logic.assert_not_called()
        game.draw_game_elements.assert_not_called()

    def test_button_plays_sound_only_for_valid_click(self):
        callback = Mock()
        button = Button(0, 0, 40, 30, 'Ir', callback)
        button.click_sound = Mock()
        for pos, mouse_button in [((60, 50), 1), ((10, 10), 3)]:
            button.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=mouse_button))
        callback.assert_not_called()
        button.click_sound.play.assert_not_called()
        button.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(10, 10), button=1))
        callback.assert_called_once_with()
        button.click_sound.play.assert_called_once_with()

    def test_asset_manager_has_real_sound_api(self):
        manager = AssetManager()
        self.assertTrue(callable(getattr(manager, 'load_sound', None)))
        self.assertTrue(callable(getattr(manager, 'get_sound', None)))

    def test_sound_load_and_missing_resources_are_not_hidden(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'click.wav'
            with wave.open(str(path), 'wb') as sound:
                sound.setnchannels(1)
                sound.setsampwidth(2)
                sound.setframerate(22050)
                sound.writeframes(b'\x00\x00' * 220)
            manager = AssetManager()
            manager.load_sound('click', path)
            self.assertIsInstance(manager.get_sound('click'), pygame.mixer.Sound)
            with self.assertRaises(KeyError):
                manager.get_sound('missing')
            with self.assertRaises(FileNotFoundError):
                manager.load_sound('missing', Path(folder) / 'missing.wav')

    def test_explicit_audio_disabled_does_not_initialize_mixer(self):
        with patch('pygame.mixer.init') as initialize:
            game = GameLoop(80, 60, 'Silencio explícito', 60, audio_enabled=False)
        initialize.assert_not_called()
        self.assertFalse(game.audio_enabled)

    def test_loop_cleans_up_when_game_logic_raises(self):
        game = GameLoop(80, 60, 'Prueba', 60, audio_enabled=False)
        game.update_game_logic = Mock(side_effect=ValueError('fallo visible'))
        with patch('pygame.event.get', return_value=[]):
            with self.assertRaisesRegex(ValueError, 'fallo visible'):
                game.run()
        self.assertFalse(pygame.get_init())

    def test_spritesheet_image_resolves_relative_to_json(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pygame.image.save(pygame.Surface((8, 8)), root / 'sheet.png')
            data = {'spritesheet_path': '/old/computer/sheet.png', 'animations': {
                'idle': [{'name': 'standing', 'x': 0, 'y': 0, 'width': 8, 'height': 8}]}}
            path = root / 'sheet.json'
            path.write_text(json.dumps(data))
            manager = AssetManager()
            manager.load_spritesheet('human', path)
            self.assertEqual(manager.get_sprite('human', 'standing').get_size(), (8, 8))
            self.assertEqual(len(manager.get_animation('human', 'idle')), 1)
            with self.assertRaises(ValueError):
                manager.get_sprite('human', 'unknown')
            with self.assertRaises(KeyError):
                manager.get_image('unknown')


if __name__ == '__main__':
    unittest.main()
