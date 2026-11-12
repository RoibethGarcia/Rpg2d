"""Menú con fondo animado. SDL dummy: no certifica cómo se ve ni suena."""
import json
from pathlib import Path
import unittest

import pygame

from game.app import LastValveGame
from game.render import BG

ROOT = Path(__file__).resolve().parents[1]


class MenuBackdropTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = LastValveGame(audio_enabled=False)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.menu = self.game.scenes['menu']
        self.menu.on_enter()

    def frame(self):
        self.menu.draw(self.game.screen)
        return self.game.screen.copy()

    def test_menu_shows_a_painted_backdrop_instead_of_a_flat_fill(self):
        self.menu.update(2)  # fade completo
        image = self.frame()
        colors = {tuple(image.get_at((x, 760))[:3]) for x in range(0, 1280, 8)}
        self.assertGreater(len(colors), 20)
        flat = sum(image.get_at((x, y))[:3] == BG[:3]
                   for x in range(0, 1280, 20) for y in range(0, 800, 20))
        self.assertLess(flat, 200, 'el menú sigue siendo casi todo un color plano')

    def test_water_birds_and_smoke_move_while_the_menu_is_open(self):
        self.menu.update(2)
        before = self.frame()
        self.game.update_game_logic(.4)
        after = self.frame()
        changed = sum(before.get_at((x, y)) != after.get_at((x, y))
                      for x in range(0, 1280, 4) for y in range(0, 800, 4))
        self.assertGreater(changed, 40)

    def test_fade_in_restarts_every_time_the_menu_is_entered(self):
        self.assertEqual(self.menu.fade, 0)
        self.menu.update(.2)
        self.assertTrue(0 < self.menu.fade < 1)
        self.menu.update(5)
        self.assertEqual(self.menu.fade, 1)
        self.game.start_new_game()
        self.game.change_scene('menu')
        self.assertEqual(self.menu.fade, 0)

    def test_menu_time_does_not_advance_outside_the_menu(self):
        self.game.start_new_game()
        before = self.menu.backdrop.effects.time
        self.game.update_game_logic(1)
        self.assertEqual(self.menu.backdrop.effects.time, before)
        self.game.change_scene('menu')

    def test_buttons_and_keyboard_still_start_the_game(self):
        labels = [b.text for b in self.menu.buttons]
        self.assertEqual(labels, ['Comenzar', 'Cómo jugar', 'Opciones', 'Salir'])
        self.menu.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)])
        self.assertIsNotNone(self.game.state)
        self.assertIs(self.game.current_scene, self.game.scenes['play'])
        self.game.change_scene('menu')

    def test_menu_data_is_valid_and_inside_the_landscape(self):
        data = json.loads((ROOT / 'data/menu.json').read_text())['ambient']
        self.assertGreater(len(data['river']), 0)
        for zone in data['river']:
            x, y, w, h = zone['rect']
            self.assertTrue(0 <= x and x + w <= 1448 and 0 <= y and y + h <= 1086, zone['rect'])
            self.assertIn(zone['kind'], ('fall', 'ripple'))
            for px, py in zone['polygon']:
                self.assertTrue(x <= px <= x + w and y <= py <= y + h, (zone['rect'], px, py))

    def test_provisional_footer_is_gone(self):
        self.menu.update(2)
        self.assertNotIn('provisional', ' '.join(getattr(self.menu, 'footer_lines', ())).lower())
        self.assertTrue(hasattr(self.menu, 'footer_lines'))


if __name__ == '__main__':
    unittest.main()
