import unittest
from game.content import new_legacy_game
from game.world import distance


class ContentTests(unittest.TestCase):
    def test_new_game_has_approved_balance_and_independent_mutable_state(self):
        s, other = new_legacy_game(), new_legacy_game()
        self.assertEqual((s.grid.width, s.grid.height), (24, 16))
        self.assertEqual((s.player.hp, s.medkits, len(s.enemies)), (30, 1, 4))
        self.assertEqual(sorted(e.hp for e in s.enemies.values()), [16, 16, 16, 48])
        self.assertEqual(sum(o['kind'] == 'medkit' for o in s.objects), 2)
        s.grid.blocked.clear()
        s.player.hp = 1
        self.assertEqual(other.player.hp, 30)
        self.assertTrue(other.grid.blocked)

    def test_map_gate_and_all_encounter_cells_walkable(self):
        s = new_legacy_game()
        self.assertFalse(s.grid.walkable((7, 8)))
        for unit in [s.player, *s.enemies.values()]:
            self.assertTrue(s.grid.walkable(unit.cell))
        for patrol in s.patrols.values():
            cells = [tuple(c) for c in patrol['cells']]
            for a, b in zip(cells, cells[1:] + cells[:1]):
                self.assertEqual(distance(a, b), 1)
                self.assertTrue(s.grid.walkable(b))


