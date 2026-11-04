"""Un sonido por golpe aplicado; SDL dummy NO acredita calidad audible."""
import hashlib
import json
import os
import unittest
from unittest.mock import Mock, call, patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

import pygame
from game.app import LastValveGame, ROOT
from game.model import GameState, Unit
from game.world import GridMap


def combat(*, boss=False):
    state = GameState(GridMap(24, 16), Unit('vera', 'Vera', (2, 3), 30, 30),
                      {'enemy': Unit('enemy', 'Custodia', (3, 3), 40, 40, boss=boss)})
    state.move_direction((1, 0))
    return state


class CombatSoundAssetsTests(unittest.TestCase):
    def test_four_fixed_original_flacs_have_provenance_and_decode(self):
        manifest = json.loads((ROOT / 'assets/manifest.json').read_text())
        self.assertIn('combat_sounds', manifest, 'Faltan los sonidos fijos de combate')
        expected = {'basic': 'hit01.mp3.flac', 'power': 'hit02.mp3.flac',
                    'guard': 'hit03.mp3.flac', 'boss': 'hit07.mp3.flac'}
        self.assertEqual(set(manifest['combat_sounds']), set(expected))
        pygame.mixer.init()
        try:
            for kind, original in expected.items():
                with self.subTest(kind=kind):
                    entry = manifest['combat_sounds'][kind]
                    self.assertEqual(entry['original_path'], original)
                    self.assertEqual(entry['source_type'], 'user_supplied')
                    self.assertEqual(entry['redistribution_status'], 'pending_confirmation')
                    self.assertNotIn('license', entry)
                    self.assertNotIn('license_file', entry)
                    self.assertTrue(entry['author'])
                    self.assertTrue(entry['source'])
                    path = (ROOT / entry['path']).resolve()
                    self.assertTrue(path.is_relative_to(ROOT / 'assets/sounds/combat'))
                    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry['sha256'])
                    provenance = (ROOT / entry['provenance_file']).resolve()
                    self.assertTrue(provenance.is_relative_to(ROOT / 'assets/provenance'))
                    self.assertTrue(provenance.is_file())
                    sound = pygame.mixer.Sound(str(path))
                    self.assertGreater(sound.get_length(), 0)
                    self.assertAlmostEqual(sound.get_length(), entry['duration_seconds'], places=2)
                    self.assertTrue(0 < entry['volume'] <= 1)
        finally:
            pygame.mixer.quit()


class CombatSoundEventTests(unittest.TestCase):
    def test_distinct_player_hits_at_same_timestamp_are_not_deduplicated(self):
        state = combat()
        self.assertTrue(state.attack())
        self.assertTrue(state.attack(True))
        self.assertTrue(hasattr(state, 'drain_attack_events'), 'Falta consumo de golpes')
        events = state.drain_attack_events()
        self.assertEqual([e.kind for e in events], ['basic', 'power'])
        self.assertEqual(events[0].occurred_at, events[1].occurred_at)
        self.assertEqual((state.player.ap, state.enemies['enemy'].hp), (1, 29))

    def test_events_keep_every_enemy_hit_in_one_large_update_and_drain_once(self):
        state = combat()
        state.end_turn()
        state.update(1)
        self.assertTrue(hasattr(state, 'drain_attack_events'), 'Falta consumo de cada golpe aplicado')
        events = state.drain_attack_events()
        self.assertEqual([e.kind for e in events], ['guard'] * 3)
        self.assertEqual([e.attacker_id for e in events], ['enemy'] * 3)
        for event, expected in zip(events, (.22, .44, .66)):
            self.assertAlmostEqual(event.occurred_at, expected)
        self.assertEqual((state.player.hp, state.turn), (21, 'player'))
        self.assertFalse(state.drain_attack_events())


