# Pantalla de créditos — 30/10/2026

El usuario aportó **«Pantalla de créditos industrial al atardecer.png»** y
solicitó mostrarla al ganar, después de activar la válvula. Se copia sin modificar
bytes a `assets/images/ui/credits.png`: **1672×940, RGB opaco**, SHA-256
`39f30f52f82ffc152264eac06083e04a854abcdd5142e9dee32d33a5331196dc`.
No se generó ni editó la imagen. Autoría, modelo de generación y condiciones de
redistribución no fueron verificados independientemente. No hay enlace público
de origen: **redistribución pendiente de confirmación**, sin licencia inventada.

## Presentación y navegación

- `VictoryScene` usa el recurso `images.credits` del manifiesto. Se muestra
  inmediatamente al alcanzar la victoria mediante la válvula, sin alterar las
  reglas del dominio, y reemplaza la antigua presentación de victoria.
- Se conserva TODO el arte con escalado proporcional y bandas negras centradas.
  La superficie escalada se prepara una vez, no por frame. La copia en disco
  permanece intacta; no depende de Downloads ni del directorio de ejecución.
- El botón pintado «Volver al menú» tiene el rectángulo de autoría
  `[704,848,266,64]` en píxeles del PNG (`menu_button` en el manifiesto).
  La zona clicable usa el mismo escalado y desplazamiento que la imagen.
  Un clic izquierdo, **Escape** o **Enter** regresan al menú con sonido `back`.
  «Comenzar» desde el menú crea una partida limpia. La derrota no cambia.
- Los textos están incrustados en la imagen, no son etiquetas editables del
  juego. Para ampliar créditos más adelante, sustituir la imagen con aprobación
  del usuario, actualizar tamaño/hash/procedencia y, si cambia el botón, su
  rectángulo. No se añadió un sistema de páginas ni desplazamiento automático.

## Texto incrustado y atribuciones reales

La imagen menciona OpenGameArt para sonido. **Eso no coincide con los recursos
sonoros cargados actualmente**: `sounds.click`, `confirm`, `error` y `back` en
`assets/manifest.json` corresponden a Interface SFX Pack 1 de **ObsydianX**,
`https://obsydianx.itch.io/interface-sfx-pack-1`, licencia CC0-1.0. Los archivos
son `assets/sounds/{click,confirm,error,back}.ogg`, renombrados sin modificar sus
bytes. Su atribución y la del resto de recursos están en `docs/ASSETS.md` y el
manifiesto; el PNG no sustituye esos registros completos.

Se conserva el arte solicitado sin corregir textos por iniciativa propia.
La discrepancia y las atribuciones completas quedan pendientes para una futura
ampliación/corrección autorizada de créditos antes de la publicación. Las
menciones de modelos que aparecen en el PNG tampoco prueban su procedencia.
