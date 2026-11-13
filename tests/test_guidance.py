"""Ayuda contextual: objetivo según mapa/estado y pista de combate."""
import unittest
from game.guidance import combat_hint, objective
from game.model import GameState, Unit
from game.world import GridMap


def duel(player=(2, 3), enemy=(3, 3), ap=6):
    state = GameState(GridMap(24, 16), Unit('vera', 'Vera', player, 30, 30),
                      enemies={'guard': Unit('guard', 'Guardia', enemy, 16, 16)})
    state.mode, state.turn, state.player.ap = 'combat', 'player', ap
    return state


class ObjectiveTests(unittest.TestCase):
    def state(self, map_id):
        state = GameState.new()
        state.map_id = map_id
        return state

    def test_puesto_points_to_maintenance_until_opened(self):
        state = self.state('puesto')
        self.assertIn('Mantenimiento', objective(state))
        self.assertNotIn('credencial', objective(state))
        state.opened.add('maintenance')
        self.assertIn('Planta de distribución', objective(state))

    def test_planta_asks_for_credential_then_valve(self):
        state = self.state('planta')
        self.assertIn('credencial', objective(state))
        state.credential = True
        self.assertIn('válvula', objective(state))

    def test_valve_objective_says_to_stand_next_to_it(self):
        state = GameState.new()
        state.map_id, state.credential = 'planta', True
        self.assertIn('Acércate', objective(state))
        self.assertIn('E', objective(state))

    def test_hondonada_points_to_puesto(self):
        self.assertIn('Puesto', objective(self.state('hondonada')))


class CombatHintTests(unittest.TestCase):
    def test_adjacent_enemy_lists_both_attacks(self):
        hint = combat_hint(duel())
        self.assertIn('Llave', hint)
        self.assertIn('Potente', hint)

    def test_two_ap_only_allows_basic_attack(self):
        hint = combat_hint(duel(ap=2))
        self.assertIn('Llave', hint)
        self.assertNotIn('Potente', hint)

    def test_far_enemy_says_to_get_closer(self):
        hint = combat_hint(duel(enemy=(8, 3)))
        self.assertIn('Acércate', hint)
        self.assertIn('1 PA', hint)

    def test_not_enough_ap_suggests_ending_turn(self):
        self.assertIn('Espacio', combat_hint(duel(ap=1)))

    def test_enemy_turn_says_wait(self):
        state = duel()
        state.turn = 'enemy'
        self.assertIn('enemigo', combat_hint(state).lower())

    def test_hint_does_not_mutate_state(self):
        state = duel()
        before = (state.player.ap, state.player.cell, state.enemies['guard'].hp, state.message)
        combat_hint(state)
        self.assertEqual(before, (state.player.ap, state.player.cell, state.enemies['guard'].hp, state.message))


if __name__ == '__main__':
    unittest.main()
