"""Acceso de pruebas: partida fresca con inventario temporal y menú normal."""
import unittest
from unittest.mock import patch


class StartupTests(unittest.TestCase):
    def test_planta_argument_starts_fresh_campaign_before_main_loop(self):
        import main
        with patch('main.LastValveGame') as constructor, patch('sys.argv', ['main.py', '--map', 'planta']):
            main.main()
            constructor.return_value.start_new_game.assert_called_once_with(map_id='planta')
            constructor.return_value.run.assert_called_once_with()

    def test_map_argument_starts_fresh_campaign_before_main_loop(self):
        import main
        with patch('main.LastValveGame') as constructor,patch('sys.argv',['main.py','--map','puesto']):
            game=constructor.return_value
            main.main()
            game.start_new_game.assert_called_once_with(map_id='puesto')
            game.run.assert_called_once_with()

    def test_normal_start_keeps_menu(self):
        import main
        with patch('main.LastValveGame') as constructor,patch('sys.argv',['main.py']):
            main.main()
            constructor.return_value.start_new_game.assert_not_called()
            constructor.return_value.run.assert_called_once_with()


class StartupStateTests(unittest.TestCase):
    def test_temporary_three_medkits_apply_to_every_start_and_reset(self):
        import pygame
        from game.app import LastValveGame
        from game.model import GameState
        game = LastValveGame(audio_enabled=False)
        try:
            for map_id in ('hondonada', 'puesto', 'planta'):
                with self.subTest(map_id=map_id):
                    game.start_new_game(map_id=map_id)
                    self.assertEqual(game.state.medkits, 3)
                    game.state.medkits = 0
                    game.start_new_game(map_id=map_id)
                    self.assertEqual(game.state.medkits, 3)
            self.assertEqual(GameState.new().medkits, 1)  # Balance base sin modificar.
        finally:
            pygame.quit()

    def test_explicit_planta_start_keeps_boss_guards_kits_and_credential_fresh(self):
        import pygame
        from game.app import LastValveGame
        game = LastValveGame(audio_enabled=False)
        try:
            game.start_new_game(map_id='planta')
            state = game.state
            self.assertEqual((state.map_id, state.player.cell, state.player.hp, state.medkits),
                             ('planta', (9,8), 30, 3))
            self.assertEqual(len(state.enemies), 4)
            self.assertEqual(state.enemies['boss'].hp, 48)
            self.assertFalse(state.credential or state.collected or state.opened)
            self.assertFalse(state.maps['puesto'].opened)
            game.start_new_game()
            self.assertEqual(game.state.map_id, 'hondonada')
        finally:
            pygame.quit()

    def test_explicit_puesto_start_is_fresh_and_menu_new_game_stays_normal(self):
        import pygame
        from game.app import LastValveGame
        game=LastValveGame(audio_enabled=False)
        try:
            game.start_new_game(map_id='puesto')
            state=game.state
            self.assertEqual((state.map_id,state.player.cell,state.player.hp,state.medkits),
                             ('puesto',(2,10),30,3))
            self.assertEqual({u.hp for u in state.enemies.values()},{16})
            self.assertFalse(state.opened or state.collected or state.motions or state.route)
            state.player.hp=1
            state.enemies['guard1'].hp=0
            game.start_new_game()
            self.assertEqual((game.state.map_id,game.state.player.hp,game.state.medkits),('hondonada',30,3))
            self.assertEqual(game.state.maps['puesto'].enemies['guard1'].hp,16)
        finally:
            pygame.quit()
