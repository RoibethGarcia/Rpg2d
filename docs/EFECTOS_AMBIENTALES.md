# Efectos ambientales — escenario 1, La Hondonada

## Qué se ve

- **Cascada:** se conserva el spritesheet `assets/images/effects/waterfall.png`,
  sus ocho poses, anclaje y máscara localizada existentes. La nueva configuración
  controla también su activación y velocidad. No se añade una segunda caída.
- **Río:** reflejos suaves en **tres zonas** de agua del paisaje fijo. Hoja RGBA
  procedural de 16 cuadros, ciclo de 2 segundos a velocidad 1, máscaras locales
  que excluyen las orillas. No se desplaza ni deforma el bitmap original, ni se
  pretende animar TODO el cauce. La placa puede ocultar zonas de río según zoom.
- **Aves:** siluetas pequeñas de 11/14 píxeles, alas curvas en 12 poses,
  transparencias de entrada/salida, desplazamiento curvo lento y desfases. Dos
  trayectorias próximas forman una bandada; otros carriles están en los márgenes.
  El máximo es un límite, no una cantidad garantizada visible en todo momento:
  pueden estar fuera del viewport, ocultas por edificios o entre apariciones.
- **Humo:** partículas suaves e irregulares desde la estufa cilíndrica occidental,
  punto `(330,464)` de la placa. Se expanden, ascienden, derivan y desaparecen.
- **Vapor:** ráfagas desde la junta de la tubería del depósito elevado,
  punto `(838,157)`. Secuencia de silencios de distinta duración; no emite siempre.

No hay nuevas chimeneas: el elemento del techo de estación en `(505,46)` es un
pórtico, no una salida de humo. No se emite desde él ni desde techos arbitrarios.

## Parámetros

Editar `ambient.settings` en [`data/hondonada.json`](../data/hondonada.json)
y reiniciar el juego. No hay menú nuevo.

| Clave | Predeterminado | Intervalo / efecto |
| --- | --- | --- |
| `enabled` | `true` | `false` oculta todos los efectos, incluida la cascada |
| `particle_intensity` | `0.65` | 0–1, proporción del cupo utilizado; 0 oculta humo/vapor |
| `max_particles` | `36` | Entero 0–64, techo global de partículas; no garantiza llenar el cupo |
| `max_birds` | `3` | Entero 0–5; 0 oculta aves |
| `smoke_frequency` | `1.0` | 0–3, multiplicador de frecuencia; 0 elimina emisiones |
| `water_speed` | `1.0` | 0–3, multiplicador de río/cascada; 0 fija sus cuadros |

El pool precalculado tiene 12 plazas por emisor (24 con los dos actuales).
La intensidad reduce las plazas consultadas, intercaladas por emisor; los ciclos
de vida hacen que normalmente haya menos partículas visibles. Subir el máximo
no crea emisores ni plazas adicionales. La frecuencia no acelera el ascenso ni
acorta la vida de cada partícula: cambia sus momentos de nacimiento.
Al saturar una plaza, la frecuencia efectiva se limita para que termine su
fundido antes de reutilizarla; no se descarta humo todavía visible.

`ambient.emitters` usa coordenadas **de la placa**; `ambient.river` usa coordenadas
**del paisaje original**. Cada zona de río declara `rect`, `polygon` y `opacity`
(0–255). NO copiar puntos de una captura de pantalla ni de la imagen de referencia:
sus transformaciones no son las de los recursos activos.

## Integración

- [`game/ambient.py`](../game/ambient.py): `AmbientConfig`, proyección del fondo,
  `EnvironmentalEffects` y `WaterfallAnimation` (reexportada desde environment
  para conservar el import anterior). Preparación de sprites, texturas, máscaras
  y tamaños una vez, nunca durante `draw` o `update`.
- [`game/environment.py`](../game/environment.py): prepara el arte de cada mapa;
  solo Hondonada declara efectos. Aplica el mismo escalado/recorte del paisaje a
  sus máscaras de agua. Pasa por proyección del mapa la cascada y el humo.
- [`game/render.py`](../game/render.py): fondo fijo + río/aves → mundo (base,
  cascada/humo, actores/capas ordenados) → composición ampliada → UI.
  Las aves quedan detrás de edificios; los actores e indicadores delante del
  humo. El zoom amplía el mundo, NO las aves ni el río del fondo.
- [`game/scenes.py`](../game/scenes.py): avanza únicamente el efecto del mapa
  activo usando el delta en segundos que realmente avanzó la simulación. Diálogo
  y finales lo pausan; no se actualiza desde menú ni otros mapas. Viajes, menú y
  partida nueva reinician las poses sin conservar partículas de la visita previa.

Los efectos no reciben `GameState` y no modifican colisiones, selección,
navegación, posiciones, AP, inventario, combate ni turnos. Las trayectorias se
muestrean analíticamente desde tiempo acumulado y usan azar local con semilla
fija al cargar: no consumen azar del gameplay ni dependen del número de frames.

