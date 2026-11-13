"""Claridad de combate: botiquín, clic para atacar y números flotantes."""
import unittest
from unittest.mock import patch
import pygame
from game.app import LastValveGame
from game.guidance import combat_hint, end_turn_advised, medkit_status
from game.model import GameState, Unit
from game.world import GridMap


def duel(enemy=(3, 3), ap=6, hp=20, medkits=3):
    state = GameState(GridMap(24, 16), Unit('vera', 'Vera', (2, 3), hp, 30),
                      enemies={'guard': Unit('guard', 'Guardia', enemy, 16, 16)})
    state.mode, state.turn, state.player.ap = 'combat', 'player', ap
    state.active_enemy_id, state.medkits = 'guard', medkits
    return state


class MedkitStatusTests(unittest.TestCase):
    def test_usable_shows_count_cost_and_amount(self):
        text, usable = medkit_status(duel())
        self.assertTrue(usable)
        self.assertIn('×3', text)
        self.assertIn('2 PA', text)
        self.assertIn('+8', text)

    def test_blocked_reasons_are_visible_on_the_button(self):
        cases = ((duel(medkits=0), '×0', 'sin'), (duel(hp=30), '×3', 'vida llena'),
                 (duel(ap=1), '×3', 'PA'))
        for state, count, reason in cases:
            text, usable = medkit_status(state)
            self.assertFalse(usable)
            self.assertIn(count, text)
            self.assertIn(reason, text)

    def test_outside_combat_it_says_so(self):
        state = duel()
        state.mode = 'exploration'
        text, usable = medkit_status(state)
        self.assertFalse(usable)
        self.assertIn('×3', text)
        self.assertIn('combate', text)


class SceneFeedbackTests(unittest.TestCase):
    def setUp(self):
        self.new = patch('game.app.GameState.new', side_effect=duel)
        self.new.start()
        self.game = LastValveGame(audio_enabled=False)
        self.game.start_new_game()
        self.state = self.game.state
        self.scene = self.game.scenes['play']
        self.renderer = self.scene.renderer

    def tearDown(self):
        self.new.stop()
        pygame.quit()

    def click_cell(self, cell):
        with patch.object(self.renderer, 'pick', return_value=cell):
            self.game.handle_specific_events(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(500, 300), button=1))

    def test_click_on_adjacent_enemy_does_basic_attack(self):
        self.click_cell((3, 3))
        enemy = self.state.enemies['guard']
        self.assertEqual((enemy.hp, self.state.player.ap), (12, 4))

    def test_click_on_far_enemy_explains_and_does_not_attack(self):
        self.state.enemies['guard'].cell = (8, 3)
        self.click_cell((8, 3))
        self.assertEqual((self.state.enemies['guard'].hp, self.state.player.ap), (16, 6))
        self.assertIn('vecina', self.state.message)

    def test_medkit_button_text_follows_state_when_drawn(self):
        self.game.draw_game_elements()
        button = self.scene.buttons[2]
        self.assertIn('×3', button.text)
        self.state.medkits = 0
        self.game.draw_game_elements()
        self.assertIn('×0', button.text)

    def test_attack_event_carries_applied_damage(self):
        self.state.attack()
        self.state.attack(power=True)
        self.assertEqual([e.damage for e in self.state.drain_attack_events()], [4, 7])

    def test_enemy_attack_event_carries_enemy_damage(self):
        self.state.end_turn()
        self.state.update(2)
        hits = [e for e in self.state.drain_attack_events() if e.attacker_id == 'guard']
        self.assertTrue(hits)
        self.assertEqual(hits[0].damage, 3)

    def test_floating_numbers_appear_and_expire(self):
        self.scene.command('attack')
        self.assertEqual([f['text'] for f in self.renderer.floaters], ['-4'])
        self.game.draw_game_elements()
        self.assertEqual(len(self.renderer.floaters), 1)
        self.state._simulation_time += 5
        self.game.draw_game_elements()
        self.assertEqual(self.renderer.floaters, [])

    def test_heal_shows_recovered_amount(self):
        self.scene.command('heal')
        self.assertEqual([f['text'] for f in self.renderer.floaters], ['+8'])

    def test_failed_actions_show_no_floater(self):
        self.state.enemies['guard'].cell = (8, 3)
        self.scene.command('attack')
        self.assertEqual(self.renderer.floaters, [])

    def test_end_turn_button_is_highlighted_only_when_advised(self):
        button = self.scene.buttons[3]
        self.game.draw_game_elements()
        normal = button.color
        self.state.player.ap = 1
        self.game.draw_game_elements()
        self.assertNotEqual(button.color, normal)
        self.state.player.ap = 6
        self.game.draw_game_elements()
        self.assertEqual(button.color, normal)


class LeftoverApTests(unittest.TestCase):
    def test_one_ap_left_advises_ending_turn_with_clear_message(self):
        for enemy in ((3, 3), (8, 3)):  # vecino y lejos
            state = duel(enemy=enemy, ap=1)
            self.assertTrue(end_turn_advised(state))
            hint = combat_hint(state)
            self.assertIn('1 PA', hint)
            self.assertIn('paso', hint)
            self.assertIn('Espacio', hint)
        # Con el enemigo pegado, retroceder lo obliga a gastar PA en alcanzarte.
        self.assertIn('atrás', combat_hint(duel(ap=1)))

    def test_no_advice_when_an_action_is_still_affordable_or_not_your_turn(self):
        self.assertFalse(end_turn_advised(duel(ap=2)))
        self.assertFalse(end_turn_advised(duel(ap=6)))
        state = duel(ap=1)
        state.turn = 'enemy'
        self.assertFalse(end_turn_advised(state))
        state.turn, state.mode = 'player', 'exploration'
        self.assertFalse(end_turn_advised(state))


if __name__ == '__main__':
    unittest.main()
