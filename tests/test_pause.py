"""Pausa real de simulación; SDL dummy no acredita escucha nativa."""
import copy
import os
import unittest
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

import pygame
from game.app import LastValveGame
from game.model import GameState, Unit
from game.world import GridMap


def snapshot(state):
    return copy.deepcopy((state.elapsed, state.map_id, state.mode, state.turn,
                          vars(state.player), state.enemies, state.route,
                          state.motions, state.last_attacks, state.medkits,
                          state._enemy_wait, state._pending_direction))


class PauseTests(unittest.TestCase):
    audio_enabled = False

    def setUp(self):
        self.game = LastValveGame(audio_enabled=self.audio_enabled)
        self.game.start_new_game()

    def tearDown(self):
        self.game.stop()
        pygame.quit()

    def key(self, key, **kwargs):
        self.game.handle_specific_events(pygame.event.Event(pygame.KEYDOWN, key=key, **kwargs))

    def click(self, label):
        button = next((b for b in self.game.current_scene.buttons if b.text == label), None)
        self.assertIsNotNone(button, f'Falta botón {label}')
        self.game.handle_specific_events(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, pos=button.rect.center, button=1))

    def pause(self):
        self.key(pygame.K_ESCAPE)
        self.assertIn('pause', self.game.scenes, 'Falta la escena de pausa')
        self.assertIs(self.game.current_scene, self.game.scenes['pause'])

    def test_escape_freezes_movement_and_preserves_route_camera_and_state(self):
        state = self.game.state
        self.key(pygame.K_d)
        self.assertTrue(state.motions)
        self.game.scenes['play'].change_zoom(1)
        before = snapshot(state)
        self.pause()
        self.game.update_game_logic(20)
        for key in (pygame.K_w, pygame.K_e, pygame.K_SPACE):
            self.key(key)
        self.assertEqual(snapshot(state), before)
        self.key(pygame.K_ESCAPE)
        self.assertIs(self.game.current_scene, self.game.scenes['play'])
        self.assertIs(self.game.state, state)
        self.assertEqual(snapshot(state), before)
        self.assertEqual(self.game.scenes['play'].renderer.camera.zoom, 1.25)
        self.game.update_game_logic(.2)
        self.assertGreater(state.elapsed, before[0])

    def test_enemy_turn_does_not_advance_until_continue(self):
        state = GameState(GridMap(24, 16), Unit('vera', 'Vera', (2, 3), 30, 30),
                          {'guard': Unit('guard', 'Guardia', (3, 3), 30, 30)})
        self.game.state = state
        self.game.scenes['play'].reset()
        state.move_direction((1, 0))
        state.end_turn()
        self.assertEqual(state.turn, 'enemy')
        before = snapshot(state)
        self.pause()
        self.click('Opciones')
        self.game.update_game_logic(30)
        self.assertEqual(snapshot(state), before)
        self.key(pygame.K_ESCAPE)
        self.click('Continuar')
        self.game.update_game_logic(.3)
        self.assertLess(state.player.hp, 30)

    def test_pending_route_is_not_cancelled_by_pausing(self):
        state = GameState(GridMap(24, 16), Unit('vera', 'Vera', (2, 3), 30, 30))
        self.game.state = state
        self.game.scenes['play'].reset()
        state.set_destination((5, 3))
        self.assertTrue(state.motions and state.route)
        before = snapshot(state)
        self.pause()
        self.game.update_game_logic(10)
        self.click('Continuar')
        self.assertEqual(snapshot(state), before)
        self.game.update_game_logic(1)
        self.assertEqual(state.player.cell, (5, 3))

    def test_attack_animation_and_feedback_survive_pause(self):
        state = GameState(GridMap(24, 16), Unit('vera', 'Vera', (2, 3), 30, 30),
                          {'guard': Unit('guard', 'Guardia', (3, 3), 30, 30)})
        self.game.state = state
        self.game.scenes['play'].reset()
        state.move_direction((1, 0))
        self.game.scenes['play'].command('attack')
        self.assertTrue(state.last_attacks)
        before = snapshot(state)
        floaters = copy.deepcopy(self.game.scenes['play'].renderer.floaters)
        self.pause()
        self.game.update_game_logic(10)
        self.click('Continuar')
        self.assertEqual(snapshot(state), before)
        self.assertEqual(self.game.scenes['play'].renderer.floaters, floaters)

    def test_options_return_to_pause_and_keep_game_frozen(self):
        state = self.game.state
        before = snapshot(state)
        self.pause()
        self.click('Opciones')
        self.assertIs(self.game.current_scene, self.game.scenes['options'])
        self.click('Música −')
        self.click('Efectos −')
        self.click('Música +')
        self.click('Efectos +')
        self.assertEqual((self.game.music_volume, self.game.effects_volume), (1, 1))
        self.click('Música −')
        self.click('Efectos −')
        self.game.update_game_logic(10)
        self.game.draw_game_elements()
        self.click('Volver a la pausa')
        self.assertIs(self.game.current_scene, self.game.scenes['pause'])
        self.click('Opciones')
        self.key(pygame.K_ESCAPE)
        self.assertIs(self.game.current_scene, self.game.scenes['pause'])
        self.click('Continuar')
        self.assertEqual(snapshot(state), before)
        self.assertAlmostEqual(self.game.music_volume, .9)
        self.assertAlmostEqual(self.game.effects_volume, .9)

    def test_pause_and_options_draw_without_updating_play_scene(self):
        self.pause()
        with patch.object(self.game.scenes['play'], 'update') as update:
            self.game.update_game_logic(5)
            self.game.draw_game_elements()
            self.click('Opciones')
            self.game.update_game_logic(5)
            self.game.draw_game_elements()
        update.assert_not_called()

    def test_repeated_escape_does_not_pause_or_resume(self):
        self.key(pygame.K_ESCAPE, repeat=True)
        self.assertIs(self.game.current_scene, self.game.scenes['play'])
        self.pause()
        self.key(pygame.K_ESCAPE, repeat=True)
        self.assertIs(self.game.current_scene, self.game.scenes['pause'])

    def test_pause_consumes_remaining_input_batch(self):
        before = snapshot(self.game.state)
        self.game.scenes['play'].handle_events([
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d)])
        self.assertIn('pause', self.game.scenes)
        self.assertIs(self.game.current_scene, self.game.scenes['pause'])
        self.assertEqual(snapshot(self.game.state), before)

    def test_return_to_menu_resets_presentation_and_options_origin(self):
        self.pause()
        self.click('Volver al menú')
        self.assertIs(self.game.current_scene, self.game.scenes['menu'])
        self.click('Opciones')
        self.click('Volver al menú')
        old = self.game.state
        self.click('Comenzar')
        self.assertIsNot(self.game.state, old)
        self.assertIs(self.game.current_scene, self.game.scenes['play'])

    def test_quit_still_works_from_pause(self):
        self.pause()
        self.game.running = True
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        self.game._handle_events()
        self.assertFalse(self.game.running)


