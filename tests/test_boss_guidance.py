"""Jefe de la planta: ganable con 1 botiquín, ayuda clara y vocabulario unificado."""
import unittest
from game.guidance import combat_hint, objective
from game.model import GameState, Unit
from game.world import GridMap


def boss_duel(hp=48, ap=6):
    state = GameState(GridMap(24, 16), Unit('vera', 'Vera', (2, 3), 30, 30),
                      enemies={'boss': Unit('boss', 'Jefe', (3, 3), hp, 48, damage=3, boss=True)})
    state.mode, state.turn, state.player.ap = 'combat', 'player', ap
    state.active_enemy_id = 'boss'
    return state


class BossBalanceTests(unittest.TestCase):
    def test_planta_boss_hits_for_four_and_keeps_42_hp(self):
        boss = GameState.new().maps['planta'].enemies['boss']
        self.assertEqual((boss.hp, boss.damage), (42, 4))

    def test_other_enemies_keep_their_damage(self):
        enemies = GameState.new().maps['planta'].enemies
        self.assertEqual([e.damage for e in enemies.values() if not e.boss], [3, 3, 3])


class BossGuidanceTests(unittest.TestCase):
    def test_power_attack_is_recommended_as_more_efficient(self):
        self.assertIn('rinde más', combat_hint(boss_duel()))

    def test_boss_hint_estimates_turns_with_power_attacks(self):
        self.assertIn('4 turnos', combat_hint(boss_duel(hp=48)))
        self.assertIn('1 turno', combat_hint(boss_duel(hp=14)))

    def test_regular_guard_has_no_turn_estimate(self):
        state = boss_duel()
        state.enemies['boss'].boss = False
        self.assertNotIn('turno', combat_hint(state))

    def test_planta_objective_is_two_steps(self):
        state = GameState.new()
        state.map_id = 'planta'
        self.assertIn('Derrota al jefe', objective(state))
        state.credential = True
        self.assertIn('válvula', objective(state))

    def test_boss_defeat_message_says_valve_not_panel(self):
        state = boss_duel(hp=7)
        result = state.attack(power=True)
        self.assertTrue(result.ok)
        self.assertIn('válvula', state.message)
        self.assertNotIn('panel', state.message)


if __name__ == '__main__':
    unittest.main()
