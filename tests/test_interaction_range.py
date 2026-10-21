"""NPC y salidas a dos aristas transitables, sin ampliar otras acciones."""
from copy import deepcopy
import unittest

from game.model import GameState, MapExit, MapState, Motion, Unit
from game.world import GridMap


def npc(cell=(3, 2), name='neighbor'):
    return dict(id=name, kind='npc', cell=cell, blocking=True,
                speaker=name, dialogue=['Una conversación.'])


def scenario(*, objects=(), exit_cell=None):
    home = MapState(GridMap(9, 7), objects=list(objects))
    away = MapState(GridMap(9, 7), reserved_spawns={(1, 1)}, name='Destino')
    if exit_cell is not None:
        home.exits['road'] = MapExit('road', exit_cell, 'away', (1, 1))
    return GameState(home.grid, Unit('vera', 'Vera', (1, 2), 30, 30),
                     maps={'home': home, 'away': away}, map_id='home')


def snapshot(state):
    return deepcopy({k: v for k, v in vars(state).items() if k != 'message'})


class InteractionRangeTests(unittest.TestCase):
    def test_npc_two_steps_away_opens_dialogue_without_moving_or_spending(self):
        state = scenario(objects=[npc()])
        before = (state.player.cell, state.player.hp, state.player.ap, state.medkits)
        self.assertTrue(state.interact())
        self.assertEqual(state.active_dialogue.npc_id, 'neighbor')
        self.assertEqual((state.player.cell, state.player.hp, state.player.ap, state.medkits), before)

    def test_exit_from_same_cell_one_or_two_steps_by_e_and_direct_command(self):
        for steps in (0, 1, 2):
            for direct in (False, True):
                with self.subTest(steps=steps, direct=direct):
                    state = scenario(exit_cell=(1 + steps, 2))
                    state.player.hp, state.player.ap, state.medkits = 17, 2, 0
                    result = state.travel('road') if direct else state.interact()
                    self.assertTrue(result, result.message)
                    self.assertEqual((state.map_id, state.player.cell), ('away', (1, 1)))
                    self.assertEqual((state.player.hp, state.player.ap, state.medkits), (17, 2, 0))

    def test_three_steps_and_same_cell_npc_are_rejected_atomically(self):
        for kind in ('npc', 'exit', 'same_npc'):
            with self.subTest(kind=kind):
                state = (scenario(exit_cell=(4, 2)) if kind == 'exit' else
                         scenario(objects=[npc((1, 2) if kind == 'same_npc' else (4, 2))]))
                before = snapshot(state)
                self.assertFalse(state.interact())
                self.assertEqual(snapshot(state), before)
                if kind == 'exit':
                    self.assertFalse(state.travel('road'))
                    self.assertEqual(snapshot(state), before)

    def test_walls_occupants_and_reserved_steps_block_intermediate_cells(self):
        for target in ('npc', 'exit'):
            for obstruction in ('wall', 'npc', 'object', 'enemy', 'reservation'):
                with self.subTest(target=target, obstruction=obstruction):
                    state = scenario(objects=[npc()] if target == 'npc' else [],
                                     exit_cell=(3, 2) if target == 'exit' else None)
                    if obstruction == 'wall':
                        state.grid.blocked.add((2, 2))
                    elif obstruction in ('npc', 'object'):
                        blocker = (npc((2, 2), 'blocker') if obstruction == 'npc' else
                                   dict(id='panel', kind='panel', cell=(2, 2), blocking=True))
                        state.objects.append(blocker)
                    elif obstruction == 'enemy':
                        state.enemies['guard'] = Unit('guard', 'Guardia', (2, 2), 16, 16)
                    else:
                        state.enemies['guard'] = Unit('guard', 'Guardia', (2, 3), 16, 16)
                        state.motions['guard'] = Motion((2, 3), (2, 2))
                    before = snapshot(state)
                    if obstruction == 'npc':
                        # Puede hablar con el bloqueante, pero no a través de él.
                        self.assertTrue(state.interact())
                        self.assertEqual(state.active_dialogue.npc_id, 'blocker')
                        self.assertEqual(state.map_id, 'home')
                    else:
                        self.assertFalse(state.interact())
                        self.assertEqual(snapshot(state), before)

    def test_exit_on_blocking_object_or_occupied_goal_is_not_usable(self):
        for obstruction in ('object', 'enemy'):
            state = scenario(exit_cell=(3, 2))
            if obstruction == 'object':
                state.objects.append(dict(id='crate', kind='crate', cell=(3, 2), blocking=True))
            else:
                state.enemies['guard'] = Unit('guard', 'Guardia', (3, 2), 16, 16)
            before = snapshot(state)
            self.assertFalse(state.interact())
            self.assertFalse(state.travel('road'))
            self.assertEqual(snapshot(state), before)

    def test_custom_graph_two_edges_not_coordinate_distance_decide_reach(self):
        for target in ('npc', 'exit'):
            with self.subTest(target=target):
                state = scenario(objects=[npc((8, 6))] if target == 'npc' else [],
                                 exit_cell=(8, 6) if target == 'exit' else None)
                state.grid.adjacency = {(1, 2): ((5, 4),), (5, 4): ((8, 6),), (8, 6): ()}
                self.assertTrue(state.interact())
                if target == 'npc':
                    self.assertEqual(state.active_dialogue.npc_id, 'neighbor')
                else:
                    self.assertEqual(state.map_id, 'away')

    def test_disconnected_and_three_edge_graph_reject_geometrically_near_targets(self):
        for adjacency in ({(1, 2): (), (2, 2): ()},
                          {(1, 2): ((5, 4),), (5, 4): ((8, 6),), (8, 6): ((2, 2),)}):
            for target in ('npc', 'exit'):
                state = scenario(objects=[npc((2, 2))] if target == 'npc' else [],
                                 exit_cell=(2, 2) if target == 'exit' else None)
                state.grid.adjacency = adjacency
                before = snapshot(state)
                self.assertFalse(state.interact())
                self.assertEqual(snapshot(state), before)

    def test_near_npc_wins_over_far_exit_and_far_npc_listed_first(self):
        state = scenario(objects=[npc((1, 4), 'far'), npc((1, 1), 'near')], exit_cell=(3, 2))
        self.assertTrue(state.interact())
        self.assertEqual(state.map_id, 'home')
        self.assertEqual(state.active_dialogue.npc_id, 'near')

    def test_equal_distance_keeps_exit_priority_and_npc_order_stable(self):
        state = scenario(objects=[npc((1, 4))], exit_cell=(3, 2))
        self.assertTrue(state.interact())
        self.assertEqual(state.map_id, 'away')
        for _ in range(2):
            state = scenario(objects=[npc((1, 4), 'first'), npc((3, 2), 'second')])
            self.assertTrue(state.interact())
            self.assertEqual(state.active_dialogue.npc_id, 'first')

    def test_unavailable_exit_does_not_mask_another_valid_interaction(self):
        for alternative in ('npc', 'medkit', 'maintenance', 'exit'):
            for reason in ('gate', 'spawn', 'motion'):
                with self.subTest(alternative=alternative, reason=reason):
                    state = scenario(exit_cell=(2, 2))
                    if reason == 'gate':
                        state.world.exits['road'] = MapExit('road', (2, 2), 'away', (1, 1), 'gate')
                    elif reason == 'spawn':
                        state.maps['away'].reserved_spawns.clear()
                    else:
                        state.enemies['guard'] = Unit('guard', 'Guardia', (7, 4), 16, 16)
                        state.motions['guard'] = Motion((7, 4), (7, 5))
                    if alternative == 'npc':
                        state.objects.append(npc((1, 1)))
                    elif alternative == 'exit':
                        if reason != 'gate':
                            continue  # Ambos viajes comparten aparición y bloqueo de movimiento.
                        state.world.exits['other'] = MapExit('other', (1, 1), 'away', (1, 1))
                    else:
                        state.objects.append(dict(id='item', kind=alternative, cell=(1, 2), target=(4, 4)))
                    self.assertTrue(state.interact())
                    if alternative == 'npc':
                        self.assertIsNotNone(state.active_dialogue)
                    elif alternative == 'exit':
                        self.assertEqual(state.map_id, 'away')
                    elif alternative == 'medkit':
                        self.assertEqual(state.medkits, 2)
                    else:
                        self.assertIn('item', state.opened)

    def test_locked_exit_without_alternative_still_rejects_atomically(self):
        state = scenario(exit_cell=(3, 2))
        state.world.exits['road'] = MapExit('road', (3, 2), 'away', (1, 1), 'gate')
        before = snapshot(state)
        self.assertFalse(state.interact())
        self.assertIn('mantenimiento', state.message)
        self.assertEqual(snapshot(state), before)

    def test_other_objects_and_attacks_do_not_gain_two_step_range(self):
        for kind in ('medkit', 'maintenance', 'mechanism', 'panel', 'note'):
            state = scenario(objects=[dict(id='item', kind=kind, cell=(3, 2), target=(4, 4))])
            state.credential = True
            before = snapshot(state)
            self.assertFalse(state.interact())
            self.assertEqual(snapshot(state), before)
        state = scenario()
        state.enemies['guard'] = Unit('guard', 'Guardia', (3, 2), 16, 16)
        state._begin_combat(state.enemies['guard'])
        before = snapshot(state)
        self.assertFalse(state.attack())
        self.assertEqual(snapshot(state), before)

    def test_busy_combat_and_terminal_gates_remain_atomic(self):
        for target in ('npc', 'exit'):
            for reason in ('motion', 'route', 'pending', 'combat', 'victory', 'defeat', 'enemy', 'dead'):
                with self.subTest(target=target, reason=reason):
                    state = scenario(objects=[npc()] if target == 'npc' else [],
                                     exit_cell=(3, 2) if target == 'exit' else None)
                    if reason == 'motion': state.motions['vera'] = Motion((1, 2), (2, 2))
                    elif reason == 'route': state.route = [(2, 2)]
                    elif reason == 'pending': state._pending_direction = (1, 0)
                    elif reason == 'enemy': state.turn = 'enemy'
                    elif reason == 'dead': state.player.hp = 0
                    else: state.mode = reason
                    before = snapshot(state)
                    self.assertFalse(state.interact())
                    if target == 'exit': self.assertFalse(state.travel('road'))
                    self.assertEqual(snapshot(state), before)

    def test_real_campaign_exits_use_two_authored_edges_and_same_cell(self):
        for map_id in ('hondonada', 'puesto', 'planta'):
            for exit_id in GameState.new().maps[map_id].exits:
                for on_exit in (False, True):
                    state = GameState.new()
                    state.map_id = map_id
                    exit = state.world.exits[exit_id]
                    if exit.requires: state.opened.add(exit.requires)
                    if on_exit:
                        state.player.cell = exit.cell
                    else:
                        occupied = state.occupied('vera')
                        state.player.cell = next(c for c in state.grid.adjacency if c not in occupied
                                                 and len(state.grid.find_path(c, exit.cell, occupied)) == 2)
                    with self.subTest(map=map_id, exit=exit_id, same=on_exit):
                        self.assertTrue(state.travel(exit_id))
                        self.assertEqual((state.map_id, state.player.cell), (exit.destination, exit.spawn))

    def test_real_hondonada_villagers_use_two_authored_edges(self):
        for npc_id in ('villager_plaza', 'villager_terrace'):
            state = GameState.new()
            villagers = [o for o in state.objects if o['kind'] == 'npc']
            target = next((o for o in villagers if o['id'] == npc_id), None)
            self.assertIsNotNone(target)
            occupied = state.occupied('vera')
            state.player.cell = next(c for c in state.grid.adjacency if c not in occupied
                                     and len(state.grid.find_path(c, target['cell'], occupied, True)) == 2)
            self.assertTrue(state.interact())
            self.assertEqual(state.active_dialogue.npc_id, npc_id)
