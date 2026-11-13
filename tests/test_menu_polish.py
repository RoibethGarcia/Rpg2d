"""Menú: navegación con teclado, selección, emblema vivo, entrada escalonada y «Cómo jugar»."""
import unittest
from unittest.mock import patch
import pygame
from game.app import LastValveGame
from game.config import BASIC_COST, BASIC_DAMAGE, HEAL_AMOUNT, POWER_COST, POWER_DAMAGE
from game.howto import HOW_TO_PLAY
from game.menu_nav import MenuSelection, reveal
from game.scenes import emblem


def key(code):
    return pygame.event.Event(pygame.KEYDOWN, key=code)


class MenuSelectionTests(unittest.TestCase):
    def test_move_wraps_in_both_directions(self):
        sel = MenuSelection(4)
        sel.move(-1)
        self.assertEqual(sel.index, 3)
        sel.move(1)
        self.assertEqual(sel.index, 0)
        sel.move(1)
        self.assertEqual(sel.index, 1)

    def test_set_accepts_valid_index_and_ignores_invalid(self):
        sel = MenuSelection(4)
        sel.set(2)
        self.assertEqual(sel.index, 2)
        sel.set(9)
        sel.set(-1)
        self.assertEqual(sel.index, 2)

    def test_reveal_is_clamped_and_monotonic(self):
        self.assertEqual(reveal(0.0, .5, .4), 0.0)
        self.assertEqual(reveal(.5, .5, .4), 0.0)
        self.assertEqual(reveal(2.0, .5, .4), 1.0)
        values = [reveal(t / 20, .5, .4) for t in range(0, 30)]
        self.assertEqual(values, sorted(values))
        self.assertTrue(0 < reveal(.7, .5, .4) < 1)


class MenuSceneTests(unittest.TestCase):
    def setUp(self):
        self.game = LastValveGame(audio_enabled=False)
        self.menu = self.game.scenes['menu']

    def tearDown(self):
        pygame.quit()

    def send(self, event):
        self.game.handle_specific_events(event)

    def test_button_order_and_begin_position(self):
        self.assertEqual([b.text for b in self.menu.buttons],
                         ['Comenzar', 'Cómo jugar', 'Opciones', 'Salir'])
        self.assertTrue(self.menu.buttons[0].rect.collidepoint(640, 440))

    def test_arrows_and_enter_open_the_selected_entry(self):
        self.send(key(pygame.K_DOWN))
        self.send(key(pygame.K_RETURN))
        self.assertIs(self.game.current_scene, self.game.scenes['howto'])
        self.assertIsNone(self.game.state)

    def test_up_from_first_wraps_to_quit(self):
        pygame.quit()
        with patch.object(LastValveGame, 'stop') as stop:  # El botón captura stop al crearse.
            self.game = LastValveGame(audio_enabled=False)
            self.game.handle_specific_events(key(pygame.K_UP))
            self.game.handle_specific_events(key(pygame.K_RETURN))
        stop.assert_called_once()

    def test_enter_still_begins_by_default(self):
        self.send(key(pygame.K_RETURN))
        self.assertIs(self.game.current_scene, self.game.scenes['play'])

    def test_mouse_motion_moves_selection(self):
        target = self.menu.buttons[2].rect.center
        self.send(pygame.event.Event(pygame.MOUSEMOTION, pos=target, rel=(0, 0), buttons=(0, 0, 0)))
        self.assertEqual(self.menu.selection.index, 2)

    def test_entering_menu_again_resets_selection_but_returning_from_howto_keeps_it(self):
        self.menu.selection.set(1)
        self.game.change_scene('howto')
        self.game.change_scene('menu')
        self.assertEqual(self.menu.selection.index, 1)
        self.game.start_new_game()
        self.game.change_scene('menu')
        self.assertEqual(self.menu.selection.index, 0)

    def test_emblem_turns_with_time_and_resets_on_enter(self):
        self.menu.update(1.0)
        self.assertGreater(self.menu.angle, 0)
        self.menu.on_enter()
        self.assertEqual(self.menu.angle, 0)

    def test_emblem_draws_differently_at_another_angle(self):
        a, b = pygame.Surface((200, 200)), pygame.Surface((200, 200))
        emblem(a, (100, 100), 60, angle=0)
        emblem(b, (100, 100), 60, angle=30)
        self.assertNotEqual(pygame.image.tobytes(a, 'RGB'), pygame.image.tobytes(b, 'RGB'))

    def test_elements_appear_in_sequence_without_blocking_input(self):
        self.assertEqual(self.menu.reveal_of('buttons'), 0)
        self.assertLess(self.menu.reveal_of('title'), 1)
        self.menu.update(5.0)
        for name in ('emblem', 'title', 'subtitle', 'buttons'):
            self.assertEqual(self.menu.reveal_of(name), 1)
        self.menu.on_enter()
        self.assertEqual(self.menu.reveal_of('buttons'), 0)
        self.send(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(640, 440), button=1))
        self.assertIs(self.game.current_scene, self.game.scenes['play'])

    def test_draw_is_not_blank_in_every_selection_state(self):
        self.menu.update(5.0)
        for index in range(4):
            self.menu.selection.set(index)
            self.menu.draw(self.game.screen)
            self.assertNotEqual(self.game.screen.get_at((640, 322))[:3], (0, 0, 0))


class HowToPlayTests(unittest.TestCase):
    def setUp(self):
        self.game = LastValveGame(audio_enabled=False)

    def tearDown(self):
        pygame.quit()

    def open(self):
        button = next(b for b in self.game.scenes['menu'].buttons if b.text == 'Cómo jugar')
        self.game.handle_specific_events(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, pos=button.rect.center, button=1))

    def test_content_uses_real_rule_numbers_and_covers_the_hard_parts(self):
        text = ' '.join(HOW_TO_PLAY.values() if isinstance(HOW_TO_PLAY, dict) else
                        (line for _, line in HOW_TO_PLAY))
        for needle in (f'{BASIC_COST} PA', f'{POWER_COST} PA', f'daño {BASIC_DAMAGE}',
                       f'daño {POWER_DAMAGE}', f'{HEAL_AMOUNT}', 'Botiquín', 'jefe',
                       'Mantenimiento', 'válvula', 'Espacio', 'WASD'):
            self.assertIn(needle, text)
        self.assertNotIn('panel', text)

    def test_opens_from_menu_without_starting_a_game(self):
        self.open()
        self.assertIs(self.game.current_scene, self.game.scenes['howto'])
        self.assertIsNone(self.game.state)

    def test_escape_and_back_button_return_to_menu(self):
        self.open()
        self.game.handle_specific_events(key(pygame.K_ESCAPE))
        self.assertIs(self.game.current_scene, self.game.scenes['menu'])
        self.open()
        back = next(b for b in self.game.current_scene.buttons if b.text == 'Volver al menú')
        self.game.handle_specific_events(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, pos=back.rect.center, button=1))
        self.assertIs(self.game.current_scene, self.game.scenes['menu'])

    def test_enter_does_not_start_a_game_here(self):
        self.open()
        self.game.handle_specific_events(key(pygame.K_RETURN))
        self.assertIsNone(self.game.state)

    def test_draw_paints_the_screen(self):
        self.open()
        self.game.update_game_logic(1)
        self.game.draw_game_elements()
        self.assertNotEqual(self.game.screen.get_at((10, 10))[:3], (0, 0, 0))


if __name__ == '__main__':
    unittest.main()
