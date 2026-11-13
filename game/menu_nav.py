"""Selección de menú y curva de aparición; lógica pura, sin pygame."""


class MenuSelection:
    def __init__(self, count):
        self.count, self.index = count, 0

    def move(self, delta):
        self.index = (self.index + delta) % self.count

    def set(self, index):
        if 0 <= index < self.count:
            self.index = index


def reveal(elapsed, start, duration):
    """0 antes de `start`, 1 pasada la duración; suavizada (smoothstep)."""
    t = min(1.0, max(0.0, (elapsed - start) / duration))
    return t * t * (3 - 2 * t)
