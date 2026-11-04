# Sonidos de golpes — 04/11/2026

El usuario aportó ocho FLAC de la carpeta
`independent_nu_ljudbank-hits_and_punches` y pidió cuatro asignaciones fijas:

| Ataque | Original integrado |
| --- | --- |
| Vera: Llave | `hit01.mp3.flac` |
| Vera: Potente | `hit02.mp3.flac` |
| Guardia | `hit03.mp3.flac` |
| Jefe | `hit07.mp3.flac` |

Copias byteidénticas bajo `assets/sounds/combat/`, sin conversión ni recorte.
Hashes SHA-256 y duraciones decodificadas en `combat_sounds` del manifiesto.
No se incorporan los cuatro archivos no seleccionados ni se requieren rutas
externas en ejecución. El volumen inicial es 0.55, ajustable por ataque.
La selección diferencia los cuatro ataques; no se ha verificado por escucha
física el carácter de cada muestra ni su balance con la música.

## Procedencia y derechos

El nombre de la carpeta menciona Independent.nu, pero no se suministró licencia
ni enlace original verificable. La consulta a
<https://opengameart.org/content/37-hitspunches> devolvió HTTP 403 y NO confirma
que estos archivos correspondan a esa página ni su licencia.
**Autoría y licencia no verificadas; redistribución pendiente de confirmación**.
No atribuirles CC0 ni la licencia de los efectos UI. Confirmar condiciones antes
de publicar los FLAC con el juego.

## Reproducción

- Una carga por archivo al iniciar con audio; sin I/O por golpe o frame.
- Un `AttackAction` por aplicación válida de daño, con tipo de ataque. La escena
  consume los hechos una vez tras un comando o actualización, también en silencio.
- `last_attacks` sigue siendo solo el último clip visual por actor. La lista de
  hechos no pierde los ataques sucesivos de IA ni los letales al limpiar el clip.
- Cada golpe usa `Sound.play()` en un canal libre. El canal 0 sigue reservado a
  UI y la música mantiene su streaming. Se permite superponer colas de sonido;
  el siguiente golpe no reinicia la muestra anterior. Los siete canales libres
  existentes cubren los tres golpes del turno enemigo y colas del jugador.
- Menú, reinicio, viaje, reset y cierre detienen colas y descartan hechos pendientes.
  El último sonido letal puede terminar al pasar a derrota; menú lo detiene.
- El sonido del golpe sustituye la confirmación genérica de un ataque válido;
  botones y rechazos mantienen sus sonidos UI.
- No se cambian daño, PA, cadencia IA, animaciones ni condiciones de victoria.
  No hay aleatoriedad ni un sonido por cuadro de animación.
- Un `dt` grande puede agrupar varios hechos: se emite una muestra por cada uno
  al finalizar esa actualización, sin inventar una secuencia tardía ni retrasar
  el dominio. La cadencia audible normal requiere frames regulares.
- SDL dummy comprueba decodificación y canales, NO sonido físico, sincronización
  perceptiva, mezcla ni saturación. Los originales conservan su silencio inicial.

## Validación — 04/11/2026

TDD: RED inicial por registros/eventos/reproducción ausentes y RED dirigido al
cleanup de victoria antes de corregirlo. GREEN: **16 pruebas específicas**
(`tests.test_combat_audio`, 8.596 s) y **275 pruebas totales** (79.115 s), salida 0.
Se actualizó la expectativa de carga de `tests.test_ui` para incluir exactamente
los cuatro sonidos UI y los cuatro de combate; no se relajó a un subconjunto.

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -B -m unittest discover -s tests -v
```

Comprobación adicional desde `/private/tmp` con SDL dummy: los cuatro originales
son byteidénticos a sus copias, se reproducen simultáneamente sin detener música
y menú los detiene. `git diff --check` sin errores. Sin builds, compilación
explícita, instalaciones, commits, publicación ni comprobación de sonido físico.