class FullPlaythroughTests(unittest.TestCase):
    """Fixture original y campaña completa por comandos públicos, sin recursos adulterados."""
    def finish_player_turn(self, state):
        if state.turn == 'player':
            self.assertTrue(state.end_turn(), state.message)
        else:
            self.assertEqual((state.turn, state.player.ap), ('enemy', 0))

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
            delta = next(d for d in ((0,-1),(1,0),(0,1),(-1,0))
                         if state.grid.direction_target(state.player.cell,d) == target)
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
            delta = next(d for d in ((0,-1),(1,0),(0,1),(-1,0))
                         if state.grid.direction_target(state.player.cell,d) == target)
            self.assertTrue(state.move_direction(delta), state.message)
            self.tick_until_player_idle(state)

    def fight(self, state, ring, heal_once):
        healed = False
        rounds = 0
        while state.mode == 'combat' and rounds < 30:
            rounds += 1
            self.assertEqual(state.turn, 'player')
            enemy = state.enemies[state.active_enemy_id]
            self.assertTrue(state.grid.can_step(state.player.cell, enemy.cell))
            if heal_once and not healed and state.player.hp <= 22:
                self.assertTrue(state.heal(), state.message)
                healed = True
                # En un circuito corto, cuatro pasos acercan al rival por el otro lado.
                self.retreat(state, ring, min(4, len(ring) // 2 - 1))
            else:
                self.assertTrue(state.attack(power=True), state.message)
                if state.mode == 'exploration':
                    break
                self.retreat(state, ring, 3)
            self.finish_player_turn(state)
            for _ in range(500):
                state.update(.02)
                if state.turn == 'player' or state.mode == 'defeat':
                    break
            self.assertNotEqual(state.mode, 'defeat', f'HP: {state.player.hp}; ronda {rounds}')
        self.assertEqual(state.mode, 'exploration')
        self.assertEqual(healed, heal_once)

    def fight_campaign_guard(self, state, ring, heal_once):
        for _ in range(2):
            self.assertTrue(state.attack(power=True), state.message)
            self.retreat(state, ring, 3)
            self.finish_player_turn(state)
            for _ in range(500):
                state.update(.02)
                if state.turn == 'player' or state.mode == 'defeat':
                    break
            self.assertEqual(state.mode, 'combat')
        if heal_once:
            self.assertTrue(state.heal(), state.message)
        self.assertTrue(state.attack(), state.message)
        self.assertEqual(state.mode, 'exploration')

    def fight_final_boss(self, state, ring):
        """Presupuesto aprobado: retirada inicial y después dos potentes/turno."""
        self.assertEqual((state.player.hp, state.medkits), (30, 0))
        self.assertTrue(state.attack(power=True))
        self.retreat(state, ring, 3)
        remaining_hp = []
        for _ in range(4):
            if state.mode != 'combat':
                break
            self.finish_player_turn(state)
            for _ in range(500):
                state.update(.02)
                if state.turn == 'player' or state.mode == 'defeat':
                    break
            self.assertEqual(state.mode, 'combat')
            remaining_hp.append(state.player.hp)
            self.assertTrue(state.attack(power=True))
            if state.mode == 'combat':
                self.assertTrue(state.attack(power=True))
        self.assertEqual(remaining_hp, [26, 14, 2])
        self.assertEqual(state.mode, 'exploration')

    def test_complete_real_map_three_guards_boss_credential_and_panel(self):
        from game.content import load_world_data
        state = new_legacy_game()
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
        clean = new_legacy_game()
        self.assertEqual((clean.mode, clean.player.hp, clean.medkits, clean.credential),
                         ('exploration', 30, 1, False))
        self.assertFalse(clean.collected | clean.opened)
        self.assertFalse(clean.motions or clean.route)

    def test_campaign_public_commands_travel_both_ways_and_complete_current_combat(self):
        from game.model import GameState
        from game.content import load_world_data
        state = GameState.new()
        rings = {e['id']: [tuple(c) for c in e['arena']] for e in load_world_data()['enemies']}
        self.walk(state, (4, 10))
        self.assertTrue(state.interact())
        self.assertEqual(state.map_id, 'puesto')
        self.walk(state, (1, 10))
        self.assertTrue(state.interact())
        self.assertEqual(state.map_id, 'hondonada')
        self.assertTrue(state.interact())
        rings['guard1'] = [(c,10) for c in range(7,11)] + [(c,9) for c in range(10,6,-1)]
        rings['guard2'] = [(c,10) for c in range(13,17)] + [(c,9) for c in range(16,12,-1)]
        self.enter_arena(state, rings['guard1'], (7,10), 'guard1')
        self.fight_campaign_guard(state, rings['guard1'], False)
        self.assertEqual(state.player.hp, 24)
        self.walk(state, (6, 10))
        self.assertTrue(state.interact())
        self.enter_arena(state, rings['guard2'], (13,10), 'guard2')
        self.fight_campaign_guard(state, rings['guard2'], True)
        self.assertEqual(state.player.hp, 26)
        self.walk(state, (6, 9))
        self.assertTrue(state.interact())
        self.walk(state, (9, 8))
        self.assertTrue(state.interact())
        self.assertEqual(state.map_id, 'planta')
        # Regreso permitido y progreso de puesto conservado, sin restaurar HP/ítems.
        resources = (state.player.hp, state.player.ap, state.medkits)
        self.assertTrue(state.interact())
        self.assertEqual(state.map_id, 'puesto')
        self.assertEqual(state.enemies['guard1'].hp, 0)
        self.assertIn('kit1', state.collected)
        self.assertIn('maintenance', state.opened)
        self.assertEqual((state.player.hp, state.player.ap, state.medkits), resources)
        self.assertTrue(state.interact())
        from game.hondonada import AuthoredLayout
        rings.update({e['id']: [tuple(c) for c in e['arena']]
                      for e in AuthoredLayout.load('planta').data['enemies']})
        self.walk(state, (1,10))
        self.assertTrue(state.interact())  # kit2, antes de los guardias de planta
        self.enter_arena(state, rings['guard3'], (2,11), 'guard3')
        self.fight_campaign_guard(state, rings['guard3'], True)
        self.assertEqual(state.player.hp, 28)
        self.enter_arena(state, rings['guard4'], (2,7), 'guard4')
        self.fight_campaign_guard(state, rings['guard4'], True)
        self.assertEqual(state.player.hp, 30)
        self.walk(state, (8,7))
        self.assertTrue(state.interact())  # kit3, antes del último guardia/jefe
        self.enter_arena(state, rings['guard5'], (12,7), 'guard5')
        self.fight_campaign_guard(state, rings['guard5'], True)
        self.assertEqual(state.player.hp, 30)
        self.enter_arena(state, rings['boss'], (17,3), 'boss')
        self.fight_final_boss(state, rings['boss'])
        self.assertTrue(state.credential)
        self.assertEqual((state.player.hp, state.medkits), (2, 0))
        self.assertTrue(all(enemy.hp == 0 for world in state.maps.values() for enemy in world.enemies.values()))
        self.assertEqual(state.maps['planta'].collected, {'kit2', 'kit3'})
        self.walk(state, (21,13))
        self.assertTrue(state.interact())
        self.assertEqual(state.mode, 'victory')
