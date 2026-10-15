"""Ejecutar con .venv/bin/python main.py desde cualquier directorio."""
from game.app import LastValveGame


def main():
    LastValveGame().run()


if __name__ == '__main__':
    main()
