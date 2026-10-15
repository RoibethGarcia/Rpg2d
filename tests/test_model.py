import unittest
from game.model import GameState, Unit
from game.world import GridMap


def fresh(enemy_cell=(4, 2)):
    return GameState(GridMap(9, 7), Unit('vera', 'Vera', (2, 2), 30, 30),
                     {'guard': Unit('guard', 'Guardia', enemy_cell, 16, 16)})


def settle(state):
    for _ in range(100):
        if not state.motions and not state.route:
            return
        state.update(.05)
    raise AssertionError('La ruta no termina')


class ExplorationTests(unittest.TestCase):
    def test_step_reserves_destination_and_commits_only_after_animation(self):
        s = fresh()
        self.assertTrue(s.move_direction((1, 0)))
        self.assertEqual(s.player.cell, (2, 2))
        self.assertEqual(s.motions['vera'].end, (3, 2))
        self.assertFalse(s.attack())
        s.update(.05)
        self.assertEqual(s.player.cell, (2, 2))
        settle(s)
        self.assertEqual(s.player.cell, (3, 2))
        self.assertEqual(s.player.ap, 6)

    def test_contact_does_not_move_or_attack_and_requires_new_order(self):
        s = fresh((3, 2))
        self.assertTrue(s.set_destination((3, 2)))
        self.assertEqual(s.mode, 'combat')
        self.assertEqual(s.player.cell, (2, 2))
        self.assertEqual(s.enemies['guard'].cell, (3, 2))
        self.assertEqual(s.enemies['guard'].hp, 16)
        self.assertEqual(s.player.ap, 6)
        self.assertFalse(s.route)
        s.update(1)
        self.assertEqual(s.enemies['guard'].hp, 16)

    def test_cancel_and_new_direction_finish_current_step(self):
        s = fresh()
        s.set_destination((2, 5))
        self.assertTrue(s.move_direction((-1, 0)))
        settle(s)
        self.assertEqual(s.player.cell, (1, 3))
        s.set_destination((1, 5))
        s.cancel_route()
        settle(s)
        self.assertEqual(s.player.cell, (1, 4))

    def test_dynamic_block_stops_no_repath(self):
        s = fresh()
        s.set_destination((2, 5))
        s.grid.blocked.add((2, 4))
        settle(s)
        self.assertEqual(s.player.cell, (2, 3))
        self.assertFalse(s.route)

    def test_wall_and_outside_reject_without_change(self):
        s = fresh()
        s.grid.blocked.add((2, 1))
        self.assertFalse(s.move_direction((0, -1)))
        self.assertFalse(s.set_destination((-1, 0)))
        self.assertEqual(s.player.cell, (2, 2))
        self.assertFalse(s.motions)


class CombatTests(unittest.TestCase):
    def combat(self):
        s = fresh((3, 2))
        s.move_direction((1, 0))
        return s

    def test_attacks_cost_damage_invalid_and_defeated_enemy_removed(self):
        s = self.combat()
        self.assertTrue(s.attack(power=True))
        self.assertEqual((s.enemies['guard'].hp, s.player.ap), (9, 3))
        self.assertTrue(s.attack(power=True))
        self.assertEqual((s.enemies['guard'].hp, s.player.ap), (2, 0))
        self.assertFalse(s.attack())
        self.assertEqual(s.mode, 'combat')  # Nunca termina turno automáticamente.
        s.end_turn()
        for _ in range(100):
            s.update(.02)
        self.assertEqual((s.turn, s.player.ap, s.player.hp), ('player', 6, 21))
        self.assertTrue(s.attack())
        self.assertEqual(s.mode, 'exploration')
        self.assertEqual(s.enemies['guard'].hp, 0)
        self.assertNotIn((3, 2), s.occupied())
        self.assertEqual(s.player.hp, 21)

    def test_healing_validates_before_mutating_caps_and_consumes(self):
        s = self.combat()
        self.assertFalse(s.heal())
        s.player.hp = 27
        self.assertTrue(s.heal())
        self.assertEqual((s.player.hp, s.player.ap, s.medkits), (30, 4, 0))
        self.assertFalse(s.heal())
        self.assertEqual(s.player.ap, 4)
        s.medkits = 1
        s.player.ap = 1
        s.player.hp = 10
        self.assertFalse(s.heal())
        self.assertEqual((s.player.hp, s.player.ap, s.medkits), (10, 1, 1))

    def test_route_executes_only_budget_no_resume_and_direction_cost_matches(self):
        s = self.combat()
        s.player.ap = 2
        self.assertTrue(s.set_destination((2, 6)))
        settle(s)
        self.assertEqual((s.player.cell, s.player.ap), ((2, 4), 0))
        self.assertFalse(s.route)
        self.assertFalse(s.move_direction((0, 1)))
        self.assertTrue(s.end_turn())
        self.assertFalse(s.attack())
        for _ in range(150):
            s.update(.02)
        self.assertEqual(s.player.cell, (2, 4))
        self.assertEqual(s.player.ap, 6)

    def test_enemy_moves_then_attacks_and_defeat_blocks_commands(self):
        s = self.combat()
        s.move_direction((-1, 0))
        settle(s)
        s.player.hp = 3
        self.assertTrue(s.end_turn())
        for _ in range(100):
            s.update(.02)
        self.assertEqual(s.mode, 'defeat')
        self.assertEqual(s.player.hp, 0)
        for command in [lambda: s.attack(), s.heal, s.end_turn, s.interact,
                        lambda: s.move_direction((1, 0)), lambda: s.set_destination((0, 0))]:
            self.assertFalse(command())
        self.assertFalse(s.motions)

    def test_boss_credential_is_automatic_not_victory(self):
        s = self.combat()
        s.enemies['guard'].boss = True
        s.enemies['guard'].hp = 4
        self.assertTrue(s.attack())
        self.assertTrue(s.credential)
        self.assertEqual(s.mode, 'exploration')


