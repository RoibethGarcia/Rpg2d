# Motor del curso: procedencia y adaptación local

## Fuente comprobada

Se recuperó el 15 de octubre de 2026 el [notebook original de clase 8](https://colab.research.google.com/drive/1A77JWUmsc-PJjF494SPnFGyEOCElgkZX?usp=sharing).
JSON original: 48 095 bytes, 14 celdas; SHA256:
`262a38dab56f35ef7381ce926af6665b22ef3d2b324b49ec208d6505d8c2b7ae`.
La copia original consultada está temporalmente en
`/private/tmp/rpg2d-clase8-original.ipynb`; NO es dependencia de ejecución.

`engine/asset_manager.py`, `spritesheet.py`, `ui.py`, `game_object.py` y
`game_loop.py` derivan respectivamente de las celdas 2, 3, 4, 5 y 6.
Se conservaron sus clases, nombres, responsabilidades y firmas originales,
salvo las adaptaciones explícitas siguientes. No se copiaron el editor,
ejemplos de Arkanoid ni notebook completo.

**Licencia docente no declarada:** no se encontró licencia explícita ni autor
nominal en el texto de sus celdas. Que sea accesible no demuestra permiso de
redistribución pública. Esta adaptación es local para la entrega del curso;
antes de publicar el motor o el repositorio se debe confirmar ese permiso.
No se atribuye a este código CC0 ni la licencia de los assets.

## Contratos de integración

- `Scene(game)`: `handle_events(events)`, `update(dt)`, `draw(surface)`.
- `GameObject(x, y, frames)`, derivado de `pygame.sprite.Sprite`:
  `update(dt=0)`, `update_animation(dt)`, `draw(surface)`. Conserva el ancla
  central del curso; objetos isométricos derivados deben ajustar su pie.
- `Button(x, y, width, height, text, callback, click_sound=None)`:
  `handle_event(event)` y `draw(surface)`. Solo clic izquierdo interior dispara
  sonido y callback; el recurso se carga antes, no al dibujar.
- `GameLoop(screen_width, screen_height, title, fps, audio_enabled=True)`:
  `handle_specific_events(event)`, `update_game_logic(dt)`,
  `draw_game_elements()`, `run()` y `stop()`. Un único bucle principal.
- `AssetManager`: API original de imágenes/spritesheets/animaciones más
  `load_sound(name, sound_path)` y `get_sound(name)` para sonidos reales.
- `Spritesheet`: JSON original con `spritesheet_path` y `animations`;
  cada frame contiene `name`, `x`, `y`, `width`, `height`.

`dt` siempre representa **segundos**. El loop convierte una sola vez el valor
de `Clock.tick(fps) / 1000.0`; los hooks no vuelven a convertirlo.
La animación usa 6 frames/segundo (equivalente a los 0.1 frames/tick originales
a 60 FPS), conserva sobrantes y soporta varias transiciones en un frame.

El juego es responsable de pasar rutas de assets estables, basadas en su raíz,
no en el directorio de trabajo del IDE. Dentro del spritesheet se conserva
la resolución del nombre de imagen junto al JSON, como en el original.
No hay inicialización de ventana/audio al importar los módulos.

## Correcciones frente al original

- Import `engine.sprite_sheet` corregido a `engine.spritesheet`.
- `Scene.update`, hooks del loop y animaciones adaptados conjuntamente a `dt`.
- QUIT impide actualizar/dibujar ese frame; cierre de Pygame garantizado mediante
  `finally`, también si falla la lógica. No se ocultan excepciones.
- Audio inicializado explícitamente solo si `audio_enabled=True`; `False` es
  un modo silencioso solicitado, no recuperación oculta ante un error de audio.
- Diccionario de sonidos ampliado a carga y acceso reales; errores de recursos
  se propagan. Eliminados los `except Exception` redundantes de carga original.

## Entorno y evidencia TDD

Se autorizó crear `.venv` con Python 3.13.15 e instalar únicamente
`pygame==2.6.1` usando `pip install --only-binary=:all: --no-compile`.
Se instaló el wheel `cp313-macosx_11_0_arm64`, sin compilar dependencias.

Comando real:

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m unittest tests.test_engine -v
```

- **RED:** sobre las clases originales y el import corregido, 8 pruebas:
  7 fallos de aserción por animación por tick, sobrante temporal, ausencia de
  API sonora, botón sin sonido, `dt` no enviado y actualización tras QUIT.
  Sin errores de importación, sintaxis ni dependencia.
- Se corrigió el caso de sobrante para expresar 6 FPS de manera consistente y
  se volvió a ejecutar RED: `current_frame` esperado 1, obtenido 0.
- **GREEN:** adaptación mínima: 8 pruebas correctas.
- **REFACTOR y regresión:** eliminar capturas redundantes; ampliar comprobaciones
  de audio real (WAV temporal), errores, modo silencioso y limpieza tras error.
  Resultado final: 11 pruebas correctas.

SDL dummy demuestra contratos y manejo de recursos, NO sonido físico, calidad
visual ni funcionamiento manual de ventana. No se ejecutaron builds,
`py_compile`, `compileall`, empaquetado, commits ni publicación.
