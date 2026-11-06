# Pantalla de créditos — reemplazo del 06/11/2026

El usuario aportó **«Pantalla de créditos en ruinas pixel art.png»** y
solicitó sustituir la pantalla anterior. Se copia sin modificar
bytes a `assets/images/ui/credits.png`: **1645×956, RGB opaco**, SHA-256
`ec5f1a41fa76d887baf13f699d0256d76eb97b8715267dd441325d562a64598e`.
No se generó ni editó la imagen. Autoría, modelo de generación y condiciones de
redistribución no fueron verificados independientemente. No hay enlace público
de origen: **redistribución pendiente de confirmación**, sin licencia inventada.

## Presentación y navegación

- `VictoryScene` usa el recurso `images.credits` del manifiesto. Se muestra
  inmediatamente al alcanzar la victoria mediante la válvula, sin alterar las
  reglas del dominio, y reemplaza la antigua presentación de victoria.
- Se conserva el encuadre completo con escalado proporcional y bandas negras
  centradas, preparado una sola vez, no por frame. No se superponen paneles,
  correcciones ni textos sobre la imagen nueva. El PNG en disco y el recurso
  original cargado permanecen intactos; no depende de Downloads.
- El botón pintado «Volver al menú» tiene el rectángulo de autoría
  `[671,839,299,60]` en píxeles del PNG (`menu_button` en el manifiesto).
  La zona clicable usa el mismo escalado y desplazamiento que la imagen.
  Un clic izquierdo, **Escape** o **Enter** regresan al menú con sonido `back`.
  «Comenzar» desde el menú crea una partida limpia. La derrota no cambia.
- Todos los textos, incluidos sonido y música, están incrustados en la imagen.
  Cambiarlos requiere otro recurso; no hay páginas ni desplazamiento.

## Texto incrustado y atribuciones reales

La imagen menciona «Game Sounds», «iwantmyfile5» y OpenGameArt para efectos.
**Eso no coincide con los cuatro efectos de interfaz cargados actualmente**:
`sounds.click`, `confirm`, `error` y `back` en
`assets/manifest.json` corresponden a Interface SFX Pack 1 de **ObsydianX**,
`https://obsydianx.itch.io/interface-sfx-pack-1`, licencia CC0-1.0. Los archivos
son `assets/sounds/{click,confirm,error,back}.ogg`, renombrados sin modificar sus
bytes. Su atribución y la del resto de recursos están en `docs/ASSETS.md` y el
manifiesto; el PNG no sustituye esos registros completos.

La nueva imagen atribuye los golpes a Independent.nu y dice CC0, y muestra
autores de las tres pistas. Son textos aportados por el usuario, **no una
verificación independiente**: la [autoría y licencia de los golpes](combat-sounds.md)
y los permisos de música siguen pendientes en sus registros. Las menciones de
modelos del PNG tampoco prueban su procedencia. No se modifican los registros de
licencias ni se resuelven permisos de publicación por cambiar esta pantalla.

## Historial

- El 30/10/2026 se integró «Pantalla de créditos industrial al atardecer.png»,
  de 1672×940, SHA-256
  `39f30f52f82ffc152264eac06083e04a854abcdd5142e9dee32d33a5331196dc`.
- El 06/11/2026 se añadió sobre ese arte un panel editable de sonido y música.
  La petición posterior de sustituir la pantalla por el nuevo PNG elimina esa
  superposición para respetar el diseño aportado completo.
