"""Estado de partida y comandos independientes de la presentación."""
from dataclasses import dataclass, field
from game.world import GridMap, Cell, DIRECTIONS, distance
from game.config import (TURN_AP, STEP_DURATION, BASIC_DAMAGE, POWER_DAMAGE, BASIC_COST,
                         POWER_COST, HEAL_AMOUNT, HEAL_COST, ENEMY_ATTACK_COST, ENEMY_ACTION_DELAY)

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

@dataclass
class GameState:
    grid: GridMap
    player: Unit
    enemies: dict[str, Unit] = field(default_factory=dict)
    objects: list[dict] = field(default_factory=list)
    patrols: dict = field(default_factory=dict)
    mode: str = 'exploration'
    turn: str = 'player'
    active_enemy_id: str | None = None
    medkits: int = 1
    credential: bool = False
    message: str = ''
    motions: dict[str, Motion] = field(default_factory=dict)
    route: list[Cell] = field(default_factory=list)
    collected: set[str] = field(default_factory=set)
    opened: set[str] = field(default_factory=set)

    _pending_direction: Cell | None = None
    _clock: float = 0
    _enemy_wait: float = 0
    _patrol_wait: dict = field(default_factory=dict)
    _patrol_index: dict = field(default_factory=dict)

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
        target = (self.player.cell[0] + delta[0], self.player.cell[1] + delta[1])
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
        if unit.hp <= 0 or unit.id in self.motions or distance(unit.cell, target) != 1 or not self.grid.walkable(target):
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
        if enemy.hp <= 0 or distance(self.player.cell, enemy.cell) != 1:
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
        if distance(enemy.cell, self.player.cell) == 1:
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

    def interact(self):
        if self.mode != 'exploration' or not self._player_allowed() or self.player.id in self.motions or self.route:
            return self._result(False, 'Interactúa fuera de combate y sin moverte')
        priorities = {'medkit': 0, 'maintenance': 1, 'mechanism': 2, 'panel': 3, 'note': 4}
        for obj in sorted(self.objects, key=lambda o: priorities.get(o['kind'], 5)):
            oid, kind, cell = obj['id'], obj['kind'], tuple(obj['cell'])
            if oid in self.collected or oid in self.opened or distance(self.player.cell, cell) > 1:
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
                if distance(self.player.cell, cell) != 1:
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

