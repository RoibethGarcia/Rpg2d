"""Independent adversarial domain checks, separate from subsystem tests."""
import unittest
from game.model import GameState, Unit
from game.content import new_legacy_game
from game.world import GridMap, Projection


def scenario(enemy_cell=(5, 2)):
    return GameState(GridMap(10, 8), Unit('vera', 'Vera', (2, 2), 30, 30),
                     {'guard': Unit('guard', 'Guardia', enemy_cell, 16, 16)})


class ContactRegressionTests(unittest.TestCase):
    def test_contact_mid_tick_cancels_other_motion_without_stale_commit_or_crash(self):
        state = scenario()
        state.enemies['patrol'] = Unit('patrol', 'Patrulla', (7, 5), 16, 16)
        state.patrols['patrol'] = {'cells': [(7, 5), (7, 4)], 'pause': .14}
        self.assertTrue(state.set_destination((5, 2)))
        state.update(.14)
        self.assertEqual(state.player.cell, (3, 2))
        self.assertEqual(set(state.motions), {'vera', 'patrol'})
        state.update(.14)
        self.assertEqual(state.mode, 'combat')
        self.assertEqual(state.player.cell, (4, 2))
        self.assertEqual(state.enemies['guard'].cell, (5, 2))
        self.assertEqual(state.enemies['patrol'].cell, (7, 5))
        self.assertFalse(state.motions)
        self.assertFalse(state.route)
        self.assertEqual((state.player.hp, state.player.ap), (30, 6))
        self.assertEqual(state.enemies['guard'].hp, 16)


class WorldRegressionTests(unittest.TestCase):
    def test_projection_centers_and_negative_boundaries_with_shifted_camera(self):
        projection = Projection(64, 32, (-173, 91), (241, -87))
        for col in range(-4, 25):
            for row in range(-4, 17):
                with self.subTest(col=col, row=row):
                    self.assertEqual(projection.pick(*projection.center((col, row))), (col, row))
                    self.assertEqual(projection.inverse(*projection.project(col, row)), (col, row))
        self.assertEqual(projection.pick(*projection.project(-.001, -.001)), (-1, -1))

    def test_invalid_bfs_endpoints_and_occupied_chokepoint(self):
        grid = GridMap(3, 3, {(0, 1), (2, 1)})
        self.assertEqual(grid.find_path((1, 0), (1, 2), {(1, 1)}), [])
        self.assertEqual(grid.find_path((-1, 0), (1, 2)), [])
        self.assertEqual(grid.find_path((1, 0), (3, 2)), [])
        self.assertEqual(grid.find_path((1, 0), (1, 2)), [(1, 1), (1, 2)])


