"""Estado de partida y comandos independientes de la presentación."""
from dataclasses import dataclass, field
from game.world import GridMap, Cell, DIRECTIONS
from game.config import (TURN_AP, STEP_DURATION, BASIC_DAMAGE, POWER_DAMAGE, BASIC_COST,
                         POWER_COST, HEAL_AMOUNT, HEAL_COST, ENEMY_ATTACK_COST, ENEMY_ACTION_DELAY)

def _valid_cell(cell):
    return (isinstance(cell, tuple) and len(cell) == 2
            and all(type(value) is int for value in cell))


@dataclass(frozen=True)
class ActionResult:
    ok: bool
    message: str
    def __bool__(self):
        return self.ok

@dataclass
class Unit:
    id: str
    name: str
    cell: Cell
    hp: int
    max_hp: int
    ap: int = TURN_AP
    damage: int = 3
    boss: bool = False

@dataclass
class Motion:
    start: Cell
    end: Cell
    elapsed: float = 0
    duration: float = STEP_DURATION

@dataclass(frozen=True)
class MapExit:
    id: str
    cell: Cell
    destination: str
    spawn: Cell
    requires: str | None = None


@dataclass
class MapState:
    """Mundo persistente por partida; no contiene otra Vera ni inventario."""
    grid: GridMap
    enemies: dict[str, Unit] = field(default_factory=dict)
    objects: list[dict] = field(default_factory=list)
    patrols: dict = field(default_factory=dict)
    collected: set[str] = field(default_factory=set)
    opened: set[str] = field(default_factory=set)
    patrol_wait: dict = field(default_factory=dict)
    patrol_index: dict = field(default_factory=dict)
    clock: float = 0
    name: str = 'Mapa de prueba'
    exits: dict[str, MapExit] = field(default_factory=dict)
    reserved_spawns: set[Cell] = field(default_factory=set)

    def spawn_available(self, cell):
        return (_valid_cell(cell) and cell in self.reserved_spawns and self.grid.walkable(cell)
                and not any(u.hp > 0 and u.cell == cell for u in self.enemies.values())
                and not any(tuple(o['cell']) == cell and
                            (o.get('blocking') or o['kind'] in ('panel', 'pump', 'tank'))
                            for o in self.objects))