class PauseAudioTests(PauseTests):
    audio_enabled = True

    def test_music_is_not_restarted_and_volume_changes_immediately_in_pause(self):
        for map_id in ('hondonada', 'puesto', 'planta'):
            with self.subTest(map=map_id):
                self.game.start_new_game(map_id)
                with patch('pygame.mixer.music.load') as load, \
                        patch('pygame.mixer.music.play') as play, \
                        patch('pygame.mixer.music.stop') as stop:
                    self.pause()
                    self.click('Opciones')
                    self.click('Música −')
                    self.click('Efectos −')
                    expected = self.game.manifest['ambiences'][map_id]['volume'] * self.game.music_volume
                    self.assertAlmostEqual(pygame.mixer.music.get_volume(), expected, delta=.008)
                    self.assertTrue(pygame.mixer.music.get_busy())
                    for kind, resource in self.game.manifest['combat_sounds'].items():
                        self.assertAlmostEqual(self.game.assets.get_sound(f'combat_{kind}').get_volume(),
                                               resource['volume'] * self.game.effects_volume, delta=.008)
                    self.key(pygame.K_ESCAPE)
                    self.click('Continuar')
                load.assert_not_called()
                play.assert_not_called()
                stop.assert_not_called()

    def test_leaving_pause_stops_music_and_combat_sounds(self):
        self.game.combat_sound('guard')
        self.pause()
        self.assertEqual(self.game.assets.get_sound('combat_guard').get_num_channels(), 1)
        self.click('Volver al menú')
        self.assertFalse(pygame.mixer.music.get_busy())
        self.assertEqual(self.game.assets.get_sound('combat_guard').get_num_channels(), 0)

    def test_mute_and_restore_in_pause_without_restarting_track(self):
        self.pause()
        self.click('Opciones')
        for _ in range(10):
            self.click('Música −')
            self.click('Efectos −')
        self.assertEqual(pygame.mixer.music.get_volume(), 0)
        self.assertTrue(all(sound.get_volume() == 0 for sound in self.game.assets.sounds.values()))
        self.assertTrue(pygame.mixer.music.get_busy())
        self.click('Música +')
        self.click('Efectos +')
        self.assertGreater(pygame.mixer.music.get_volume(), 0)
        self.assertTrue(all(sound.get_volume() > 0 for sound in self.game.assets.sounds.values()))


if __name__ == '__main__':
    unittest.main()