class InteractionTests(unittest.TestCase):
    def test_objects_pickup_once_maintenance_gate_and_panel_requirements(self):
        s = fresh()
        s.grid.blocked.add((3, 3))
        s.objects = [dict(id='kit', kind='medkit', cell=(2, 3), text='Suministros')]
        self.assertTrue(s.interact())
        self.assertEqual(s.medkits, 2)
        self.assertFalse(s.interact())
        s.objects.append(dict(id='gate', kind='maintenance', cell=(2, 3), target=(3, 3), text='Abierto'))
        self.assertTrue(s.interact())
        self.assertTrue(s.grid.walkable((3, 3)))
        s.objects.append(dict(id='panel', kind='panel', cell=(2, 3), text='El agua llegó'))
        self.assertFalse(s.interact())
        s.credential = True
        self.assertTrue(s.interact())
        self.assertEqual(s.mode, 'victory')

    def test_no_interactions_during_combat(self):
        s = fresh((3, 2))
        s.objects = [dict(id='kit', kind='medkit', cell=(2, 3), text='Kit')]
        s.move_direction((1, 0))
        self.assertFalse(s.interact())
        self.assertEqual(s.medkits, 1)


class ExplorationHealTests(unittest.TestCase):
    def test_exploration_heal_rejected_without_consumption(self):
        s = fresh()
        s.player.hp = 10
        self.assertFalse(s.heal())
        self.assertEqual((s.player.hp, s.player.ap, s.medkits), (10, 6, 1))


class PatrolReservationTests(unittest.TestCase):
    def test_patrol_moves_after_pause_waits_when_blocked_and_contact_pauses_others(self):
        s = fresh((4, 2))
        s.patrols = {'guard': {'cells': [(4, 2), (3, 2)], 'pause': .1}}
        s.update(.08)
        self.assertFalse(s.motions)
        s.update(.02)
        self.assertIn('guard', s.motions)
        s.update(.14)
        self.assertEqual(s.enemies['guard'].cell, (3, 2))
        s.move_direction((1, 0))
        self.assertEqual(s.mode, 'combat')
        previous = s.enemies['guard'].cell
        s.update(10)
        self.assertEqual(s.enemies['guard'].cell, previous)

    def test_reservation_and_actor_in_transit_block_without_hostile_contact(self):
        from game.model import Motion
        s = fresh((3, 2))
        s.motions['guard'] = Motion((3, 2), (3, 3))
        self.assertFalse(s.move_direction((1, 0)))
        self.assertEqual(s.mode, 'exploration')
        s.player.cell = (2, 3)
        self.assertFalse(s.move_direction((1, 0)))
        self.assertEqual(s.mode, 'exploration')
        self.assertEqual(s.player.ap, 6)

    def test_contact_mid_tick_does_not_commit_cancelled_other_patrol_motion(self):
        from game.model import Motion
        s = fresh((4, 2))
        s.enemies['other'] = Unit('other', 'Otro', (7, 4), 16, 16)
        s.set_destination((4, 2))
        s.motions['other'] = Motion((7, 4), (7, 5))
        s.update(.14)
        self.assertEqual(s.mode, 'combat')
        self.assertEqual(s.enemies['other'].cell, (7, 4))
        self.assertFalse(s.motions)

    def test_large_dt_and_small_dt_produce_same_patrol_state(self):
        a, b = fresh(), fresh()
        for s in (a, b):
            s.patrols = {'guard': {'cells': [(4, 2), (5, 2)], 'pause': .2}}
        a.update(1.6)
        for _ in range(80):
            b.update(.02)
        self.assertEqual(a.enemies['guard'].cell, b.enemies['guard'].cell)
        self.assertEqual(set(a.motions), set(b.motions))
