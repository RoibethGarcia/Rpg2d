"""Carga nuevos datos independientes; nunca conserva estado mutable entre partidas."""
import json
from pathlib import Path
from game.model import GameState, MapState, MapExit, Unit
from game.world import GridMap

DATA_PATH = Path(__file__).resolve().parents[1] / 'data' / 'world.json'


def load_world_data():
    with DATA_PATH.open(encoding='utf-8') as source:
        return json.load(source)


def new_legacy_game():
    """Fixture explícita del prototipo original, conservada para su regresión."""
    data = load_world_data()
    p = data['player']
    player = Unit(p['id'], p['name'], tuple(p['cell']), p['hp'], p['hp'])
    enemies = {e['id']: Unit(e['id'], e['name'], tuple(e['cell']), e['hp'], e['hp'],
                             damage=e['damage'], boss=e['boss']) for e in data['enemies']}
    objects = [{**o, 'cell': tuple(o['cell'])} for o in data['objects']]
    return GameState(GridMap(data['width'], data['height'], {tuple(c) for c in data['blocked']}),
                     player, enemies, objects,
                     {e['id']: e['patrol'] for e in data['enemies']},
                     message='La Hondonada necesita agua. Busca el acceso de mantenimiento y llega al panel de control.')


def new_game():
    """Campaña independiente: tres ilustraciones con navegación autorada."""
    old = new_legacy_game()
    from game.hondonada import HondonadaLayout
    hondonada = MapState(HondonadaLayout.load().grid(),
                        objects=[old.objects[0]], name='La Hondonada')
    puesto_layout = HondonadaLayout.load('puesto')
    for uid, cells in {'guard1': [[8,10],[9,10],[10,10],[9,10]],
                       'guard2': [[13,9],[14,9],[15,9],[14,9]]}.items():
        old.enemies[uid].cell = tuple(cells[0])
        old.patrols[uid]['cells'] = cells
    puesto = MapState(puesto_layout.grid(),
                      enemies={uid: old.enemies[uid] for uid in ('guard1','guard2')},
                      objects=[o for o in old.objects if o['id'] in ('maintenance', 'kit1')],
                      patrols={uid: old.patrols[uid] for uid in ('guard1','guard2')}, name='Puesto de control')
    planta_layout = HondonadaLayout.load('planta')
    planta_data = planta_layout.data
    planta = MapState(planta_layout.grid(),
                      enemies={e['id']: Unit(e['id'], e['name'], tuple(e['cell']), e['hp'], e['hp'],
                                            damage=e['damage'], boss=e['boss'])
                               for e in planta_data['enemies']},
                      objects=[{**o, 'cell': tuple(o['cell'])} for o in planta_data['objects']],
                      patrols={e['id']: e['patrol'] for e in planta_data['enemies']},
                      name='Planta de distribución')
    puesto.grid.blocked.add((7, 8))
    hondonada.exits['to_puesto'] = MapExit('to_puesto', (5, 10), 'puesto', (2, 10))
    puesto.exits['to_hondonada'] = MapExit('to_hondonada', (1, 11), 'hondonada', (4, 10))
    puesto.exits['to_planta'] = MapExit('to_planta', (8, 8), 'planta', (9, 8), 'maintenance')
    planta.exits['to_puesto'] = MapExit('to_puesto', (8, 8), 'puesto', (9, 8))
    hondonada.reserved_spawns = {(2, 10), (4, 10)}
    puesto.reserved_spawns = {(2, 10), (1, 10), (9, 8)}
    planta.reserved_spawns = {(9, 8)}
    maps = {'hondonada': hondonada, 'puesto': puesto, 'planta': planta}
    state = GameState(hondonada.grid, old.player, maps=maps, map_id='hondonada',
                     message='Recorre La Hondonada: clic o WASD; las escaleras unen sus niveles. Salida al sur: acércate y pulsa E.')
    state.validate_campaign()
    return state
