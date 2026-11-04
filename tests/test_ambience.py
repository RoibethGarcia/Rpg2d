"""Ambientación por mapa con SDL dummy; no acredita escucha ni mezcla audible."""
import hashlib
import json
import os
import unittest
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

import pygame
from game.app import LastValveGame, ROOT


class AmbienceAssetTests(unittest.TestCase):
    def test_initial_map_has_original_user_supplied_track_and_provenance(self):
        manifest = json.loads((ROOT / 'assets/manifest.json').read_text())
        self.assertIn('ambiences', manifest)
        self.assertEqual(set(manifest['ambiences']), {'hondonada', 'puesto', 'planta'})
        entry = manifest['ambiences']['hondonada']
        self.assertEqual(entry['path'], 'assets/sounds/ambience/prologue.mp3')
        self.assertEqual(entry['original_path'], 'prologue.mp3')
        self.assertEqual(entry['source_type'], 'user_supplied')
        self.assertEqual(entry['redistribution_status'], 'pending_confirmation')
        self.assertNotIn('license', entry)
        self.assertNotIn('license_file', entry)
        self.assertTrue(entry['author'])
        self.assertTrue(entry['source'])
        self.assertGreater(entry['volume'], 0)
        self.assertLessEqual(entry['volume'], 1)
        path = (ROOT / entry['path']).resolve()
        self.assertTrue(path.is_relative_to(ROOT / 'assets/sounds'))
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry['sha256'])
        provenance = (ROOT / entry['provenance_file']).resolve()
        self.assertTrue(provenance.is_relative_to(ROOT / 'assets/provenance'))
        self.assertTrue(provenance.is_file())

    def test_second_map_has_original_user_supplied_track_and_provenance(self):
        manifest = json.loads((ROOT / 'assets/manifest.json').read_text())
        self.assertIn('puesto', manifest['ambiences'])
        entry = manifest['ambiences']['puesto']
        self.assertEqual(entry['path'], 'assets/sounds/ambience/heroic-demise-new.mp3')
        self.assertEqual(entry['original_path'], 'Heroic Demise (New).mp3')
        self.assertEqual(entry['source_type'], 'user_supplied')
        self.assertEqual(entry['redistribution_status'], 'pending_confirmation')
        self.assertNotIn('license', entry)
        self.assertNotIn('license_file', entry)
        self.assertTrue(entry['author'])
        self.assertTrue(entry['source'])
        self.assertGreater(entry['volume'], 0)
        self.assertLessEqual(entry['volume'], 1)
        path = (ROOT / entry['path']).resolve()
        self.assertTrue(path.is_relative_to(ROOT / 'assets/sounds'))
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry['sha256'])
        provenance = (ROOT / entry['provenance_file']).resolve()
        self.assertTrue(provenance.is_relative_to(ROOT / 'assets/provenance'))
        self.assertTrue(provenance.is_file())

    def test_third_map_has_original_user_supplied_track_and_provenance(self):
        manifest = json.loads((ROOT / 'assets/manifest.json').read_text())
        self.assertIn('planta', manifest['ambiences'])
        entry = manifest['ambiences']['planta']
        self.assertEqual(entry['path'], 'assets/sounds/ambience/gran-batalla.mp3')
        self.assertEqual(entry['original_path'], 'Gran Batalla.mp3')
        self.assertEqual(entry['source_type'], 'user_supplied')
        self.assertEqual(entry['redistribution_status'], 'pending_confirmation')
        self.assertNotIn('license', entry)
        self.assertNotIn('license_file', entry)
        self.assertTrue(entry['author'])
        self.assertTrue(entry['source'])
        self.assertGreater(entry['volume'], 0)
        self.assertLessEqual(entry['volume'], 1)
        path = (ROOT / entry['path']).resolve()
        self.assertTrue(path.is_relative_to(ROOT / 'assets/sounds'))
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry['sha256'])
        provenance = (ROOT / entry['provenance_file']).resolve()
        self.assertTrue(provenance.is_relative_to(ROOT / 'assets/provenance'))
        self.assertTrue(provenance.is_file())