class GameState:
    """Fachada de comandos; cada propiedad de mundo delega al mapa activo."""
    def __init__(self, grid, player, enemies=None, objects=None, patrols=None,
                 *, message='', maps=None, map_id='legacy'):
        self.player = player
        self.maps = maps if maps is not None else {
            map_id: MapState(grid, enemies if enemies is not None else {},
                             objects if objects is not None else [],
                             patrols if patrols is not None else {})}
        self.map_id = map_id
        self.context_revision = 0
        self.mode = 'exploration'
        self.turn = 'player'
        self.active_enemy_id = None
        self.medkits = 1
        self.credential = False
        self.message = message
        self.motions = {}
        self.route = []
        self._pending_direction = None
        self._enemy_wait = 0

    @property
    def world(self):
        return self.maps[self.map_id]

    @property
    def grid(self):
        return self.world.grid

    @property
    def enemies(self):
        return self.world.enemies

    @enemies.setter
    def enemies(self, value):
        self.world.enemies = value

    @property
    def objects(self):
        return self.world.objects

    @objects.setter
    def objects(self, value):
        self.world.objects = value

    @property
    def patrols(self):
        return self.world.patrols

    @patrols.setter
    def patrols(self, value):
        self.world.patrols = value

    @property
    def collected(self):
        return self.world.collected

    @property
    def opened(self):
        return self.world.opened

    @property
    def _patrol_wait(self):
        return self.world.patrol_wait

    @property
    def _patrol_index(self):
        return self.world.patrol_index

    @property
    def _clock(self):
        return self.world.clock

    @_clock.setter
    def _clock(self, value):
        self.world.clock = value

    @classmethod
    def new(cls):
        from game.content import new_game
        return new_game()

    def _result(self, ok, message):
        self.message = message
        return ActionResult(ok, message)

    def _player_allowed(self):
        return self.mode in ('exploration', 'combat') and self.turn == 'player' and self.player.hp > 0

    def occupied(self, exclude=None):
        units = [self.player, *self.enemies.values()]
        cells = {u.cell for u in units if u.hp > 0 and u.id != exclude}
        cells.update(m.end for uid, m in self.motions.items() if uid != exclude)
        return cells

    def move_direction(self, delta):
        if not self._player_allowed() or delta not in DIRECTIONS:
            return self._result(False, 'Movimiento no disponible')
        self.route.clear()
        if self.player.id in self.motions:
            self._pending_direction = delta
            return self._result(True, 'Dirección preparada después del paso actual')
        target = self.grid.direction_target(self.player.cell, delta)
        return self._start_step(self.player, target)

    def set_destination(self, cell):
        if not self._player_allowed() or self.player.id in self.motions:
            return self._result(False, 'Espera a completar el paso actual')
        path = self.preview_path(cell)
        if not path:
            return self._result(False, 'Sin ruta')
        if self.mode == 'combat':
            path = path[:self.player.ap]
        if not path:
            return self._result(False, 'PA insuficientes')
        self.route = path
        self._pending_direction = None
        return self._advance_route()

    def cancel_route(self):
        if not self._player_allowed():
            return self._result(False, 'Acción no disponible')
        self.route.clear()
        self._pending_direction = None
        return self._result(True, 'Recorrido cancelado después del paso actual')

    def preview_path(self, cell):
        if not self._player_allowed():
            return []
        hostile_goal = self.mode == 'exploration' and any(
            u.hp > 0 and u.cell == cell and u.id not in self.motions for u in self.enemies.values())
        return self.grid.find_path(self.player.cell, cell, self.occupied(self.player.id), hostile_goal)

    def _advance_route(self):
        if not self.route:
            return self._result(False, 'Sin pasos pendientes')
        cell = self.route.pop(0)
        result = self._start_step(self.player, cell)
        if not result:
            self.route.clear()
        return result

    def _start_step(self, unit, target):
        if unit.hp <= 0 or unit.id in self.motions or not self.grid.can_step(unit.cell, target):
            return self._result(False, 'Destino bloqueado')
        # Reservas y actores en tránsito son bloqueos ordinarios, no contacto.
        if any(m.end == target for uid, m in self.motions.items() if uid != unit.id):
            return self._result(False, 'Destino reservado')
        occupants = [u for u in [self.player, *self.enemies.values()] if u.hp > 0 and u.id != unit.id and u.cell == target]
        if occupants:
            other = occupants[0]
            if self.mode == 'exploration' and other.id not in self.motions and (unit.id == self.player.id or other.id == self.player.id):
                enemy = other if unit.id == self.player.id else unit
                self._begin_combat(enemy)
                return self._result(True, 'Contacto: Vera comienza. Da una nueva orden.')
            return self._result(False, 'Casilla ocupada')
        if self.mode == 'combat' and unit.ap < 1:
            return self._result(False, 'PA insuficientes')
        self.motions[unit.id] = Motion(unit.cell, target)
        return self._result(True, 'Movimiento')

    def _begin_combat(self, enemy):
        self.mode = 'combat'
        self.turn = 'player'
        self.active_enemy_id = enemy.id
        self.player.ap = TURN_AP
        self.route.clear()
        self.motions.clear()
        self._pending_direction = None

    def _combat_action_allowed(self):
        return self._player_allowed() and self.mode == 'combat' and not self.motions and not self.route

    def attack(self, power=False):
        if not self._combat_action_allowed():
            return self._result(False, 'Ataque no disponible: espera tu turno y detén el movimiento')
        enemy = self.enemies[self.active_enemy_id]
        cost = POWER_COST if power else BASIC_COST
        if enemy.hp <= 0 or not self.grid.can_step(self.player.cell, enemy.cell):
            return self._result(False, 'El enemigo debe estar en una casilla vecina')
        if self.player.ap < cost:
            return self._result(False, 'PA insuficientes')
        self.player.ap -= cost
        damage = POWER_DAMAGE if power else BASIC_DAMAGE
        enemy.hp = max(0, enemy.hp - damage)
        if enemy.hp == 0:
            self.mode = 'exploration'
            self.active_enemy_id = None
            self.route.clear()
            self.motions.clear()
            if enemy.boss:
                self.credential = True
                return self._result(True, 'Jefe derrotado. Credencial recuperada: activa el panel con E.')
            return self._result(True, f'{enemy.name} derrotado. Conservas vida y recursos.')
        return self._result(True, f'Golpe de Vera: {damage} de daño')

    def heal(self):
        if not self._combat_action_allowed():
            return self._result(False, 'Botiquín disponible solo durante tu turno de combate')
        if self.medkits < 1:
            return self._result(False, 'No quedan botiquines')
        if self.player.hp >= self.player.max_hp:
            return self._result(False, 'La vida ya está completa')
        if self.player.ap < HEAL_COST:
            return self._result(False, 'PA insuficientes')
        self.medkits -= 1
        self.player.hp = min(self.player.max_hp, self.player.hp + HEAL_AMOUNT)
        self.player.ap -= HEAL_COST
        return self._result(True, 'Botiquín utilizado: hasta 8 de vida recuperada')

    def end_turn(self):
        if not self._combat_action_allowed():
            return self._result(False, 'No puedes terminar el turno ahora')
        self.route.clear()
        self._pending_direction = None
        self.turn = 'enemy'
        self.enemies[self.active_enemy_id].ap = TURN_AP
        self._enemy_wait = ENEMY_ACTION_DELAY
        return self._result(True, 'Turno de La Custodia')

    def _enemy_action(self):
        enemy = self.enemies[self.active_enemy_id]
        if enemy.hp <= 0:
            return
        if self.grid.can_step(enemy.cell, self.player.cell):
            if enemy.ap >= ENEMY_ATTACK_COST:
                enemy.ap -= ENEMY_ATTACK_COST
                self.player.hp = max(0, self.player.hp - enemy.damage)
                self.message = f'{enemy.name}: {enemy.damage} de daño'
                if self.player.hp == 0:
                    self.mode = 'defeat'
                    self.motions.clear()
                    self.route.clear()
                    self.message = 'Vera cayó. La Hondonada sigue esperando agua.'
                return
        elif enemy.ap >= 1:
            path = self.grid.find_path(enemy.cell, self.player.cell, self.occupied(enemy.id), True)
            if path and self._start_step(enemy, path[0]):
                return
        self.turn = 'player'
        self.player.ap = TURN_AP
        self.message = 'Turno de Vera: 6 PA'

    def validate_campaign(self):
        """Rechaza datos inseguros en carga; nunca inventa una aparición alternativa."""
        if self.map_id not in self.maps:
            raise ValueError('Mapa activo inexistente')
        for map_id, world in self.maps.items():
            if (world.grid.width, world.grid.height) != (24, 16):
                raise ValueError(f'{map_id}: se requiere una rejilla 24×16')
            if any(not _valid_cell(c) or not world.grid.in_bounds(c) for c in world.grid.blocked):
                raise ValueError(f'{map_id}: obstáculo fuera de la rejilla')
            if not world.reserved_spawns:
                raise ValueError(f'{map_id}: faltan apariciones reservadas')
            for cell in world.reserved_spawns:
                if not _valid_cell(cell) or not world.spawn_available(cell):
                    raise ValueError(f'{map_id}: aparición reservada inválida {cell}')
            for uid, patrol in world.patrols.items():
                cells = [tuple(c) for c in patrol['cells']]
                if (uid not in world.enemies or not cells
                        or any(not _valid_cell(c) or not world.grid.walkable(c)
                               or c in world.reserved_spawns for c in cells)
                        or any(not world.grid.can_step(a, b) for a, b in zip(cells, cells[1:] + cells[:1]))):
                    raise ValueError(f'{map_id}: patrulla inválida {uid}')
            for exit_id, exit in world.exits.items():
                destination = self.maps.get(exit.destination)
                if (exit.id != exit_id or not _valid_cell(exit.cell) or not world.grid.walkable(exit.cell)
                        or destination is None or not _valid_cell(exit.spawn)
                        or not destination.spawn_available(exit.spawn)
                        or not any(world.grid.can_step(c, exit.cell) for c in world.reserved_spawns)
                        or (exit.requires and not any(o['id'] == exit.requires and o['kind'] == 'maintenance'
                                                     for o in world.objects))):
                    raise ValueError(f'{map_id}: salida inválida {exit_id}')
        if (not _valid_cell(self.player.cell) or not self.world.spawn_available(self.player.cell)):
            raise ValueError('Aparición inicial de Vera inválida')

    def travel(self, exit_id):
        """Viaje atómico: validar todo antes de cambiar el mapa activo."""
        if (self.mode != 'exploration' or not self._player_allowed()
                or self.motions or self.route or self._pending_direction is not None):
            return self._result(False, 'Viaja solo en exploración y sin pasos ni rutas pendientes')
        exit = self.world.exits.get(exit_id)
        if (exit is None or not _valid_cell(exit.cell) or not self.grid.walkable(exit.cell)
                or not self.grid.can_step(self.player.cell, exit.cell)):
            return self._result(False, 'Acércate a una casilla vecina de la salida')
        if exit.requires and exit.requires not in self.opened:
            return self._result(False, 'La salida exige abrir el acceso de mantenimiento')
        destination = self.maps.get(exit.destination)
        if destination is None or not destination.spawn_available(exit.spawn):
            return self._result(False, 'Datos de viaje inválidos: aparición no disponible')
        self.route.clear()
        self.motions.clear()
        self._pending_direction = None
        self.active_enemy_id = None
        self._enemy_wait = 0
        self.map_id = exit.destination
        self.context_revision += 1
        self.player.cell = exit.spawn
        return self._result(True, f'{destination.name}. Vida y recursos conservados.')

    def interact(self):
        if (self.mode != 'exploration' or not self._player_allowed()
                or self.player.id in self.motions or self.route or self._pending_direction is not None):
            return self._result(False, 'Interactúa fuera de combate y sin moverte')
        for exit_id, exit in self.world.exits.items():
            if self.grid.can_step(self.player.cell, exit.cell):
                return self.travel(exit_id)
        priorities = {'medkit': 0, 'maintenance': 1, 'mechanism': 2, 'panel': 3, 'note': 4}
        for obj in sorted(self.objects, key=lambda o: priorities.get(o['kind'], 5)):
            oid, kind, cell = obj['id'], obj['kind'], tuple(obj['cell'])
            if oid in self.collected or oid in self.opened or (self.player.cell != cell and not self.grid.can_step(self.player.cell, cell)):
                continue
            if kind == 'medkit':
                self.medkits += 1
                self.collected.add(oid)
            elif kind == 'maintenance':
                self.grid.blocked.discard(tuple(obj['target']))
                self.opened.add(oid)
            elif kind == 'mechanism':
                self.opened.add(oid)
            elif kind == 'panel':
                if self.motions:
                    return self._result(False, 'Espera a que terminen los pasos antes de activar el suministro')
                if not self.grid.can_step(self.player.cell, cell):
                    return self._result(False, 'Colócate en una casilla vecina al panel')
                if not self.credential:
                    return self._result(False, 'El panel exige la credencial del jefe')
                self.mode = 'victory'
                self.opened.add(oid)
            return self._result(True, obj.get('text', 'Objeto examinado'))
        return self._result(False, 'No hay nada cercano con lo que interactuar')

    def update(self, dt):
        if dt < 0:
            raise ValueError('dt debe expresarse en segundos no negativos')
        if self.mode in ('victory', 'defeat'):
            return
        # Pasos de simulación acotados: un dt grande no altera costos ni secuencia.
        self._clock += dt
        while self._clock + 1e-9 >= .02:
            self._clock -= .02
            self._tick(.02)
            if self.mode in ('victory', 'defeat'):
                self._clock = 0
                break

    def _tick(self, dt):
        for uid, motion in list(self.motions.items()):
            # Un contacto previo en este tick pudo cancelar el snapshot restante.
            if self.motions.get(uid) is not motion:
                continue
            motion.elapsed += dt
            if motion.elapsed + 1e-9 < motion.duration:
                continue
            unit = self.player if uid == self.player.id else self.enemies[uid]
            unit.cell = motion.end
            del self.motions[uid]
            if self.mode == 'combat':
                unit.ap -= 1
            if uid == self.player.id:
                if self._pending_direction is not None:
                    delta = self._pending_direction
                    self._pending_direction = None
                    self.move_direction(delta)
                elif self.route:
                    self._advance_route()
        if self.mode == 'exploration':
            self._update_patrols(dt)
        elif self.mode == 'combat' and self.turn == 'enemy' and not self.motions:
            self._enemy_wait -= dt
            if self._enemy_wait <= 1e-9:
                self._enemy_action()
                self._enemy_wait = ENEMY_ACTION_DELAY

    def _update_patrols(self, dt):
        for uid, patrol in self.patrols.items():
            unit = self.enemies[uid]
            if unit.hp <= 0 or uid in self.motions:
                continue
            self._patrol_wait[uid] = self._patrol_wait.get(uid, patrol.get('pause', 1)) - dt
            if self._patrol_wait[uid] > 0:
                continue
            cells = patrol['cells']
            index = self._patrol_index.get(uid, 0)
            target = tuple(cells[(index + 1) % len(cells)])
            result = self._start_step(unit, target)
            if self.mode == 'combat':
                break
            if result:
                self._patrol_index[uid] = (index + 1) % len(cells)
            self._patrol_wait[uid] = patrol.get('pause', 1)