class StateRegressionTests(unittest.TestCase):
    def combat(self):
        state = scenario((3, 2))
        self.assertTrue(state.move_direction((1, 0)))
        self.assertEqual(state.mode, 'combat')
        return state

    def test_patrol_contact_keeps_both_cells_and_pauses_other_patrols(self):
        state = scenario((3, 2))
        state.enemies['other'] = Unit('other', 'Otra', (7, 5), 16, 16)
        state.patrols = {
            'guard': {'cells': [(3, 2), (2, 2)], 'pause': .02},
            'other': {'cells': [(7, 5), (7, 4)], 'pause': .02},
        }
        state.update(.02)
        self.assertEqual((state.mode, state.active_enemy_id, state.turn), ('combat', 'guard', 'player'))
        self.assertEqual((state.player.cell, state.enemies['guard'].cell), ((2, 2), (3, 2)))
        self.assertFalse(state.motions or state.route)
        state.update(2)
        self.assertEqual(state.enemies['other'].cell, (7, 5))
        self.assertEqual((state.player.hp, state.enemies['guard'].hp), (30, 16))

    def test_reservation_prevents_patrol_stealing_destination(self):
        state = scenario((3, 3))
        state.patrols = {'guard': {'cells': [(3, 3), (3, 2)], 'pause': .02}}
        self.assertTrue(state.move_direction((1, 0)))
        self.assertIn((3, 2), state.occupied())
        state.update(.02)
        self.assertEqual(state.enemies['guard'].cell, (3, 3))
        self.assertNotIn('guard', state.motions)
        self.assertEqual(state.mode, 'exploration')

    def test_no_automatic_turn_after_last_ap_and_only_completed_step_costs(self):
        state = self.combat()
        state.player.ap = 1
        self.assertTrue(state.move_direction((-1, 0)))
        self.assertEqual((state.player.ap, state.player.cell), (1, (2, 2)))
        state.update(.12)
        self.assertEqual(state.player.ap, 1)
        state.update(.02)
        self.assertEqual((state.player.ap, state.player.cell), (0, (1, 2)))
        state.update(3)
        self.assertEqual((state.turn, state.player.hp, state.player.ap), ('player', 30, 0))
        self.assertFalse(state.move_direction((0, 1)))

    def test_invalid_attacks_and_heals_are_atomic(self):
        state = self.combat()
        state.player.hp = 20
        state.player.ap = 1
        before = (state.player.hp, state.player.ap, state.enemies['guard'].hp, state.medkits)
        for action in (state.attack, lambda: state.attack(True), state.heal):
            self.assertFalse(action())
            self.assertEqual((state.player.hp, state.player.ap, state.enemies['guard'].hp, state.medkits), before)
        state.player.ap = 6
        state.player.hp = 30
        self.assertFalse(state.heal())
        self.assertEqual((state.player.hp, state.player.ap, state.medkits), (30, 6, 1))
        state.player.hp = 29
        self.assertTrue(state.heal())
        self.assertEqual((state.player.hp, state.player.ap, state.medkits), (30, 4, 0))

    def test_terminal_commands_and_updates_never_change_gameplay(self):
        for mode in ('victory', 'defeat'):
            state = scenario()
            state.mode = mode
            baseline = (state.player.cell, state.player.hp, state.player.ap, state.medkits,
                        state.enemies['guard'].cell, state.enemies['guard'].hp, state.turn)
            for action in (state.attack, state.heal, state.interact, state.end_turn,
                           state.cancel_route, lambda: state.move_direction((1, 0)),
                           lambda: state.set_destination((2, 3))):
                self.assertFalse(action())
            state.update(3)
            self.assertEqual((state.player.cell, state.player.hp, state.player.ap, state.medkits,
                              state.enemies['guard'].cell, state.enemies['guard'].hp, state.turn), baseline)
            self.assertFalse(state.motions or state.route)

    def test_victory_requires_neighbor_not_standing_on_panel(self):
        state = scenario()
        state.objects = [dict(id='panel', kind='panel', cell=(2, 2), text='Agua')]
        state.credential = True
        self.assertFalse(state.interact())
        self.assertEqual(state.mode, 'exploration')
        self.assertTrue(state.move_direction((0, 1)))
        state.update(.14)
        self.assertTrue(state.interact())
        self.assertEqual(state.mode, 'victory')

    def test_reset_does_not_share_nested_patrol_objects_or_pending_state(self):
        first, other = new_legacy_game(), new_legacy_game()
        first.patrols['guard1']['cells'][0][0] = 999
        first.objects[0]['cell'] = (99, 99)
        first.player.hp = 1
        first.medkits = 0
        first.credential = True
        first.collected.add('kit1')
        first.opened.add('maintenance')
        self.assertTrue(first.move_direction((-1, 0)))
        self.assertEqual(other.patrols['guard1']['cells'][0], [4, 4])
        self.assertEqual((other.player.hp, other.medkits, other.credential), (30, 1, False))
        self.assertFalse(other.collected or other.opened or other.motions or other.route)
        self.assertEqual(other.objects[0]['cell'], (2, 11))

    def test_dynamic_block_stops_route_without_autorepath_or_extra_cost(self):
        state = self.combat()
        self.assertTrue(state.set_destination((2, 5)))
        state.grid.blocked.add((2, 4))
        state.update(1)
        self.assertEqual((state.player.cell, state.player.ap), ((2, 3), 5))
        self.assertFalse(state.motions or state.route)

    def test_dt_chunking_preserves_deterministic_movement_and_cost(self):
        a, b = self.combat(), self.combat()
        self.assertTrue(a.set_destination((2, 5)))
        self.assertTrue(b.set_destination((2, 5)))
        a.update(.42)
        for _ in range(21):
            b.update(.02)
        self.assertEqual((a.player.cell, a.player.ap, a.turn, a.route),
                         (b.player.cell, b.player.ap, b.turn, b.route))
        self.assertFalse(a.motions or b.motions)


if __name__ == '__main__':
    unittest.main()
