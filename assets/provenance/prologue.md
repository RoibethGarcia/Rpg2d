# Ambientación de La Hondonada — 04/11/2026

El usuario aportó `prologue.mp3` y solicitó usarlo en el escenario inicial.
Se copia sin modificar bytes a `assets/sounds/ambience/prologue.mp3`:
1 810 180 bytes, SHA-256
`53d36059f2af6884572f002a0153aa8b394b68b7d4a2adb7ffdd2a2e701820ea`.
El juego no depende de Downloads ni del directorio de ejecución.

No se proporcionaron autoría, enlace original ni licencia verificable.
**Redistribución pendiente de confirmación**: no atribuir CC0 ni la licencia de
los efectos de interfaz; confirmar condiciones antes de publicar el recurso.

## Reproducción y límites

- `ambiences.hondonada` del manifiesto asocia la pista al mapa inicial.
- Streaming con `pygame.mixer.music`, bucle infinito y volumen inicial 0.35.
  No se decodifica la pista completa como `Sound` ni se carga por frame.
- Se mantiene al caminar, interactuar y conversar; los efectos de botones
  siguen usando su canal reservado, sin cortar la ambientación.
- Al viajar a un mapa sin pista, ir al menú, ganar, perder o cerrar se detiene
  y libera el stream. Volver a Hondonada o crear otra partida inicia desde cero.
- Menú, créditos, derrota, puesto y planta no tienen pistas propias en este
  incremento inicial. Posteriormente se asignaron al puesto y a la planta sus
  propias pistas: [Heroic Demise](heroic-demise.md) y
  [Gran Batalla](gran-batalla.md). Sus inicios directos no usan `prologue.mp3`.
- `audio_enabled=False` no inicializa ni utiliza el mixer; los errores reales
  de carga/reproducción no se ocultan.
- Las pruebas SDL dummy comprueban decodificación, reproducción y transiciones,
  NO escucha física, equilibrio de volumen ni continuidad audible de la unión
  del bucle. No se ha editado el MP3 para crear una unión sin saltos.

Para sustituir una pista, copiar su archivo al proyecto y actualizar la entrada
en `ambiences` bajo el ID del mapa, con ruta, volumen, hash y procedencia.
No requiere modificar las reglas del dominio.

## Validación — 04/11/2026

TDD: se observaron fallos por ausencia del registro y de la reproducción antes
de implementar. Resultado final: **13 pruebas específicas y 240 pruebas totales
correctas**, con SDL dummy. El MP3 también se reprodujo desde un directorio de
trabajo distinto, a la vez que un efecto UI, y se detuvo al regresar al menú.

Comando de la suite completa, desde la raíz del repositorio:

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -B -m unittest discover -s tests -v
```

`git diff --check` sin errores y hash de la copia idéntico al original.
Sin builds, empaquetado, instalaciones ni comprobación de sonido físico.
