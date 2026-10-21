"""Contratos de campaña provisional; dominio sin pantalla ni recursos."""
import unittest

from game.model import GameState


class CampaignTests(unittest.TestCase):
    def test_new_campaign_has_three_independent_persistent_maps_and_one_vera(self):
        state, other = GameState.new(), GameState.new()
        self.assertTrue(hasattr(state, 'maps'), 'Falta la colección persistente de mapas')
        self.assertEqual(set(state.maps), {'hondonada', 'puesto', 'planta'})
        self.assertEqual(state.map_id, 'hondonada')
        self.assertIs(state.grid, state.maps['hondonada'].grid)
        self.assertIs(state.enemies, state.maps['hondonada'].enemies)
        self.assertEqual((state.player.hp, state.medkits, state.credential), (30, 1, False))
        for map_id, world in state.maps.items():
            self.assertEqual((world.grid.width, world.grid.height), (24, 16))
            self.assertIsNot(world, other.maps[map_id])
            self.assertIsNot(world.grid, other.maps[map_id].grid)
            for field in ('enemies', 'objects', 'patrols', 'collected', 'opened',
                          'patrol_wait', 'patrol_index', 'exits', 'reserved_spawns'):
                self.assertIsNot(getattr(world, field), getattr(other.maps[map_id], field))
            world.collected.add('test')
            world.opened.add('test')
            world.grid.blocked.clear()
            self.assertNotIn('test', other.maps[map_id].collected)
            self.assertNotIn('test', other.maps[map_id].opened)
            self.assertTrue(other.maps[map_id].grid.blocked)
        self.assertIsNot(state.maps['puesto'].grid, state.maps['planta'].grid)

    def test_neighbor_e_roundtrip_preserves_shared_and_map_progress(self):
        state = GameState.new()
        vera = state.player
        home = state.world
        state.player.hp, state.player.ap, state.medkits = 17, 2, 0
        state.credential = True
        state.player.cell = (4, 10)
        self.assertTrue(state.interact(), 'E vecino debe viajar al puesto')
        self.assertEqual((state.map_id, state.player.cell), ('puesto', (2, 10)))
        self.assertIs(state.player, vera)
        self.assertIs(state.grid, state.maps['puesto'].grid)
        state.enemies['guard1'].hp = 0
        state.collected.add('kit1')
        state.opened.add('maintenance')
        state.grid.blocked.discard((7, 8))
        state._patrol_wait['guard1'] = .75
        state._patrol_index['guard1'] = 2
        state.player.cell = (1, 10)
        self.assertTrue(state.interact())
        self.assertEqual((state.map_id, state.player.cell), ('hondonada', (4, 10)))
        self.assertIs(state.world, home)
        self.assertTrue(state.interact())
        self.assertEqual(state.enemies['guard1'].hp, 0)
        self.assertEqual(state.collected, {'kit1'})
        self.assertEqual(state.opened, {'maintenance'})
        self.assertTrue(state.grid.walkable((7, 8)))
        self.assertEqual((state._patrol_wait['guard1'], state._patrol_index['guard1']), (.75, 2))
        self.assertEqual((vera.hp, vera.ap, state.medkits, state.credential), (17, 2, 0, True))

    def test_maintenance_gate_blocks_forward_but_not_return(self):
        state = GameState.new()
        state.player.cell = (4, 10)
        self.assertTrue(state.interact())
        state.player.cell = (9, 8)
        self.assertFalse(state.interact())
        self.assertEqual(state.map_id, 'puesto')
        state.player.cell = (6, 8)
        self.assertTrue(state.interact())
        self.assertIn('maintenance', state.opened)
        state.player.cell = (9, 8)
        self.assertTrue(state.interact())
        self.assertEqual(state.map_id, 'planta')
        state.maps['puesto'].opened.clear()  # El requisito solo limita la ida.
        self.assertTrue(state.interact())
        self.assertEqual(state.map_id, 'puesto')

    def test_invalid_initial_spawn_is_rejected_not_relocated(self):
        from unittest.mock import patch
        from game.content import load_world_data
        data = load_world_data()
        data['player']['cell'] = [0, 0]
        with patch('game.content.load_world_data', return_value=data):
            with self.assertRaises(ValueError):
                GameState.new()

    def snapshot(self, state):
        from copy import deepcopy
        return deepcopy({key: value for key, value in vars(state).items() if key != 'message'})

    def test_invalid_travel_is_atomic_for_context_and_busy_states(self):
        from game.model import Motion
        for reason in ('combat', 'victory', 'defeat', 'enemy_turn', 'dead', 'route',
                       'player_motion', 'patrol_motion', 'pending', 'far', 'unknown'):
            with self.subTest(reason=reason):
                state = GameState.new()
                state.player.cell = (4, 10)
                if reason in ('combat', 'victory', 'defeat'):
                    state.mode = reason
                elif reason == 'enemy_turn':
                    state.turn = 'enemy'
                elif reason == 'dead':
                    state.player.hp = 0
                elif reason == 'route':
                    state.route.append((4, 9))
                elif reason.endswith('motion'):
                    uid = 'vera' if reason == 'player_motion' else 'guard'
                    state.motions[uid] = Motion((4, 10), (4, 9))
                elif reason == 'pending':
                    state._pending_direction = (1, 0)
                elif reason == 'far':
                    state.player.cell = (3, 10)
                before = self.snapshot(state)
                self.assertFalse(state.travel('missing' if reason == 'unknown' else 'to_puesto'))
                self.assertEqual(self.snapshot(state), before)
                if reason in ('combat', 'victory', 'defeat', 'route', 'player_motion', 'pending'):
                    self.assertFalse(state.interact())
                    self.assertEqual(self.snapshot(state), before)

    def test_invalid_or_occupied_return_spawn_rejects_without_random_teleport(self):
        from game.model import Unit
        for reason in ('blocked', 'occupied', 'object', 'unreserved', 'missing_map'):
            with self.subTest(reason=reason):
                state = GameState.new()
                state.player.cell = (4, 10)
                self.assertTrue(state.interact())
                state.player.cell = (1, 10)
                home = state.maps['hondonada']
                if reason == 'blocked':
                    home.grid.blocked.add((4, 10))
                elif reason == 'occupied':
                    home.enemies['intruder'] = Unit('intruder', 'Intruso', (4, 10), 16, 16)
                elif reason == 'object':
                    home.objects.append(dict(id='tank', kind='tank', cell=(4, 10)))
                elif reason == 'unreserved':
                    home.reserved_spawns.remove((4, 10))
                else:
                    del state.maps['hondonada']
                before = self.snapshot(state)
                self.assertFalse(state.interact())
                self.assertEqual(self.snapshot(state), before)

    def test_invalid_reserved_data_and_exits_raise_value_error(self):
        from dataclasses import replace
        for reason in ('blocked_spawn', 'patrol_spawn', 'blocking_prop', 'bad_exit',
                       'missing_destination', 'unreserved_destination', 'missing_approach', 'bad_gate'):
            with self.subTest(reason=reason):
                state = GameState.new()
                world = state.maps['puesto']
                if reason == 'blocked_spawn':
                    world.grid.blocked.add((2, 10))
                elif reason == 'patrol_spawn':
                    world.reserved_spawns.add((8, 10))
                elif reason == 'blocking_prop':
                    world.objects.append(dict(id='tank', kind='tank', cell=(2, 10)))
                elif reason == 'bad_exit':
                    world.exits['to_planta'] = replace(world.exits['to_planta'], cell=(-1, 3))
                elif reason == 'missing_destination':
                    world.exits['to_planta'] = replace(world.exits['to_planta'], destination='missing')
                elif reason == 'unreserved_destination':
                    world.exits['to_planta'] = replace(world.exits['to_planta'], spawn=(9, 7))
                elif reason == 'missing_approach':
                    world.reserved_spawns.remove((1, 10))
                else:
                    world.exits['to_planta'] = replace(world.exits['to_planta'], requires='missing')
                with self.assertRaises(ValueError):
                    state.validate_campaign()

    def test_inactive_maps_freeze_including_patrol_progress_and_fractional_clock(self):
        state = GameState.new()
        puesto = state.maps['puesto']
        puesto.patrol_wait['guard1'], puesto.patrol_index['guard1'], puesto.clock = .1, 0, .01
        before = self.snapshot(state)['maps']['puesto']
        state.update(3.57)
        self.assertEqual(puesto, before)
        state.player.cell = (4, 10)
        self.assertTrue(state.interact())
        state.update(.02)
        self.assertLess(puesto.patrol_wait['guard1'], .1)
        for _ in range(30):
            state.update(.02)
            if state.motions:
                break
        self.assertIn('guard1', state.motions)
        state.update(.14)
        state.player.cell = (1, 10)
        self.assertTrue(state.interact())
        frozen = self.snapshot(state)['maps']['puesto']
        state.update(7)
        self.assertEqual(puesto, frozen)

    def test_new_game_resets_all_nested_progress_without_shared_references(self):
        first, clean = GameState.new(), GameState.new()
        first.player.hp, first.medkits, first.credential = 1, 0, True
        first.route.append((2, 9))
        first.maps['puesto'].patrols['guard1']['cells'][0][0] = 99
        first.maps['puesto'].objects[0]['cell'] = (99, 99)
        first.maps['planta'].enemies['boss'].hp = 0
        first.maps['planta'].collected.add('kit2')
        first.maps['puesto'].opened.add('maintenance')
        first.maps['puesto'].patrol_index['guard1'] = 2
        self.assertEqual(clean.maps['puesto'].patrols['guard1']['cells'][0], [8, 10])
        self.assertNotEqual(clean.maps['puesto'].objects[0]['cell'], (99, 99))
        self.assertEqual(clean.maps['planta'].enemies['boss'].hp, 48)
        self.assertEqual((clean.map_id, clean.player.hp, clean.player.ap, clean.medkits, clean.credential),
                         ('hondonada', 30, 6, 1, False))
        self.assertFalse(clean.route or clean.motions)
        for world in clean.maps.values():
            self.assertFalse(world.collected or world.opened or world.patrol_index or world.patrol_wait)

    def test_runtime_invalid_exit_cell_or_malformed_spawn_is_rejected_atomically(self):
        from dataclasses import replace
        for reason in ('blocked_exit', 'malformed_spawn'):
            state = GameState.new()
            state.player.cell = (4, 10)
            if reason == 'blocked_exit':
                state.grid.blocked.add((5, 10))
            else:
                state.world.exits['to_puesto'] = replace(state.world.exits['to_puesto'], spawn=[2, 10])
            before = self.snapshot(state)
            self.assertFalse(state.travel('to_puesto'))
            self.assertEqual(self.snapshot(state), before)

    def test_real_combat_freezes_all_patrol_timers_and_inactive_maps(self):
        state = GameState.new()
        state.player.cell = (4, 10)
        self.assertTrue(state.interact())
        state.player.cell = (7, 10)
        target = state.enemies['guard1'].cell
        delta = next(d for d, c in state.grid.step_directions[state.player.cell].items() if c == target)
        self.assertTrue(state.move_direction(delta))
        self.assertEqual(state.mode, 'combat')
        before = self.snapshot(state)
        state.update(3)
        self.assertEqual(state.maps['planta'], before['maps']['planta'])
        self.assertEqual(state.maps['hondonada'], before['maps']['hondonada'])
        self.assertEqual(state._patrol_wait, before['maps']['puesto'].patrol_wait)
        self.assertEqual(state._patrol_index, before['maps']['puesto'].patrol_index)
        self.assertFalse(state.motions)
