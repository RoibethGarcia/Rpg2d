# UI e integración: evidencia ejecutada

## Contratos y alcance

`LastValveGame(GameLoop)` coordina `scenes`, `current_scene` y
`change_scene(...)`. `MenuScene`, `PlayScene`, `VictoryScene` y `DefeatScene`
heredan de `Scene`; `WorldActor` hereda de `GameObject` y adapta el modelo sin
alterar su casilla. `main.py` tiene un único punto de entrada protegido.

La ventana es 1280×800; proyección 48×24, origen `(400,110)`, sin cámara.
La vista completa del mapa queda separada del panel derecho y las acciones
inferiores. Toda la superficie de ambos paneles captura clics: no hay órdenes
de movimiento que atraviesen botones o áreas vacías de UI.

- WASD y clic delegan en comandos del mismo dominio; Escape cancela rutas.
- Espacio finaliza turno; E recoge o activa; ataques y botiquín mediante botones.
- Ataques, curación y fin de turno aparecen atenuados fuera de combate; los
  comandos rechazados muestran la explicación del dominio, sin consumir recursos.
- Ruta con tramo disponible y resto diferenciado; costo y PA restantes visibles.
- Cambios terminales proceden de `state.mode`, no de condiciones paralelas de UI.
- Cada comienzo crea `GameState.new()` y limpia selección y adaptadores visuales.
- Assets se resuelven desde `Path(__file__)`, se cargan una sola vez y no se
  sustituyen silenciosamente ante archivos ausentes.

Recursos reales: humano frontal/trasero de intellikat, tubería de Darkmoonfire y
sonidos de ObsydianX según `assets/manifest.json`. Suelos, paredes, maquinaria,
insignias y objetos de UI son geometría propia provisional. No se integró SBS.
El humano usa el primer frame GIF estático, escalado 2×; su desplazamiento sí se
interpola desde `Motion`, con pie estable `(16,31)` escalado.

Los sonidos reales usan volumen 0.35 y el canal UI reservado 0. Cada señal
reemplaza la anterior, evitando superponer las largas colas de los originales.
El silencio solo se activa mediante `audio_enabled=False`.

## TDD y regresión

Comando ejecutado:

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m unittest tests.test_ui -v
```

1. **RED:** sobre esqueletos importables, 9 pruebas, 8 fallos de aserción:
   comienzo no creaba partida, estado no se reiniciaba, no se cargaban recursos,
   input no llegaba al dominio y no se transitaba a escenas terminales.
   Ningún fallo por importación, dependencia o sintaxis.
2. **GREEN:** 9/9 correctas tras implementar escenas, renderer y app.
3. **RED de audio:** clic de comienzo dejaba 2 canales ocupados cuando se esperaba
   1. **GREEN:** `ClickCue` conserva el contrato `play()` de `Button` y dirige las
   señales al mismo canal reservado.
4. Se añadió regresión de interpolación: dibujar un movimiento no cambia la
   casilla lógica. **Resultado final UI: 11/11 correctas.**

Se corrigió durante la integración una referencia accidental a `state` en el
dibujo del menú; las pruebas de dibujo detectaron el error y se repitieron verdes.
No se cuenta ese error como un ciclo RED de comportamiento nuevo.

Suite completa ejecutada después de integrar QA independiente:

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m unittest discover -s tests -v
```

Resultado: **70 pruebas correctas**. Incluye recursos, motor, dominio, recorrido
completo real del mapa, UI y pruebas independientes de integración.
El recorrido de dominio es una comprobación distinta de las capturas fixture.
`git diff --check` también se ejecutó sin errores. No se ejecutaron builds,
compilación de validación, empaquetado ni commits.

## Evidencia visual y arranque real

Capturas de superficie Pygame en `artifacts/` (directorio ignorado por Git):
`menu.png`, `partida.png`, `combate.png`, `victoria.png`, `derrota.png`.
Menú y partida corresponden al inicio real; combate usa una posición preparada,
y victoria/derrota son **fixtures gráficos de estado**, NO evidencia E2E.
Se inspeccionaron estas imágenes para mapa completo, lectura y separación de UI.
Esa inspección estática no equivale a jugar manualmente.

Se solicitó y obtuvo autorización expresa para abrir ventana y reproducir audio.
Comando de smoke real (sin variables SDL dummy):

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -c 'import pygame; from game.app import LastValveGame; app = LastValveGame(audio_enabled=True); print("REAL_DRIVERS", pygame.display.get_driver(), pygame.mixer.get_init()); app.start_new_game(); app.draw_game_elements(); pygame.display.flip(); pygame.image.save(app.screen, "artifacts/smoke-real.png"); pygame.time.set_timer(pygame.QUIT, 2200, loops=1); app.run(); print("REAL_SMOKE_OK", not pygame.get_init())'
```

Resultado real: `REAL_DRIVERS cocoa (44100, -16, 2)`;
`REAL_SMOKE_OK True`; proceso terminó con código 0.
Se abrió el juego, se ejecutó la señal sonora de inicio y se cerró tras 2.2 s;
la captura es solo de su superficie, no del escritorio.
Esto comprueba arranque de ventana y mixer reales, **no certifica percepción
audible, interacción humana ni un recorrido manual completo**.
