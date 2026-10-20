"""Ejecutar con .venv/bin/python main.py desde cualquier directorio."""
import argparse
from game.app import LastValveGame


def main():
    parser = argparse.ArgumentParser(description='La última válvula')
    parser.add_argument('--map', choices=('puesto', 'planta'),
                        help='Comenzar una partida de prueba fresca en el mapa elegido')
    args = parser.parse_args()
    game = LastValveGame()
    if args.map:
        game.start_new_game(map_id=args.map)
    game.run()


if __name__ == '__main__':
    main()
