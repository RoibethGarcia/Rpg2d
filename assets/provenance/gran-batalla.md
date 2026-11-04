# Ambientación de la Planta — 04/11/2026

El usuario aportó `Gran Batalla.mp3` y solicitó usarlo en el tercer escenario,
la Planta (`planta`). Se copia sin modificar bytes a
`assets/sounds/ambience/gran-batalla.mp3`: 1 799 155 bytes, SHA-256
`71131d0ab60e29a67e41206984fa3f95642e147af9290668427a3d6db58ba407`.
Solo se cambia el nombre local; no se recorta, convierte ni normaliza el audio.
El juego no depende de Downloads ni del directorio de ejecución.

No se proporcionaron autoría, enlace original ni licencia verificable.
El título no acredita procedencia ni permisos: **redistribución pendiente de
confirmación** antes de publicar. No se le atribuye CC0 ni la licencia de los
efectos de interfaz.

## Reproducción y límites

- `ambiences.planta` configura la pista con volumen inicial 0.35 y bucle infinito.
- Reutiliza el streaming de `pygame.mixer.music` existente, sin modificar la
  lógica del juego ni las reglas de viaje, combate o victoria.
- Viajar desde el puesto detiene y libera `Heroic Demise (New).mp3` e inicia
  `Gran Batalla.mp3`. Regresar al puesto restaura su pista desde el principio.
- El inicio directo `--map planta` también usa esta pista. Frames, combate y
  sonidos UI no la reinician; UI conserva su canal reservado independiente.
- Volver al menú, ganar activando la válvula, perder o cerrar detiene y libera
  el stream. Una nueva partida inicia la pista de su escenario desde cero.
- `audio_enabled=False` sigue sin inicializar ni utilizar el mixer.
- Las pruebas con SDL dummy no acreditan escucha física, equilibrio de volumen
  ni continuidad audible en la unión del bucle. No se editó el MP3 para hacerla
  continua.

## Validación — 04/11/2026

TDD: RED por ausencia del registro y del stream de planta; GREEN con **19
pruebas de audio y 246 pruebas totales correctas** en SDL dummy. Incluye inicio
directo, viajes puesto↔planta, terminales en los tres mapas y reproducción real
del MP3 desde otro directorio junto con un efecto UI. No acredita escucha física.

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -B -m unittest discover -s tests -v
```

Copia idéntica verificada con `cmp` y SHA-256; `git diff --check` sin errores.
Sin builds, instalaciones, commits ni publicaciones.
