"""Opciones de volumen con SDL dummy; no certifica escucha nativa."""
import os
import unittest
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

import pygame
from game.app import LastValveGame


class OptionsMenuTests(unittest.TestCase):
    def setUp(self):
        self.game = LastValveGame(audio_enabled=False)

    def tearDown(self):
        self.game.stop()
        pygame.quit()

    def click_button(self, text):
        button = next((b for b in self.game.current_scene.buttons if b.text == text), None)
        self.assertIsNotNone(button, f'Falta el botón {text}')
        self.game.handle_specific_events(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, pos=button.rect.center, button=1))

    def open_options(self):
        self.click_button('Opciones')
        self.assertIs(self.game.current_scene, self.game.scenes['options'])

    def test_options_button_opens_without_starting_a_game(self):
        self.open_options()
        self.game.update_game_logic(.02)
        self.game.draw_game_elements()
        self.assertIsNone(self.game.state)

    def test_controls_adjust_music_and_effects_independently(self):
        self.open_options()
        self.click_button('Música −')
        self.assertAlmostEqual(self.game.music_volume, .9)
        self.assertEqual(self.game.effects_volume, 1)
        self.click_button('Efectos −')
        self.assertAlmostEqual(self.game.effects_volume, .9)
        self.assertAlmostEqual(self.game.music_volume, .9)
        self.click_button('Música +')
        self.assertEqual(self.game.music_volume, 1)
        self.assertAlmostEqual(self.game.effects_volume, .9)
        self.click_button('Efectos +')
        self.assertEqual(self.game.effects_volume, 1)

    def test_controls_stop_at_silence_and_full_volume(self):
        self.open_options()
        for label, attribute in (('Música', 'music_volume'), ('Efectos', 'effects_volume')):
            for _ in range(12):
                self.click_button(f'{label} −')
            self.assertEqual(getattr(self.game, attribute), 0)
            self.click_button(f'{label} +')
            self.assertAlmostEqual(getattr(self.game, attribute), .1)
            for _ in range(12):
                self.click_button(f'{label} +')
            self.assertEqual(getattr(self.game, attribute), 1)

    def test_back_button_and_escape_return_to_menu(self):
        self.open_options()
        self.click_button('Volver al menú')
        self.assertIs(self.game.current_scene, self.game.scenes['menu'])
        self.open_options()
        self.game.handle_specific_events(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        self.assertIs(self.game.current_scene, self.game.scenes['menu'])
        self.assertIsNone(self.game.state)

    def test_enter_in_options_does_not_start_a_game(self):
        self.open_options()
        self.game.handle_specific_events(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        self.assertIsNone(self.game.state)
        self.assertIs(self.game.current_scene, self.game.scenes['options'])

    def test_volume_survives_reopening_options_and_starting_new_games(self):
        self.open_options()
        self.click_button('Música −')
        self.click_button('Efectos −')
        self.click_button('Volver al menú')
        for _ in range(2):
            self.click_button('Comenzar')
            self.game.change_scene('menu')
        self.open_options()
        self.assertAlmostEqual(self.game.music_volume, .9)
        self.assertAlmostEqual(self.game.effects_volume, .9)

    def test_percentages_are_drawn_from_current_settings_without_loading_assets(self):
        self.open_options()
        self.click_button('Música −')
        self.click_button('Efectos −')
        scene = self.game.current_scene
        with patch.object(scene.type, 'text', wraps=scene.type.text) as text, \
                patch.object(self.game.assets, 'load_image') as load:
            self.game.draw_game_elements()
        labels = [call.args[1] for call in text.call_args_list]
        self.assertIn('Música: 90 %', labels)
        self.assertIn('Efectos: 90 %', labels)
        load.assert_not_called()


class AudioVolumeTests(unittest.TestCase):
    def setUp(self):
        self.game = LastValveGame(audio_enabled=True)

    def tearDown(self):
        self.game.stop()
        pygame.quit()

    def test_defaults_preserve_existing_mix(self):
        self.assertEqual(getattr(self.game, 'music_volume', None), 1)
        self.assertEqual(getattr(self.game, 'effects_volume', None), 1)
        for name in self.game.manifest['sounds']:
            self.assertAlmostEqual(self.game.assets.get_sound(name).get_volume(), .35, delta=.008)
        for kind, resource in self.game.manifest['combat_sounds'].items():
            self.assertAlmostEqual(self.game.assets.get_sound(f'combat_{kind}').get_volume(),
                                   resource['volume'], delta=.008)

    def test_effects_scale_every_ui_and_combat_sound_but_not_music(self):
        self.assertTrue(callable(getattr(self.game, 'set_effects_volume', None)))
        self.game.start_new_game()
        self.game.combat_sound('guard')
        with patch('pygame.mixer.music.set_volume') as music:
            self.game.set_effects_volume(.4)
        music.assert_not_called()
        for name in self.game.manifest['sounds']:
            self.assertAlmostEqual(self.game.assets.get_sound(name).get_volume(), .35 * .4, delta=.008)
        for kind, resource in self.game.manifest['combat_sounds'].items():
            self.assertAlmostEqual(self.game.assets.get_sound(f'combat_{kind}').get_volume(),
                                   resource['volume'] * .4, delta=.008)
        self.assertEqual(self.game.assets.get_sound('combat_guard').get_num_channels(), 1)

    def test_music_changes_immediately_without_restarting_track_or_changing_effects(self):
        self.assertTrue(callable(getattr(self.game, 'set_music_volume', None)))
        self.game.start_new_game()
        before = {name: sound.get_volume() for name, sound in self.game.assets.sounds.items()}
        with patch('pygame.mixer.music.load') as load, patch('pygame.mixer.music.play') as play:
            self.game.set_music_volume(.4)
            self.assertAlmostEqual(pygame.mixer.music.get_volume(), .35 * .4, delta=.008)
        load.assert_not_called()
        play.assert_not_called()
        self.assertTrue(pygame.mixer.music.get_busy())
        self.assertEqual(before, {name: sound.get_volume() for name, sound in self.game.assets.sounds.items()})

    def test_music_setting_applies_to_all_maps_and_after_restart(self):
        self.assertTrue(callable(getattr(self.game, 'set_music_volume', None)))
        self.game.set_music_volume(.2)
        for map_id in ('hondonada', 'puesto', 'planta', 'hondonada'):
            self.game.start_new_game(map_id)
            self.assertAlmostEqual(pygame.mixer.music.get_volume(),
                                   self.game.manifest['ambiences'][map_id]['volume'] * .2, delta=.008)
        self.game.state.player.cell = self.game.state.world.exits['to_puesto'].cell
        self.game.handle_specific_events(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
        self.assertEqual(self.game.state.map_id, 'puesto')
        self.assertAlmostEqual(pygame.mixer.music.get_volume(),
                               self.game.manifest['ambiences']['puesto']['volume'] * .2, delta=.008)

    def test_mute_and_restore_do_not_compound_attenuation(self):
        self.assertTrue(callable(getattr(self.game, 'set_effects_volume', None)))
        self.game.start_new_game()
        for level in (.5, .5, 0, 1):
            self.game.set_effects_volume(level)
            self.game.set_music_volume(level)
            self.assertAlmostEqual(pygame.mixer.music.get_volume(), .35 * level, delta=.008)
            for name in self.game.manifest['sounds']:
                self.assertAlmostEqual(self.game.assets.get_sound(name).get_volume(), .35 * level, delta=.008)
            for kind, resource in self.game.manifest['combat_sounds'].items():
                self.assertAlmostEqual(self.game.assets.get_sound(f'combat_{kind}').get_volume(),
                                       resource['volume'] * level, delta=.008)

    def test_volume_setters_clamp_to_valid_range(self):
        self.assertTrue(callable(getattr(self.game, 'set_effects_volume', None)))
        for requested, expected in ((-1, 0), (2, 1)):
            self.game.set_effects_volume(requested)
            self.game.set_music_volume(requested)
            self.assertEqual(self.game.effects_volume, expected)
            self.assertEqual(self.game.music_volume, expected)


class SilentOptionsTests(unittest.TestCase):
    def test_options_work_without_initializing_or_accessing_mixer(self):
        pygame.quit()
        with patch('pygame.mixer.init') as initialize, \
                patch('pygame.mixer.Sound') as sound, \
                patch('pygame.mixer.music') as music:
            game = LastValveGame(audio_enabled=False)
            try:
                self.assertTrue(callable(getattr(game, 'set_effects_volume', None)))
                game.set_effects_volume(.3)
                game.set_music_volume(.2)
                game.change_scene('options')
                game.update_game_logic(.02)
                game.draw_game_elements()
                game.start_new_game()
                self.assertEqual(game.effects_volume, .3)
                self.assertEqual(game.music_volume, .2)
                initialize.assert_not_called()
                sound.assert_not_called()
                self.assertFalse(music.mock_calls)
            finally:
                game.stop()
                pygame.quit()


if __name__ == '__main__':
    unittest.main()
