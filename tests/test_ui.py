"""Integración SDL dummy; no certifica sonido físico ni revisión manual."""
import os
from pathlib import Path
import unittest
from unittest.mock import patch
import pygame
from engine.game_loop import GameLoop
from engine.game_object import GameObject
from engine.ui import Scene
from game.app import LastValveGame
from game.model import GameState, Unit, Motion
from game.world import GridMap
from game.render import WorldActor


def fresh_state():
    return GameState(GridMap(24, 16), Unit('vera', 'Vera', (2, 3), 30, 30),
                     enemies={'guard': Unit('guard', 'Guardia', (4, 3), 16, 16)})


class UITests(unittest.TestCase):
    def setUp(self):
        self.new = patch('game.app.GameState.new', side_effect=fresh_state)
        self.new.start()
        self.game = LastValveGame(audio_enabled=False)
    def tearDown(self):
        self.new.stop()
        pygame.quit()
    def click(self, point):
        self.game.handle_specific_events(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=point, button=1))
    def test_inheritance_and_initial_menu(self):
        self.assertIsInstance(self.game, GameLoop)
        self.assertIsInstance(self.game.current_scene, Scene)
        self.assertTrue(all(isinstance(scene, Scene) for scene in self.game.scenes.values()))
        self.assertIsNone(self.game.state)
        self.assertTrue(issubclass(WorldActor, GameObject))
    def test_begin_button_starts_fresh_state(self):
        self.click((640, 440))
        self.assertIsNotNone(self.game.state)
        self.assertIs(self.game.current_scene, self.game.scenes['play'])
    def test_new_game_does_not_reuse_mutable_state(self):
        self.game.start_new_game()
        self.assertIsNotNone(self.game.state)
        before = self.game.state
        before.player.hp = 1
        before.medkits = 0
        self.game.start_new_game()
        self.assertIsNot(self.game.state, before)
        self.assertEqual(self.game.state.player.hp, 30)
        self.assertEqual(self.game.state.medkits, 1)
    def test_ui_click_does_not_order_world_movement(self):
        self.game.start_new_game()
        self.assertIsNotNone(self.game.state)
        with patch.object(self.game.state, 'set_destination') as move:
            self.click((1050, 200))
            self.click((100, 780))
        move.assert_not_called()
    def test_terminal_states_change_scene(self):
        for mode in ('victory', 'defeat'):
            self.game.state = fresh_state()
            self.game.state.mode = mode
            self.game.current_scene = self.game.scenes['play']
            self.game.update_game_logic(.02)
            self.assertIs(self.game.current_scene, self.game.scenes[mode])
    def test_keyboard_and_click_use_domain_commands(self):
        self.game.start_new_game()
        self.assertIsNotNone(self.game.state)
        with patch.object(self.game.state, 'move_direction') as move:
            move.return_value.ok = True
            self.game.handle_specific_events(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))
        move.assert_called_once_with((0, -1))
    def test_assets_are_loaded_once_and_draw_is_nonempty(self):
        self.assertIn('human_front', self.game.assets.images)
        self.assertIn('human_rear', self.game.assets.images)
        self.assertIn('pipes', self.game.assets.images)
        self.game.draw_game_elements()
        self.assertNotEqual(self.game.screen.get_at((10, 10))[:3], (0, 0, 0))
    def test_menu_and_play_draw_without_reloading_assets(self):
        with patch.object(self.game.assets, 'load_image') as load:
            self.game.draw_game_elements()
            self.game.start_new_game()
            self.game.draw_game_elements()
        self.assertIsNotNone(self.game.state)
        load.assert_not_called()
    def test_audio_enabled_loads_real_manifest_sounds(self):
        pygame.quit()
        game = LastValveGame(audio_enabled=True)
        self.assertEqual(set(game.assets.sounds), {'click', 'confirm', 'back', 'error'})
        self.assertIsInstance(game.assets.get_sound('confirm'), pygame.mixer.Sound)

    def test_ui_sounds_replace_one_another_without_accumulation(self):
        pygame.quit()
        game = LastValveGame(audio_enabled=True)
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(640, 440), button=1)
        game.handle_specific_events(event)
        busy = sum(pygame.mixer.Channel(index).get_busy() for index in range(pygame.mixer.get_num_channels()))
        self.assertEqual(busy, 1)

    def test_actor_interpolation_does_not_mutate_logical_cell(self):
        self.game.start_new_game()
        state = self.game.state
        start = state.player.cell
        end = (start[0] + 1, start[1])
        state.motions[state.player.id] = Motion(start, end, elapsed=.07, duration=.14)
        self.game.draw_game_elements()
        renderer = self.game.scenes['play'].renderer
        actor = renderer.actors[state.player.id]
        self.assertIsInstance(actor, GameObject)
        self.assertEqual(state.player.cell, start)
        self.assertEqual(actor.foot, renderer.projection.center((start[0] + .5, start[1])))

if __name__ == '__main__':
    unittest.main()
