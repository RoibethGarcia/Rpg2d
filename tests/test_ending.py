"""Pantalla de cierre del primer nivel: flujo, aparición y entrada protegida."""
import unittest
import pygame
from game.app import LastValveGame


def key(code):
    return pygame.event.Event(pygame.KEYDOWN, key=code)


class EndingTests(unittest.TestCase):
    def setUp(self):
        self.game = LastValveGame(audio_enabled=False)
        self.game.start_new_game()
        self.game.state.mode = 'victory'
        self.game.update_game_logic(0)
        self.ending = self.game.scenes['ending']

    def tearDown(self):
        pygame.quit()

    def send(self, event):
        self.game.handle_specific_events(event)

    def click(self, button):
        self.send(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=button.rect.center, button=1))

    def test_victory_goes_to_ending_first(self):
        self.assertIs(self.game.current_scene, self.ending)
        self.assertEqual([b.text for b in self.ending.buttons], ['Ver créditos', 'Volver al menú'])
        self.assertTrue(self.ending.title.startswith('FIN DEL PRIMER NIVEL'))
        self.assertIn('más niveles', self.ending.note.lower())
        self.assertIn('prueba', self.ending.note.lower())

    def test_elements_appear_in_order_and_buttons_come_last(self):
        self.assertEqual(self.ending.reveal_of('buttons'), 0)
        self.ending.update(1.2)
        self.assertGreater(self.ending.reveal_of('title'), 0)
        self.assertEqual(self.ending.reveal_of('buttons'), 0)
        self.ending.update(5)
        for name in self.ending.REVEALS:
            self.assertEqual(self.ending.reveal_of(name), 1)

    def test_first_input_skips_the_animation_instead_of_leaving(self):
        self.send(key(pygame.K_RETURN))
        self.assertIs(self.game.current_scene, self.ending)
        self.assertEqual(self.ending.elapsed, self.ending.READY)
        self.send(key(pygame.K_RETURN))
        self.assertIs(self.game.current_scene, self.game.scenes['victory'])

    def test_early_click_on_hidden_buttons_does_not_navigate(self):
        self.click(self.ending.buttons[1])
        self.assertIs(self.game.current_scene, self.ending)

    def test_buttons_work_once_visible(self):
        self.ending.update(5)
        self.click(self.ending.buttons[0])
        self.assertIs(self.game.current_scene, self.game.scenes['victory'])
        self.game.change_scene('ending')
        self.ending.update(5)
        self.click(self.ending.buttons[1])
        self.assertIs(self.game.current_scene, self.game.scenes['menu'])

    def test_keyboard_selection_picks_the_second_button(self):
        self.ending.update(5)
        self.send(key(pygame.K_DOWN))
        self.send(key(pygame.K_RETURN))
        self.assertIs(self.game.current_scene, self.game.scenes['menu'])

    def test_escape_returns_to_menu(self):
        self.send(key(pygame.K_ESCAPE))
        self.assertIs(self.game.current_scene, self.game.scenes['menu'])

    def test_entering_again_restarts_the_sequence(self):
        self.ending.update(5)
        self.game.change_scene('victory')
        self.game.change_scene('ending')
        self.assertEqual(self.ending.elapsed, 0)

    def test_gameplay_stays_frozen_and_state_is_kept(self):
        state = self.game.state
        before = (state.player.cell, state.player.hp, state.mode)
        self.send(key(pygame.K_w))
        self.game.update_game_logic(1)
        self.assertEqual((state.player.cell, state.player.hp, state.mode), before)
        self.assertIs(self.game.state, state)

    def test_draw_is_not_blank_at_every_stage_and_without_state(self):
        for seconds in (0.1, 1.5, 3.0, 6.0):
            self.ending.elapsed = seconds
            self.ending.draw(self.game.screen)
            self.assertNotEqual(self.game.screen.get_at((640, 300))[:3], (0, 0, 0))
        self.game.state = None
        self.ending.draw(self.game.screen)

    def test_credits_scene_no_longer_overlays_text_on_its_bands(self):
        self.assertFalse(hasattr(self.game.scenes['victory'], 'TOP_LINE'))


if __name__ == '__main__':
    unittest.main()
