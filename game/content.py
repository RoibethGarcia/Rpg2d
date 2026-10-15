"""Carga nuevos datos independientes; nunca conserva estado mutable entre partidas."""
import json
from pathlib import Path
from game.model import GameState, Unit
from game.world import GridMap

DATA_PATH = Path(__file__).resolve().parents[1] / 'data' / 'world.json'


def load_world_data():
    with DATA_PATH.open(encoding='utf-8') as source:
        return json.load(source)


def new_game():
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