class CombatSoundPresentationTests(unittest.TestCase):
    def setUp(self):
        self.game = LastValveGame(audio_enabled=False)
        self.game.combat_sound = Mock()
        self.game.sound = Mock()
        self.scene = self.game.scenes['play']
        self.use_state(combat())

    def tearDown(self):
        pygame.quit()

    def use_state(self, state):
        self.game.state = state
        self.game.change_scene('play')
        self.scene.reset()

    def test_vera_uses_fixed_sound_for_each_skill_and_never_on_draw(self):
        self.assertTrue(self.scene.command('attack'))
        self.game.combat_sound.assert_called_once_with('basic')
        self.game.sound.assert_not_called()  # El impacto sustituye el confirm genérico.
        for _ in range(3):
            self.game.draw_game_elements()
            self.game.update_game_logic(0)
        self.game.combat_sound.assert_called_once_with('basic')
        self.game.update_game_logic(.20)
        self.assertTrue(self.scene.command('attack', True))
        self.assertEqual(self.game.combat_sound.call_args_list, [call('basic'), call('power')])
        self.assertEqual((self.game.state.player.ap, self.game.state.enemies['enemy'].hp), (1, 29))

    def test_rejected_repeat_and_insufficient_ap_do_not_sound(self):
        self.scene.command('attack')
        self.assertFalse(self.scene.command('attack'))
        self.game.update_game_logic(.20)
        self.game.state.player.ap = 1
        self.assertFalse(self.scene.command('attack', True))
        self.game.combat_sound.assert_called_once_with('basic')
        self.assertEqual(self.game.sound.call_args_list, [call('error'), call('error')])

    def test_out_of_range_and_wrong_turn_do_not_sound(self):
        self.game.state.enemies['enemy'].cell = (8, 3)
        self.assertFalse(self.scene.command('attack'))
        self.game.state.turn = 'enemy'
        self.assertFalse(self.scene.command('attack'))
        self.game.combat_sound.assert_not_called()

    def test_all_three_enemy_hits_sound_once_with_large_or_fractional_dt(self):
        for boss in (False, True):
            for steps in ([1.0], [.02] * 50):
                with self.subTest(boss=boss, steps=len(steps)):
                    self.use_state(combat(boss=boss))
                    self.game.combat_sound.reset_mock()
                    self.scene.command('end_turn')
                    for dt in steps:
                        self.game.update_game_logic(dt)
                    self.assertEqual(self.game.combat_sound.call_args_list,
                                     [call('boss' if boss else 'guard')] * 3)
                    self.game.update_game_logic(1)
                    self.assertEqual(self.game.combat_sound.call_count, 3)
                    self.assertEqual(self.game.state.player.hp, 21)

    def test_lethal_player_and_enemy_hits_sound_even_when_clip_is_cleared(self):
        self.game.state.enemies['enemy'].hp = 1
        self.assertTrue(self.scene.command('attack', True))
        self.game.combat_sound.assert_called_once_with('power')
        self.assertFalse(self.game.state.last_attacks)
        self.game.update_game_logic(.1)
        self.game.combat_sound.assert_called_once_with('power')
        self.use_state(combat(boss=True))
        self.game.state.player.hp = 1
        self.game.combat_sound.reset_mock()
        self.scene.command('end_turn')
        self.game.update_game_logic(1)
        self.assertIs(self.game.current_scene, self.game.scenes['defeat'])
        self.game.combat_sound.assert_called_once_with('boss')
        self.assertFalse(self.game.state.last_attacks)

    def test_context_reset_menu_and_new_game_discard_pending_events(self):
        for reset in (self.scene.reset, self.scene.to_menu, self.game.start_new_game):
            self.use_state(combat())
            self.game.state.attack()
            self.game.combat_sound.reset_mock()
            reset()
            self.game.update_game_logic(.1)
            self.game.combat_sound.assert_not_called()