class AmbienceTests(unittest.TestCase):
    def setUp(self):
        self.music_patch = patch('game.app.pygame.mixer.music')
        self.music = self.music_patch.start()
        self.addCleanup(self.music_patch.stop)
        self.addCleanup(pygame.quit)
        self.game = LastValveGame(audio_enabled=True)

    def test_menu_is_silent_and_new_game_streams_infinite_loop(self):
        self.music.load.assert_not_called()
        self.music.play.assert_not_called()
        self.game.start_new_game()
        self.music.load.assert_called_once_with(str(ROOT / 'assets/sounds/ambience/prologue.mp3'))
        self.music.set_volume.assert_called_once_with(self.game.manifest['ambiences']['hondonada']['volume'])
        self.music.play.assert_called_once_with(loops=-1)

    def test_frames_dialogue_and_ui_do_not_restart_or_stop_ambience(self):
        self.game.start_new_game()
        for _ in range(3):
            self.game.update_game_logic(.02)
            self.game.draw_game_elements()
        state = self.game.state
        npc = next(obj for obj in state.objects if obj['kind'] == 'npc')
        state.player.cell = next(cell for cell in state.grid.neighbors(npc['cell'])
                                 if cell not in state.occupied('vera'))
        self.assertTrue(self.game.state.interact().ok)
        self.assertIsNotNone(self.game.state.active_dialogue)
        self.game.update_game_logic(.02)
        for cue in ('click', 'confirm', 'error', 'back'):
            self.game.sound(cue)
        self.music.load.assert_called_once()
        self.music.play.assert_called_once_with(loops=-1)
        self.music.stop.assert_not_called()
        self.music.unload.assert_not_called()
        self.assertTrue(self.game.ui_channel.get_busy())

    def test_travel_via_input_switches_tracks_and_return_reloads_prologue(self):
        self.game.start_new_game()
        self.game.state.player.cell = self.game.state.world.exits['to_puesto'].cell
        self.game.handle_specific_events(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
        self.assertEqual(self.game.state.map_id, 'puesto')
        self.music.stop.assert_called_once()
        self.music.unload.assert_called_once()
        self.assertEqual(self.music.load.call_count, 2)
        self.music.load.assert_called_with(str(ROOT / 'assets/sounds/ambience/heroic-demise-new.mp3'))
        self.music.play.assert_called_with(loops=-1)
        self.game.state.player.cell = self.game.state.world.exits['to_hondonada'].cell
        self.game.handle_specific_events(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
        self.assertEqual(self.game.state.map_id, 'hondonada')
        self.assertEqual(self.music.load.call_count, 3)
        self.assertEqual(self.music.play.call_count, 3)
        self.music.load.assert_called_with(str(ROOT / 'assets/sounds/ambience/prologue.mp3'))
        self.assertEqual(self.music.stop.call_count, 2)
        self.assertEqual(self.music.unload.call_count, 2)

    def test_update_also_synchronizes_domain_travel(self):
        self.game.start_new_game()
        self.game.state.player.cell = self.game.state.world.exits['to_puesto'].cell
        self.assertTrue(self.game.state.travel('to_puesto').ok)
        self.game.update_game_logic(.02)
        self.music.stop.assert_called_once()
        self.music.unload.assert_called_once()
        self.music.load.assert_called_with(str(ROOT / 'assets/sounds/ambience/heroic-demise-new.mp3'))

    def test_menu_stops_track_and_new_game_restarts(self):
        self.game.start_new_game()
        self.game.change_scene('menu')
        self.music.stop.assert_called_once()
        self.music.unload.assert_called_once()
        self.game.start_new_game()
        self.assertEqual(self.music.play.call_count, 2)

    def test_new_game_in_same_map_restarts_track(self):
        self.game.start_new_game()
        self.game.start_new_game()
        self.music.stop.assert_called_once()
        self.music.unload.assert_called_once()
        self.assertEqual(self.music.play.call_count, 2)

    def test_terminal_states_stop_track(self):
        for map_id in ('hondonada', 'puesto', 'planta'):
            for mode in ('victory', 'defeat'):
                with self.subTest(map_id=map_id, mode=mode):
                    self.game.start_new_game(map_id)
                    self.music.reset_mock()
                    self.game.state.mode = mode
                    self.game.update_game_logic(.02)
                    self.assertIs(self.game.current_scene, self.game.scenes[mode])
                    self.music.stop.assert_called_once()
                    self.music.unload.assert_called_once()

    def test_close_window_stops_and_unloads_track(self):
        self.game.start_new_game()
        self.game.running = True
        with patch('pygame.event.get', return_value=[pygame.event.Event(pygame.QUIT)]):
            self.game._handle_events()
        self.assertFalse(self.game.running)
        self.music.stop.assert_called_once()
        self.music.unload.assert_called_once()

    def test_direct_start_in_planta_loops_without_reloading_on_frames_or_ui(self):
        self.game.start_new_game('planta')
        self.music.load.assert_called_once_with(str(ROOT / 'assets/sounds/ambience/gran-batalla.mp3'))
        self.music.set_volume.assert_called_once_with(self.game.manifest['ambiences']['planta']['volume'])
        self.music.play.assert_called_once_with(loops=-1)
        for _ in range(3):
            self.game.update_game_logic(.02)
        self.game.sound('click')
        self.music.load.assert_called_once()
        self.music.play.assert_called_once()
        self.music.stop.assert_not_called()

    def test_direct_start_in_puesto_loops_without_reloading_on_frames_or_ui(self):
        self.game.start_new_game('puesto')
        self.music.load.assert_called_once_with(str(ROOT / 'assets/sounds/ambience/heroic-demise-new.mp3'))
        self.music.set_volume.assert_called_once_with(self.game.manifest['ambiences']['puesto']['volume'])
        self.music.play.assert_called_once_with(loops=-1)
        for _ in range(3):
            self.game.update_game_logic(.02)
        self.game.sound('click')
        self.music.load.assert_called_once()
        self.music.play.assert_called_once()
        self.music.stop.assert_not_called()

    def test_travel_between_puesto_and_planta_switches_tracks(self):
        self.game.start_new_game('puesto')
        # Fixture: la salida existente exige haber abierto mantenimiento.
        self.game.state.opened.add('maintenance')
        self.game.state.player.cell = self.game.state.world.exits['to_planta'].cell
        self.game.handle_specific_events(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
        self.assertEqual(self.game.state.map_id, 'planta')
        self.music.stop.assert_called_once()
        self.music.unload.assert_called_once()
        self.assertEqual(self.music.load.call_count, 2)
        self.music.load.assert_called_with(str(ROOT / 'assets/sounds/ambience/gran-batalla.mp3'))
        self.music.play.assert_called_with(loops=-1)
        self.game.state.player.cell = self.game.state.world.exits['to_puesto'].cell
        self.game.handle_specific_events(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
        self.assertEqual(self.game.state.map_id, 'puesto')
        self.music.load.assert_called_with(str(ROOT / 'assets/sounds/ambience/heroic-demise-new.mp3'))
        self.assertEqual(self.music.load.call_count, 3)
        self.assertEqual(self.music.play.call_count, 3)
        self.assertEqual(self.music.stop.call_count, 2)
        self.assertEqual(self.music.unload.call_count, 2)

    def test_explicit_silent_mode_never_touches_music(self):
        pygame.quit()
        self.music.reset_mock()
        with patch('pygame.mixer.init') as initialize:
            game = LastValveGame(audio_enabled=False)
            game.start_new_game()
            game.start_new_game('planta')
            game.update_game_logic(.02)
            game.change_scene('menu')
            game.stop()
        initialize.assert_not_called()
        self.assertEqual(self.music.mock_calls, [])

    def test_resource_errors_are_not_hidden(self):
        self.music.load.side_effect = pygame.error('MP3 inválido')
        with self.assertRaisesRegex(pygame.error, 'MP3 inválido'):
            self.game.start_new_game()


class RealAmbienceIntegrationTests(unittest.TestCase):
    def tearDown(self):
        pygame.quit()

    def test_real_mp3_stream_decodes_from_other_cwd_and_stops_on_menu(self):
        import tempfile
        from contextlib import chdir

        with tempfile.TemporaryDirectory() as cwd, chdir(cwd):
            game = LastValveGame(audio_enabled=True)
            self.assertFalse(pygame.mixer.music.get_busy())
            game.start_new_game()
            self.assertTrue(pygame.mixer.music.get_busy())
            game.sound('error')
            self.assertTrue(pygame.mixer.music.get_busy())
            self.assertTrue(game.ui_channel.get_busy())
            game.change_scene('menu')
            self.assertFalse(pygame.mixer.music.get_busy())

    def test_planta_mp3_decodes_from_other_cwd_and_stops_on_menu(self):
        import tempfile
        from contextlib import chdir

        with tempfile.TemporaryDirectory() as cwd, chdir(cwd):
            game = LastValveGame(audio_enabled=True)
            with patch('pygame.mixer.music.load', wraps=pygame.mixer.music.load) as load:
                game.start_new_game('planta')
                load.assert_called_once_with(str(ROOT / 'assets/sounds/ambience/gran-batalla.mp3'))
                self.assertTrue(pygame.mixer.music.get_busy())
                game.sound('error')
                self.assertTrue(pygame.mixer.music.get_busy())
                self.assertTrue(game.ui_channel.get_busy())
                game.change_scene('menu')
                self.assertFalse(pygame.mixer.music.get_busy())

    def test_puesto_mp3_decodes_from_other_cwd_and_switches_back_to_prologue(self):
        import tempfile
        from contextlib import chdir

        with tempfile.TemporaryDirectory() as cwd, chdir(cwd):
            game = LastValveGame(audio_enabled=True)
            with patch('pygame.mixer.music.load', wraps=pygame.mixer.music.load) as load:
                game.start_new_game('puesto')
                load.assert_called_once_with(str(ROOT / 'assets/sounds/ambience/heroic-demise-new.mp3'))
                self.assertTrue(pygame.mixer.music.get_busy())
                game.sound('error')
                self.assertTrue(pygame.mixer.music.get_busy())
                self.assertTrue(game.ui_channel.get_busy())
                game.state.player.cell = game.state.world.exits['to_hondonada'].cell
                game.handle_specific_events(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
                self.assertEqual(game.state.map_id, 'hondonada')
                load.assert_called_with(str(ROOT / 'assets/sounds/ambience/prologue.mp3'))
                self.assertEqual(load.call_count, 2)
                self.assertTrue(pygame.mixer.music.get_busy())
                game.stop()
                self.assertFalse(pygame.mixer.music.get_busy())


if __name__ == '__main__':
    unittest.main()