## Puesto, Planta y menú

Los tres reutilizan `EnvironmentalEffects`; solo cambian los datos del bloque
`ambient` de su JSON (`data/puesto.json`, `data/planta.json`, `data/menu.json`).
Sin humo ni vapor propios (`emitters: []`, `particle_intensity: 0`); sí aves
(`max_birds` 2 en los mapas, 3 en el menú) y agua.

Cada zona de agua declara `kind`, `rect`, `polygon` y `opacity`:

| `kind` | Qué dibuja | Uso típico |
| --- | --- | --- |
| `ripple` | Brillos que ondulan en horizontal (hoja procedural de 16 cuadros) | ríos, lagos, piletas |
| `fall` | Estelas claras que bajan, con cabeza y cola suaves (16 cuadros, bucle sin salto) | caídas pintadas |

- `river` está en coordenadas del **paisaje** y se dibuja detrás de la placa. Sin
  `kind` se entiende `ripple` (así sigue funcionando el JSON de La Hondonada).
  Una caída del paisaje (la represa de la Planta) es una entrada `river` con
  `kind: "fall"`.
- `flows` está en coordenadas de la **placa** y se dibuja encima de ella, debajo
  de los actores. `kind` es obligatorio; un valor desconocido es un error al cargar.
- `water_speed` y `enabled` de `settings` aplican igual que en La Hondonada.
- Los polígonos se obtuvieron detectando el agua por color dentro de regiones
  dibujadas a mano y revisando el resultado sobre la imagen. Si se cambia una
  placa o un paisaje hay que rehacerlos: no se corrigen solos.

El menú dibuja el paisaje de la planta con escala «cover», efectos, un velo
oscuro y el texto con sombra corta. Al volver desde la partida el fundido y los
efectos reinician; desde «Opciones» no. Su reloj solo avanza mientras el menú o
las opciones son la escena activa. No hay humo en el menú: las torres de
enfriamiento quedan fuera del encuadre.

## Recursos y fidelidad

**No faltan recursos obligatorios para visualizar los efectos actuales.** Aves,
humo y ondas se generan desde código como superficies RGBA; no se incorporaron
packs externos ni se editaron ilustraciones. Son efectos pequeños y sutiles, no
animaciones ilustradas de alto detalle ni una reconstrucción de la referencia.
La cascada conserva su [procedencia y redistribución pendiente](../assets/provenance/waterfall.md).
Los permisos pendientes de los recursos originales no cambian por este trabajo.

Para mayor detalle de aves, opcionalmente registrar un PNG con alfa real en
`assets/manifest.json` (`images.<nombre>` con `path`, `grid: [columnas, filas]`,
`frame_seconds` y procedencia/licencia verificada) y añadir
`"bird_image": "<nombre>"` dentro de `ambient`, al nivel de `settings`.
Se admiten hasta 64 poses uniformes; mantener el mismo lienzo/ancla en cada celda
y recortar márgenes transparentes excesivos antes de aportar el recurso. Los
frames se preparan a los mismos tamaños pequeños y con sus fades al cargar.
No añadir esa referencia sin el PNG: un recurso declarado ausente es un error,
no se oculta con un placeholder.

## Comprobaciones

Desde la raíz que contiene `main.py`, sin builds:

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -B -m unittest discover -s tests -v
```

Resultado observado al cerrar este incremento: **300 pruebas correctas en
96.527 s**, incluidas **17 nuevas** de efectos. Se ejecutó con ambos drivers SDL
dummy y sin escribir bytecode. `git diff --check` sin errores; enlaces locales
verificados. Comparación del JSON contra HEAD: todos los datos previos son
idénticos al retirar el bloque nuevo `ambient`. `WaterfallAnimation` se trasladó
byte a byte, sin reescribir su lógica ni duplicar su implementación.

Las nuevas pruebas en `tests/test_environment_effects.py` cubren tiempo dividido
en frames, cupos, fades, zonas laterales, vapor irregular, PNG opcional, máscaras,
agua visible tras oclusión, configuración, desactivación, pausa, reset/viajes,
ausencia de I/O/escalado por frame, zoom, clip y no mutación de dominio/recursos.
El test histórico de cascada aísla aves/humo/río con mocks para conservar su
comprobación de que solo cambia el área de la caída.

Se inspeccionaron capturas SDL dummy del estado inicial y efectos a 100%/150%,
así como recortes de la placa y máscaras sobre el paisaje. Estas capturas NO
certifican una partida nativa, el movimiento percibido en pantalla ni todos los
solapamientos posibles. **Pendiente de revisión humana:** observar sutileza,
cadencia y continuidad de las animaciones en una ventana real, viajar ida/vuelta
y conversar con NPC en los tres niveles de zoom. No se ejecutaron builds ni se
instalaron herramientas para validar.
