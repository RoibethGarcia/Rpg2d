"""Ejecutar con .venv/bin/python main.py desde cualquier directorio."""
import argparse
import os

# macOS: que el clic que da foco a la ventana también llegue al juego (sin doble clic).
os.environ.setdefault('SDL_MOUSE_FOCUS_CLICKTHROUGH', '1')

from game.app import LastValveGame  # noqa: E402 (después de fijar el entorno de SDL)


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
