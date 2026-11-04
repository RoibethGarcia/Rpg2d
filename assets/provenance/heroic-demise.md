# Ambientación de El Puesto de Control — 04/11/2026

El usuario aportó `Heroic Demise (New).mp3` y solicitó usarlo en el segundo
escenario, El Puesto de Control (`puesto`). Se copia sin modificar bytes a
`assets/sounds/ambience/heroic-demise-new.mp3`: 12 381 383 bytes, SHA-256
`f6551bed406c25acc8877ce51fd6fff0b70df3cb7636d9186eb220541b9d158e`.
Solo se cambia el nombre local; no se recorta, convierte ni normaliza el audio.
El juego no depende de Downloads ni del directorio de ejecución.

No se proporcionaron autoría, enlace original ni licencia verificable.
El título del archivo no acredita su autoría ni condiciones de uso.
**Redistribución pendiente de confirmación**: confirmar condiciones antes de
publicar; no atribuirle la licencia CC0 de los efectos de interfaz.

## Reproducción y límites

- `ambiences.puesto` en el manifiesto configura la pista y volumen inicial 0.35.
- Reutiliza el streaming con `pygame.mixer.music`, en bucle infinito, sin
  cambios de código del juego ni de las reglas del dominio.
- Al viajar desde Hondonada, se detiene y libera `prologue.mp3` y empieza
  esta pista. Al regresar se restaura `prologue.mp3` desde el principio.
- El inicio directo `--map puesto` también reproduce esta pista. Los frames,
  el combate y los efectos de botones no reinician ni sustituyen la ambientación.
- Viajar a planta cambia a [Gran Batalla](gran-batalla.md), asignada en el
  incremento posterior. Ir al menú, victoria, derrota y cierre detienen y
  liberan el stream. Cada nueva partida reinicia su pista.
- Los sonidos UI conservan su canal independiente; el modo explícito
  `audio_enabled=False` sigue sin inicializar ni utilizar el mixer.
- SDL dummy no acredita escucha real, mezcla de volúmenes ni continuidad
  audible en la unión del bucle. No se ha editado la pista para hacerla continua.

## Validación — 04/11/2026

TDD: RED observado por ausencia de la entrada `puesto`, de la reproducción al
iniciar allí y del cambio de pista al viajar. GREEN: **17 pruebas de audio y
244 pruebas totales correctas** con SDL dummy. Incluye inicio directo del puesto,
ida/vuelta con Hondonada, salida a planta y reproducción real del MP3 desde otro
directorio junto con un efecto UI. No acredita escucha física.

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -B -m unittest discover -s tests -v
```

Copia idéntica verificada con `cmp` y SHA-256; `git diff --check` sin errores.
Sin builds, instalaciones, commits ni publicaciones.
