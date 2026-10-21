"""Agotar PA cede el turno una vez; ganar el combate tiene prioridad."""
import unittest

from game.config import ENEMY_ACTION_DELAY, TURN_AP
from game.model import GameState, Unit
from game.world import GridMap


def combat():
    state = GameState(GridMap(10, 8), Unit('vera', 'Vera', (2, 2), 30, 30),
                      {'guard': Unit('guard', 'Guardia', (3, 2), 20, 20)})
    state.move_direction((1, 0))
    return state


class AutomaticTurnTests(unittest.TestCase):
    def test_last_basic_or_power_attack_starts_enemy_turn_without_update(self):
        for power, cost, damage in ((False, 2, 4), (True, 3, 7)):
            with self.subTest(power=power):
                state = combat()
                state.player.ap = cost
                state.enemies['guard'].ap = 0
                result = state.attack(power)
                self.assertTrue(result)
                self.assertEqual((state.turn, state.player.ap, state.player.hp), ('enemy', 0, 30))
                self.assertEqual((state.enemies['guard'].hp, state.enemies['guard'].ap),
                                 (20 - damage, TURN_AP))
                self.assertEqual(state._enemy_wait, ENEMY_ACTION_DELAY)
                self.assertIn('Turno de La Custodia', result.message)
                state.update(.1)
                wait = state._enemy_wait
                self.assertFalse(state.end_turn())
                self.assertEqual(state._enemy_wait, wait)  # No reinicia el turno.

    def test_last_medkit_heals_and_starts_enemy_turn(self):
        state = combat()
        state.player.ap = 2
        state.player.hp = 10
        result = state.heal()
        self.assertTrue(result)
        self.assertEqual((state.turn, state.player.ap, state.player.hp, state.medkits),
                         ('enemy', 0, 18, 0))
        self.assertIn('Turno de La Custodia', result.message)

    def test_last_step_finishes_before_turn_and_discards_pending_direction(self):
        state = combat()
        state.player.ap = 1
        self.assertTrue(state.move_direction((0, 1)))
        self.assertTrue(state.move_direction((0, 1)))
        state.update(.12)
        self.assertEqual((state.turn, state.player.ap, state.player.cell), ('player', 1, (2, 2)))
        self.assertIn('vera', state.motions)
        state.update(.02)
        self.assertEqual((state.turn, state.player.ap, state.player.cell), ('enemy', 0, (2, 3)))
        self.assertFalse(state.motions or state.route)
        self.assertIsNone(state._pending_direction)
        state.update(3)
        self.assertEqual((state.turn, state.player.ap, state.player.cell), ('player', TURN_AP, (2, 3)))
        self.assertFalse(state.motions or state.route)

    def test_click_route_discards_over_budget_steps_and_never_resumes(self):
        state = combat()
        state.player.ap = 2
        self.assertTrue(state.set_destination((2, 7)))
        state.update(.28)
        self.assertEqual((state.turn, state.player.ap, state.player.cell), ('enemy', 0, (2, 4)))
        self.assertFalse(state.route or state.motions)
        state.update(3)
        self.assertEqual((state.turn, state.player.ap, state.player.cell), ('player', TURN_AP, (2, 4)))
        self.assertFalse(state.route or state.motions)

    def test_cancelled_route_still_finishes_last_paid_step_and_turn(self):
        state = combat()
        state.player.ap = 1
        self.assertTrue(state.set_destination((2, 7)))
        self.assertTrue(state.cancel_route())
        state.update(.14)
        self.assertEqual((state.turn, state.player.ap, state.player.cell), ('enemy', 0, (2, 3)))
        self.assertFalse(state.route or state.motions)

    def test_invalid_actions_do_not_consume_or_change_turn(self):
        for ap in (0, 1):
            with self.subTest(ap=ap):
                state = combat()
                state.player.ap = ap
                state.player.hp = 20
                state.grid.blocked.add((2, 3))
                for action in (state.attack, lambda: state.attack(True), state.heal,
                               lambda: state.move_direction((0, 1)),
                               lambda: state.set_destination((2, 3))):
                    self.assertFalse(action())
                    self.assertEqual((state.turn, state.player.ap, state.player.hp,
                                      state.medkits, state.enemies['guard'].hp),
                                     ('player', ap, 20, 1, 20))

    def test_remaining_pa_keeps_player_turn_and_manual_end_is_available(self):
        state = combat()
        self.assertTrue(state.attack())
        self.assertEqual((state.turn, state.player.ap), ('player', 4))
        self.assertTrue(state.end_turn())
        self.assertEqual(state.turn, 'enemy')

    def test_winning_last_attack_keeps_exploration_and_credential_priority(self):
        for boss in (False, True):
            with self.subTest(boss=boss):
                state = combat()
                state.player.ap = 2
                state.enemies['guard'].hp = 4
                state.enemies['guard'].ap = 0
                state.enemies['guard'].boss = boss
                self.assertTrue(state.attack())
                self.assertEqual((state.mode, state.turn, state.player.ap), ('exploration', 'player', 0))
                self.assertEqual(state.credential, boss)
                self.assertIsNone(state.active_enemy_id)
                self.assertEqual(state.enemies['guard'].ap, 0)
                state.update(3)
                self.assertEqual((state.player.hp, state.mode, state.turn), (30, 'exploration', 'player'))

    def test_exploration_does_not_spend_pa_or_start_enemy_turn(self):
        state = combat()
        state.mode = 'exploration'
        state.active_enemy_id = None
        state.player.ap = 0
        self.assertTrue(state.move_direction((0, 1)))
        state.update(.14)
        self.assertEqual((state.mode, state.turn, state.player.ap, state.player.cell),
                         ('exploration', 'player', 0, (2, 3)))

    def test_automatic_enemy_turn_can_defeat_vera(self):
        state = combat()
        state.player.hp = 3
        state.player.ap = 2
        self.assertTrue(state.attack())
        state.update(3)
        self.assertEqual((state.mode, state.player.hp), ('defeat', 0))
        self.assertFalse(state.motions or state.route)
        self.assertFalse(state.heal())

    def test_dt_chunking_preserves_automatic_turn_sequence(self):
        a, b = combat(), combat()
        for state in (a, b):
            state.player.ap = 1
            self.assertTrue(state.move_direction((0, 1)))
        a.update(1.5)
        for _ in range(75):
            b.update(.02)
        self.assertEqual((a.turn, a.player.ap, a.player.hp, a.player.cell, a.enemies, a.motions),
                         (b.turn, b.player.ap, b.player.hp, b.player.cell, b.enemies, b.motions))
        self.assertAlmostEqual(a._enemy_wait, b._enemy_wait)

