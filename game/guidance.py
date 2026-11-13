"""Textos de ayuda contextuales; solo leen el estado, nunca lo modifican."""

from math import ceil

from game.config import BASIC_COST, POWER_COST, HEAL_COST, HEAL_AMOUNT, POWER_DAMAGE, BASIC_DAMAGE, TURN_AP


def objective(state):
    if state.map_id == 'puesto':
        if 'maintenance' in state.opened:
            return 'Cruza la salida «Planta de distribución» (E).'
        return 'Pulsa E junto a «Mantenimiento» para abrir la planta.'
    if state.map_id == 'hondonada':
        return 'Sigue el camino hasta la salida al Puesto (E).'
    if state.credential:
        return 'Acércate a la válvula y pulsa E a su lado.'
    return 'Derrota al jefe de La Custodia y recupera su credencial.'


def combat_hint(state):
    if state.turn != 'player':
        return 'Turno enemigo: espera a que termine.'
    ap = state.player.ap
    if end_turn_advised(state):
        if any(u.hp > 0 and state.grid.can_step(state.player.cell, u.cell)
               for u in state.enemies.values()):
            # Medido con el motor: retroceder le cuesta PA al enemigo al alcanzarte.
            return f'Te queda {ap} PA: da un paso atrás (el enemigo gasta PA en alcanzarte) o Espacio termina el turno'
        return f'Te queda {ap} PA: solo alcanza para un paso · Espacio termina el turno'
    foes = [u for u in state.enemies.values()
            if u.hp > 0 and state.grid.can_step(state.player.cell, u.cell)]
    if foes:
        # Estimación con Potente (el golpe que más rinde por PA); es una guía, no una regla.
        boss = next((u for u in foes if u.boss), None)
        turns = ''
        if boss is not None:
            n = ceil(boss.hp / (POWER_DAMAGE * (TURN_AP // POWER_COST)))
            turns = f' · jefe: ~{n} turno' + ('s' if n > 1 else '')
        if ap >= POWER_COST:
            return (f'Enemigo al lado · Potente {POWER_COST} PA (daño {POWER_DAMAGE}) rinde más '
                    f'que Llave {BASIC_COST} PA (daño {BASIC_DAMAGE}){turns}')
        if ap >= BASIC_COST:
            return f'Enemigo al lado · te quedan {ap} PA: alcanza Llave (daño {BASIC_DAMAGE}){turns}'
        return 'Sin PA para atacar · Espacio termina el turno'
    if ap < 1:
        return 'Sin PA · Espacio termina el turno'
    return 'Acércate a un enemigo: cada paso cuesta 1 PA y solo se ataca desde una casilla vecina'


def medkit_status(state):
    """Texto del botón y si se puede usar ahora; el motivo va en el propio botón."""
    n = state.medkits
    if state.mode != 'combat':
        return f'Botiquín ×{n} · en combate', False
    if state.turn != 'player':
        return f'Botiquín ×{n} · espera tu turno', False
    if n < 1:
        return 'Botiquín ×0 · sin stock', False
    if state.player.hp >= state.player.max_hp:
        return f'Botiquín ×{n} · vida llena', False
    if state.player.ap < HEAL_COST:
        return f'Botiquín ×{n} · faltan PA', False
    return f'Botiquín ×{n} · {HEAL_COST} PA / +{HEAL_AMOUNT}', True


def end_turn_advised(state):
    """True si solo queda mover un paso: no alcanza para atacar ni curar."""
    return (state.mode == 'combat' and state.turn == 'player'
            and 0 < state.player.ap < min(BASIC_COST, POWER_COST, HEAL_COST))
