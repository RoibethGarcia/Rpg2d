import unittest
from game.model import GameState
from game.world import distance


class ContentTests(unittest.TestCase):
    def test_new_game_has_approved_balance_and_independent_mutable_state(self):
        s, other = GameState.new(), GameState.new()
        self.assertEqual((s.grid.width, s.grid.height), (24, 16))
        self.assertEqual((s.player.hp, s.medkits, len(s.enemies)), (30, 1, 4))
        self.assertEqual(sorted(e.hp for e in s.enemies.values()), [16, 16, 16, 48])
        self.assertEqual(sum(o['kind'] == 'medkit' for o in s.objects), 2)
        s.grid.blocked.clear()
        s.player.hp = 1
        self.assertEqual(other.player.hp, 30)
        self.assertTrue(other.grid.blocked)

    def test_map_gate_and_all_encounter_cells_walkable(self):
        s = GameState.new()
        self.assertFalse(s.grid.walkable((7, 8)))
        for unit in [s.player, *s.enemies.values()]:
            self.assertTrue(s.grid.walkable(unit.cell))
        for patrol in s.patrols.values():
            cells = [tuple(c) for c in patrol['cells']]
            for a, b in zip(cells, cells[1:] + cells[:1]):
                self.assertEqual(distance(a, b), 1)
                self.assertTrue(s.grid.walkable(b))


class FullPlaythroughTests(unittest.TestCase):
    """Partida real: comandos públicos; sin teleports, HP ni inventario adulterados."""
    def tick_until_player_idle(self, state):
        for _ in range(500):
            if state.player.id not in state.motions and not state.route:
                return
            state.update(.02)
        self.fail('Movimiento no termina')

    def walk(self, state, cell):
        for _ in range(100):
            if state.player.cell == cell or state.mode != 'exploration':
                break
            result = state.set_destination(cell)
            if result:
                self.tick_until_player_idle(state)
            else:
                state.update(.2)
        self.assertEqual(state.player.cell, cell, state.message)

    def enter_arena(self, state, ring, entry, enemy_id):
        self.walk(state, entry)
        for _ in range(300):
            if state.mode == 'combat':
                break
            index = ring.index(state.player.cell)
            target = ring[(index + 1) % len(ring)]
            delta = (target[0] - state.player.cell[0], target[1] - state.player.cell[1])
            if state.move_direction(delta):
                self.tick_until_player_idle(state)
            else:
                state.update(.2)
        self.assertEqual(state.active_enemy_id, enemy_id)
        self.assertIn(state.player.cell, ring)
        self.assertIn(state.enemies[enemy_id].cell, ring)

    def retreat(self, state, ring, steps):
        enemy = state.enemies[state.active_enemy_id]
        index = ring.index(state.player.cell)
        direction = 1 if ring[(index + 1) % len(ring)] != enemy.cell else -1
        for _ in range(steps):
            index = ring.index(state.player.cell)
            target = ring[(index + direction) % len(ring)]
            delta = (target[0] - state.player.cell[0], target[1] - state.player.cell[1])
            self.assertTrue(state.move_direction(delta), state.message)
            self.tick_until_player_idle(state)

    def fight(self, state, ring, heal_once):
        healed = False
        rounds = 0
        while state.mode == 'combat' and rounds < 30:
            rounds += 1
            self.assertEqual(state.turn, 'player')
            enemy = state.enemies[state.active_enemy_id]
            self.assertEqual(distance(state.player.cell, enemy.cell), 1)
            if heal_once and not healed and state.player.hp <= 22:
                self.assertTrue(state.heal(), state.message)
                healed = True
                self.retreat(state, ring, 4)
            else:
                self.assertTrue(state.attack(power=True), state.message)
                if state.mode == 'exploration':
                    break
                self.retreat(state, ring, 3)
            self.assertTrue(state.end_turn(), state.message)
            for _ in range(500):
                state.update(.02)
                if state.turn == 'player' or state.mode == 'defeat':
                    break
            self.assertNotEqual(state.mode, 'defeat', f'HP: {state.player.hp}; ronda {rounds}')
        self.assertEqual(state.mode, 'exploration')
        self.assertEqual(healed, heal_once)

    def test_complete_real_map_three_guards_boss_credential_and_panel(self):
        from game.content import load_world_data
        state = GameState.new()
        rings = {e['id']: [tuple(c) for c in e['arena']] for e in load_world_data()['enemies']}
        self.enter_arena(state, rings['guard1'], (2, 8), 'guard1')
        self.fight(state, rings['guard1'], False)
        self.walk(state, (6, 10))
        self.assertTrue(state.interact())  # botiquín 1
        self.walk(state, (6, 9))
        self.assertTrue(state.interact())  # mantenimiento
        self.assertIn('maintenance', state.opened)
        self.enter_arena(state, rings['guard2'], (9, 6), 'guard2')
        self.fight(state, rings['guard2'], True)
        self.enter_arena(state, rings['guard3'], (9, 9), 'guard3')
        self.fight(state, rings['guard3'], True)
        self.walk(state, (14, 8))
        self.assertTrue(state.interact())  # botiquín 2
        self.enter_arena(state, rings['boss'], (17, 8), 'boss')
        self.fight(state, rings['boss'], True)
        self.assertTrue(state.credential)
        self.assertEqual([e.hp for e in state.enemies.values()], [0, 0, 0, 0])
        self.assertEqual((state.player.hp, state.medkits), (2, 0))
        self.walk(state, (22, 13))
        self.assertTrue(state.interact())
        self.assertEqual(state.mode, 'victory')
        self.assertFalse(state.attack())
        clean = GameState.new()
        self.assertEqual((clean.mode, clean.player.hp, clean.medkits, clean.credential),
                         ('exploration', 30, 1, False))
        self.assertFalse(clean.collected | clean.opened)
        self.assertFalse(clean.motions or clean.route)