class CombatSoundMixerTests(unittest.TestCase):
    def setUp(self):
        self.game = LastValveGame(audio_enabled=True)
        self.game.state = combat()
        self.game.change_scene('play')
        self.scene = self.game.scenes['play']
        self.scene.reset()

    def tearDown(self):
        self.game.stop()
        pygame.quit()

    def test_repeated_hits_overlap_without_cutting_ui_or_map_music(self):
        self.assertTrue(hasattr(self.game, 'combat_sound'), 'Falta canal de golpes independiente')
        self.game.sound('click')
        ui_sound = self.game.ui_channel.get_sound()
        for _ in range(3):
            self.game.combat_sound('guard')
        sound = self.game.assets.get_sound('combat_guard')
        self.assertEqual(sound.get_num_channels(), 3)
        self.assertIs(self.game.ui_channel.get_sound(), ui_sound)
        self.game.start_new_game('puesto')
        self.scene.command('move_direction', (0, 1))
        self.game.combat_sound('boss')
        self.game.sound('error')
        self.assertTrue(pygame.mixer.music.get_busy())
        self.assertEqual(self.game.assets.get_sound('combat_boss').get_num_channels(), 1)

    def test_reset_menu_restart_and_stop_cancel_sound_tails(self):
        self.assertTrue(hasattr(self.game, 'combat_sound'), 'Falta reproducción de golpes')
        sound = self.game.assets.get_sound('combat_basic')
        for reset in (self.scene.reset, self.scene.to_menu,
                      self.game.start_new_game, self.game.stop):
            self.game.combat_sound('basic')
            self.assertGreater(sound.get_num_channels(), 0)
            reset()
            self.assertEqual(sound.get_num_channels(), 0)

    def test_lethal_sound_tail_survives_transition_to_defeat_but_not_menu(self):
        self.assertTrue(hasattr(self.game, 'combat_sound'), 'Falta reproducción de golpes')
        self.game.state.player.hp = 1
        self.scene.command('end_turn')
        self.game.update_game_logic(.22)
        self.assertIs(self.game.current_scene, self.game.scenes['defeat'])
        sound = self.game.assets.get_sound('combat_guard')
        self.assertEqual(sound.get_num_channels(), 1)
        self.game.change_scene('menu')
        self.assertEqual(sound.get_num_channels(), 0)

    def test_victory_cancels_tails_unlike_lethal_defeat(self):
        self.game.combat_sound('power')
        self.game.state.mode = 'victory'
        self.game.update_game_logic(0)
        self.assertIs(self.game.current_scene, self.game.scenes['victory'])
        self.assertEqual(self.game.assets.get_sound('combat_power').get_num_channels(), 0)

    def test_domain_travel_discards_pending_lethal_event_and_stops_old_tails(self):
        self.game.start_new_game('puesto')
        state = self.game.state
        enemy = next(iter(state.enemies.values()))
        state.player.cell = next(c for c in state.grid.neighbors(enemy.cell)
                                 if c not in state.occupied('vera'))
        state.mode = 'combat'
        state.active_enemy_id = enemy.id
        enemy.hp = 1
        self.assertTrue(state.attack())  # Hecho pendiente sin consumir por escena.
        self.game.combat_sound('guard')
        state.player.cell = state.world.exits['to_hondonada'].cell
        self.assertTrue(state.travel('to_hondonada'))
        self.assertFalse(state.drain_attack_events())
        with patch.object(self.game, 'combat_sound') as play:
            self.game.update_game_logic(0)
            play.assert_not_called()
        self.assertEqual(self.game.assets.get_sound('combat_guard').get_num_channels(), 0)

    def test_playback_reuses_loaded_resources(self):
        self.assertTrue(hasattr(self.game, 'combat_sound'), 'Falta reproducción de golpes')
        with patch('pygame.mixer.Sound', side_effect=AssertionError('Carga por golpe')):
            for kind in ('basic', 'power', 'guard', 'boss'):
                self.game.combat_sound(kind)
                self.assertEqual(self.game.assets.get_sound(f'combat_{kind}').get_num_channels(), 1)


class SilentCombatTests(unittest.TestCase):
    def test_silent_mode_consumes_hits_without_initializing_or_using_mixer(self):
        pygame.quit()
        with patch('pygame.mixer.init') as initialize, patch('pygame.mixer.Sound') as sound:
            game = LastValveGame(audio_enabled=False)
            try:
                game.state = combat()
                game.change_scene('play')
                game.scenes['play'].command('attack')
                game.update_game_logic(.22)
                self.assertTrue(hasattr(game.state, 'drain_attack_events'), 'Falta consumir golpes')
                self.assertFalse(game.state.drain_attack_events())
                initialize.assert_not_called()
                sound.assert_not_called()
            finally:
                game.stop()
                pygame.quit()


if __name__ == '__main__':
    unittest.main()
