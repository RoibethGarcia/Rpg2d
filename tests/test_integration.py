"""QA independiente del input/escenas: SDL dummy, no revisión audiovisual.

Las fixtures pequeñas declaran explícitamente HP/posiciones para transiciones;
la viabilidad del contenido real está en tests.test_playthrough.
"""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import pygame
from game.app import LastValveGame
from game.model import GameState, Unit
from game.world import GridMap

ROOT = Path(__file__).resolve().parents[1]


def encounter_fixture(hp=16, player_hp=30, boss=False):
    return GameState(GridMap(24, 16), Unit('vera', 'Vera', (2, 3), player_hp, 30),
                     {'enemy': Unit('enemy', 'Enemigo de prueba', (3, 3), hp, hp,
                                    damage=3, boss=boss)})


def snapshot(state):
    return (state.player.cell, state.player.hp, state.player.ap, state.medkits,
            tuple((u.id, u.cell, u.hp, u.ap) for u in state.enemies.values()),
            tuple(state.route),
            tuple((uid, m.start, m.end, m.elapsed) for uid, m in state.motions.items()))


class InputSceneIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.game = LastValveGame(audio_enabled=False)

    def tearDown(self):
        pygame.quit()

    def click(self, point):
        self.game.handle_specific_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                           pos=point, button=1))

    def key(self, key):
        self.game.handle_specific_events(pygame.event.Event(pygame.KEYDOWN, key=key))

    def use_fixture(self, state):
        self.game.state = state
        self.game.change_scene('play')
        self.game.scenes['play'].reset()

    def test_real_menu_click_and_play_menu_restart_create_fresh_real_state(self):
        self.assertIsNone(self.game.state)
        self.click((640, 440))
        self.assertIs(self.game.current_scene, self.game.scenes['play'])
        original = self.game.state
        self.assertEqual((original.player.hp, len(original.enemies), original.medkits), (30, 4, 1))
        # Una orden real queda pendiente antes de abandonar la partida.
        self.key(pygame.K_d)
        self.assertIn('vera', original.motions)
        self.click((1130, 755))
        self.assertIs(self.game.current_scene, self.game.scenes['menu'])
        self.click((640, 440))
        self.assertIsNot(self.game.state, original)
        self.assertFalse(self.game.state.motions or self.game.state.route)
        self.assertEqual((self.game.state.player.hp, self.game.state.medkits), (30, 1))

    def test_blank_panels_and_action_button_never_leak_clicks_to_world(self):
        state = encounter_fixture()
        self.use_fixture(state)
        before = snapshot(state)
        for point in [(500, 50), (20, 790), (1100, 300), (100, 710)]:
            self.click(point)
            self.assertEqual(snapshot(state), before)

    def test_map_click_and_wasd_reach_the_same_logical_destination(self):
        clicked = encounter_fixture()
        self.use_fixture(clicked)
        target = (2, 2)
        point = self.game.scenes['play'].renderer.projection.center(target)
        self.click(point)
        self.game.update_game_logic(.14)
        self.assertEqual(clicked.player.cell, target)
        keyboard = encounter_fixture()
        self.use_fixture(keyboard)
        self.key(pygame.K_w)
        self.game.update_game_logic(.14)
        self.assertEqual(keyboard.player.cell, clicked.player.cell)
        self.assertEqual(keyboard.player.ap, clicked.player.ap)

    def test_actions_during_enemy_turn_never_mutate_domain(self):
        state = encounter_fixture()
        self.use_fixture(state)
        self.key(pygame.K_d)  # Contacto, sin ataque gratuito.
        self.key(pygame.K_SPACE)
        self.assertEqual(state.turn, 'enemy')
        before = snapshot(state)
        for point in [(100, 710), (280, 710), (480, 710), (680, 710)]:
            self.click(point)
            self.assertEqual(snapshot(state), before)
        self.key(pygame.K_w)
        self.assertEqual(snapshot(state), before)

    def test_action_buttons_while_player_moves_do_not_double_spend(self):
        state = encounter_fixture()
        self.use_fixture(state)
        self.key(pygame.K_d)
        self.key(pygame.K_w)
        self.assertIn('vera', state.motions)
        before = snapshot(state)
        for point in [(100, 710), (280, 710), (480, 710), (680, 710)]:
            self.click(point)
            self.assertEqual(snapshot(state), before)
        self.game.update_game_logic(.14)
        self.assertEqual((state.player.cell, state.player.ap), ((2, 2), 5))

    def test_defeat_from_enemy_action_routes_to_terminal_and_back_to_menu(self):
        state = encounter_fixture(player_hp=3)
        self.use_fixture(state)
        self.key(pygame.K_d)
        self.key(pygame.K_SPACE)
        self.game.update_game_logic(1)
        self.assertEqual(state.mode, 'defeat')
        self.assertIs(self.game.current_scene, self.game.scenes['defeat'])
        self.click((640, 565))
        self.assertIs(self.game.current_scene, self.game.scenes['menu'])
        self.click((640, 440))
        self.assertEqual(self.game.state.player.hp, 30)
        self.assertEqual(len(self.game.state.enemies), 4)

    def test_boss_fixture_ui_kill_panel_victory_and_terminal_new_game(self):
        state = encounter_fixture(hp=4, boss=True)
        state.objects = [dict(id='panel', kind='panel', cell=(2, 2), text='Agua restaurada')]
        self.use_fixture(state)
        self.key(pygame.K_d)
        self.assertEqual(state.mode, 'combat')
        self.click((100, 710))
        self.assertEqual((state.mode, state.credential), ('exploration', True))
        self.key(pygame.K_e)
        self.game.update_game_logic(.02)
        self.assertEqual(state.mode, 'victory')
        self.assertIs(self.game.current_scene, self.game.scenes['victory'])
        self.click((640, 492))
        self.assertIs(self.game.current_scene, self.game.scenes['play'])
        self.assertIsNot(self.game.state, state)
        self.assertEqual((self.game.state.player.hp, self.game.state.credential), (30, False))
        self.assertFalse(self.game.state.opened or self.game.state.collected)


class ImportAndResourceIntegrationTests(unittest.TestCase):
    def test_main_import_from_other_cwd_does_not_initialize_window_or_audio(self):
        code = ("import sys; sys.path.insert(0, sys.argv[1]); import main, pygame; "
                "assert not pygame.display.get_init(); assert not pygame.mixer.get_init(); "
                "assert not pygame.font.get_init(); assert callable(main.main)")
        with tempfile.TemporaryDirectory() as cwd:
            result = subprocess.run([sys.executable, '-c', code, str(ROOT)], cwd=cwd,
                                    capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_resources_and_world_load_from_other_cwd(self):
        code = ("import sys; sys.path.insert(0, sys.argv[1]); import pygame; "
                "from game.app import LastValveGame; "
                "g=LastValveGame(audio_enabled=False); g.start_new_game(); "
                "assert len(g.state.enemies)==4; assert len(g.assets.images)>=3; "
                "g.draw_game_elements(); pygame.quit()")
        with tempfile.TemporaryDirectory() as cwd:
            result = subprocess.run([sys.executable, '-c', code, str(ROOT)], cwd=cwd,
                                    capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
