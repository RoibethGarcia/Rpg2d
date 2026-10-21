# Recursos integrados y procedencia

La selección inicial se descargó el 15 de octubre de 2026 mediante los controles públicos de descarga gratuita de itch.io. Sin cuentas, pagos ni compras. No se redistribuyen archivos ZIP completos ni metadatos privados. El 19 de octubre se reemplazaron los personajes activos por seis PNG aportados por el usuario. `assets/manifest.json` es el contrato de carga; todos sus `path` son relativos a la raíz del proyecto, NO al directorio de trabajo. Incluye procedencia, archivo original, modificaciones y SHA-256; licencia solamente cuando se conoce.

## Personajes activos: nuevos PNG

`assets/images/characters/{vera,guard,boss}_{front,rear}.png` contiene los seis
originales estáticos, copiados byte a byte. Son de 1254×1254 con alfa real.
Origen y nombres originales: [registro de procedencia](../assets/provenance/user-supplied-characters.md).
Fueron generados con ChatGPT según lo indicado por el usuario; no se atribuye
una autoría humana ni una licencia pública no verificada. El manifiesto declara
`source_type: user_supplied`, `redistribution_status: pending_confirmation` y
`provenance_file`, en lugar de inventar un enlace de descarga o `license_file`.
**No publicar estos PNG hasta confirmar condiciones de redistribución.**

- Cada rol carga sus propias vistas. No se aplica el tinte de las plantillas.
- `frame` es un subrectángulo explícito dentro del original; `anchor` es local
  a ese frame y corresponde al apoyo entre las botas, no al centro del arma.
- `render_height` fija 64 px para Vera/guardias y 72 px para el jefe. Se usa
  smoothscale proporcional y el ancla se escala con la misma transformación.
- El recorte/escala ocurre una sola vez al preparar el renderer; no se generan
  ni guardan imágenes derivadas. Los archivos originales no se editan.
- Pies y profundidad dependen de la casilla lógica proyectada. Barras y marcas
  de rol quedan encima del arte, sin pintar sobre su cuerpo.
- Se conserva la orientación frente/espalda existente al desplazarse. No hay
  ciclos de caminar ni ataques animados en este reemplazo.

El arte modular básico se integró originalmente en los tres mapas mediante el atlas descrito abajo. La Hondonada y El Puesto lo sustituyen ahora por sus placas registradas; la planta conserva el atlas. El aldeano de la taza, las láminas de animación, la arena y la interfaz inspirada en el mockup siguen [pendientes por fases](integracion-assets/README.md).
El incremento original de atlas no utilizaba fondos completos. Las integraciones posteriores de La Hondonada y El Puesto, descritas abajo, sí usan placas completas con oclusión por capas y navegación explícita.

## Packs anteriores conservados

| Recursos locales | Fuente y autor | Licencia | Cambios |
|---|---|---|---|
| `assets/images/human_front.gif`, `human_rear.gif` (legacy, no usados por personajes activos) | [32px Isometric Modern Character Template — intellikat](https://intellikat.itch.io/isometric-character-template) | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) | Renombrado, bytes originales de `cycles/template-{front,rear}-stand.gif`. |
| `assets/images/pipes.png` | [Isometric Pipes — Darkmoonfire](https://darkmoonfire.itch.io/isometric-pipes) | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | Ninguno; hoja original `Isometric_Pipes.png`. Selección de rectángulo en tiempo de ejecución. |
| `assets/sounds/{click,confirm,error,back}.ogg` | [Interface SFX Pack 1 — ObsydianX](https://obsydianx.itch.io/interface-sfx-pack-1) | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) | Renombrado, bytes originales. Rutas originales precisas en manifiesto. |

Textos de licencia completos: `assets/licenses/CC0-1.0.txt` (incluido en ZIP de intellikat) y `assets/licenses/CC-BY-SA-4.0.txt` (texto oficial Creative Commons). Para tuberías se conserva autor, enlace y licencia; cualquier modificación artística derivada debe identificarse y compartirse bajo BY-SA 4.0. No aplicar esa licencia indiscriminadamente a todo el código del juego.

### Contrato gráfico de los packs anteriores

- `images.human_front` y `human_rear`: GIF indexado 32×32, color transparente magenta `(255,0,255)`, apoyo `[16,31]`. Pygame detecta el colorkey; al convertir, preservar transparencia (`convert_alpha` o copia con colorkey). Los PNG gigantes del ZIP están ampliados y NO se usan.
- Solo dos orientaciones originales: frente y espalda. Espejo horizontal permite las direcciones laterales; no implica cuatro vistas originales ni animaciones completas.
- Son plantillas humanas monocromas, NO diseños terminados de Vera o La Custodia. Se conservan cargadas como recursos legacy para compatibilidad, pero el renderer activo usa exclusivamente los seis PNG por rol; no aplica los tintes anteriores.
- `images.pipes`: hoja RGBA 192×512; 6 columnas de 32 px, 16 filas. Cuatro variantes, en bandas de cuatro filas: estándar, óxido, plata, azul. `frame:[32,128,32,32]` selecciona un segmento oxidado. Apoyo local `[16,28]` para esa celda; no usarlo para toda la hoja.
- El suelo de planta usa texturas del atlas recortadas a rombos 2:1 de 48×24 en memoria. La Hondonada y El Puesto usan las placas registradas por capas descritas abajo. La fixture legacy conserva suelo geométrico. La lógica del mapa permanece independiente del arte. El escalado humano fijo a 64×64 fue sustituido por escala proporcional y anclas por vista.

### Contrato sonoro

`sounds.click`, `confirm`, `error` y `back` son OGG decodificables por el mixer de Pygame. Los originales duran 6 segundos (incluyen cola/silencio); no se recortaron. Volumen inicial discreto y canales limitados en la UI para evitar acumulación. Las pruebas usan audio dummy: verifican decodificación, NO calidad audible ni adecuación musical. Revisión con dispositivo real pendiente.

## Recursos NO integrados

[SBS Floor Pack](https://screamingbrainstudios.itch.io/isotilepack), [Wall Pack](https://screamingbrainstudios.itch.io/isowallpack) y [Object Pack](https://screamingbrainstudios.itch.io/isometric-object-pack) anuncian CC0 en sus páginas. La descarga de piso respondió HTTP 429; no se reintentó ni se cambió de vía para eludirlo. NO hay archivos SBS integrados y no deben presentarse como tales.

Ni el atlas ni las placas de La Hondonada y El Puesto convierten los packs SBS en recursos integrados. La fixture `legacy` conserva el entorno geométrico. Notas (radio/registro), indicadores de acciones/estado y señalización siguen siendo geometría explícita del proyecto; la planta utiliza módulos raster para suelo, muros, maquinaria, panel y botiquín.

## Verificación

`tests.test_assets` comprueba existencias, rutas confinadas, procedencia, licencias conocidas (sin extenderlas a los PNG), hashes, dimensiones, transparencia, frame y anclaje, además de decodificación de audio. `tests.test_character_assets` verifica recursos por rol/vista, buffers RGBA sin tintes, escala proporcional, pie durante interpolación, ausencia de recarga y error explícito si falta un PNG. No hay descargas durante las pruebas. Resultado histórico del reemplazo de personajes del 19 de octubre: **75 pruebas correctas**; no es el conteo actual de la suite. Se inspeccionaron los seis originales y capturas del renderer real con SDL dummy; partida manual y sonido físico no se verificaron para ese cambio. Evidencia RED/GREEN y resultados posteriores en [VALIDACION](VALIDACION.md).

## Escenarios: incremento anterior de atlas modular

Se generó un atlas nuevo a partir de las tres ilustraciones completas aportadas
por el usuario. **En este incremento anterior no se pegaron esas imágenes como fondos ni se editaron sus bytes.**
Las referencias originales están en `assets/reference/scenarios/`; el atlas
1254×1254 RGBA se carga desde `assets/images/environments/scenario_atlas.png`.
[Procedencia de integración](../assets/provenance/scenario-assets.md) ·
[Prompt exacto y generación](../assets/provenance/scenario-atlas-prompt.md).

- `images.environment_atlas`: `source_type: ai_generated`, hash, referencias con
  hashes y prompt obligatorio; no se inventa licencia CC0/BY-SA. Redistribución
  pendiente para atlas y referencias. No publicar aún.
- `environment_frames`: 16 recortes explícitos; la imagen generada NO respetó
  celdas uniformes. Escalas y anclas locales se preparan una vez en memoria.
- `environment_sets`: configuración conservada del incremento modular anterior; actualmente solo la planta la utiliza en campaña. Hondonada y Puesto usan las integraciones por capas descritas abajo. En aquel incremento había suelos y muros distintos por mapa; casetas/toldos en pueblo,
  caseta roja/cajas en puesto, depósitos/bombas en planta. Texturas de suelo con
  máscara de rombo y underlay intencional. No cargas ni escalados por frame.
- Las decoraciones solo usan huellas ya bloqueadas y respetan objetos, salidas y
  apariciones. Profundidad ordenada por pie, compartida con actores y obstáculos.
- No se modificaron colisiones, rutas, enemigos, combate ni balance. En aquel incremento La Hondonada
  seguía siendo un espacio provisional con módulos pequeños sobre el borde; no se
  afirma reconstrucción completa del pueblo. Hay halos rojizos leves de generación.

`tests.test_environment_assets` añade selección de estilo tras viajes, integridad
del dominio al dibujar, caché, errores explícitos, huellas y profundidad. La auditoría
de recursos también comprueba prompt y los hashes de las tres referencias.

## La Hondonada: ilustración por capas y escaleras

Este incremento sustituye el pueblo modular provisional por la ilustración elegida
por el usuario. `images.hondonada_plate` carga
`assets/images/environments/hondonada_clean.png`: **1448×1086 RGB de 24 bits, fondo
negro opaco sin alfa**, salida de edición con `image_gen.imagegen`, copiada sin
alterar bytes. La edición solicitó retirar únicamente el personaje incrustado de
la plaza. La referencia original conserva sus bytes y hash; la salida generativa
no se presenta como idéntica píxel a píxel al original.
[Procedencia](../assets/provenance/hondonada-layered.md) ·
[Prompt exacto](../assets/provenance/hondonada-clean-prompt.md).

- El fondo opaco es intencional y propio de las placas registradas. No se aplica colorkey
  negro global: la esquina es `(2,2,2)` y hay sombras oscuras dentro del pueblo.
- La base y las máscaras de primer plano se derivan del mismo recurso registrado.
  Los recortes de oclusión se cachean en memoria, no se entregan PNG separados
  de edificios con traseras reconstruidas ni sprites reutilizables de toda la escena.
- La navegación se define por casillas y conexiones explícitas, con anclas de
  presentación y superficies de selección. Las escaleras autorizadas conectan
  recorridos; no basta con desplazar el sprite sobre la pintura. No hay física 3D,
  saltos ni acceso automático a tejados, agua o edificios cerrados.
- En este incremento de Hondonada, puesto/planta conservaban el atlas; El Puesto
  se integra posteriormente como se describe abajo. La fixture legacy conserva
  geometría explícita. NPC, diálogos nuevos, arena lateral y animaciones no
  formaron parte del cambio de Hondonada.
- La auditoría de recursos exige referencia no vacía con hash, prompt y procedencia
  para cada recurso IA. Las placas `hondonada_plate` y `puesto_plate` declaran
  `background: opaque_black`; los demás recursos mantienen transparencia validada.

**Redistribución pendiente** de referencia y placa: no atribuir CC0/BY-SA ni
publicar sin confirmación. La verificación automática y sus límites se registran
en [VALIDACION](VALIDACION.md); no equivalen a jugar manualmente todos los
recorridos ni revisar todos los solapamientos.

### Resultado histórico de verificación de Hondonada

La suite completa posterior al ajuste de navegación/ocultación de Hondonada dio
**106 pruebas correctas** (`Ran 106 tests in 10.530s`, SDL dummy, salida 0).
Este resultado no es el conteo actual tras integrar El Puesto. Los conteos de
75/96 corresponden a incrementos todavía anteriores. La prueba de visibilidad
de puente/porche comprueba que Vera
no desaparezca detrás de sus propias fachadas; no prueba oclusión perfecta en
cada píxel. Comando, capturas y límites en [VALIDACION](VALIDACION.md).

## El Puesto: ilustración explorable y guardias de combate

`images.puesto_plate` registra `assets/images/environments/puesto-clean.png`:
**1448×1086 RGB de 24 bits, fondo negro opaco sin alfa**, salida de edición con
`image_gen.imagegen`, copiada sin alterar bytes. Se solicitó retirar los cinco
guardias pintados para sustituirlos por actores del juego; la referencia
`assets/reference/scenarios/puesto.png` conserva su hash y sus bytes originales.
[Procedencia](../assets/provenance/puesto-layered.md) ·
[Prompt exacto](../assets/provenance/puesto-clean-prompt.md).

- El Puesto sustituye su presentación modular anterior por esta placa completa.
  Navegación y oclusión se registran aparte de los píxeles de la ilustración;
  no se obtiene transitabilidad automática de escaleras, tejados o carreteras.
- Los guardias móviles usan los PNG activos de personaje y las reglas de
  combate del juego. Los humanos retirados no son unidades ni ocupación lógica.
- Se mantiene la política explícita `background: opaque_black`, sin colorkey
  negro global; sprites y atlas no cambian su contrato de transparencia.
- La edición pidió mantener composición y encuadre, pero no garantiza identidad
  píxel a píxel fuera de las personas retiradas. Hashes y prompt identifican el
  resultado real; no certifican todos sus detalles artísticos ni solapamientos.

**Redistribución pendiente** de referencia y placa: no publicar sin confirmación
ni atribuir licencias no verificadas. El conteo actualizado de pruebas y los
límites de validación se registran en [VALIDACION](VALIDACION.md), no se infieren
de los resultados históricos de otros incrementos.

## Planta: ilustración explorable y válvula final (20/10/2026)

`images.planta_plate` carga **`assets/images/environments/planta-clean-v2.png`**,
1448×1086, fondo negro opaco. Se conserva el original
`assets/reference/scenarios/planta.png` y el primer intento intermedio
`planta-clean.png` (no cargado). La edición integrada con `image_gen.imagegen`
retira la pequeña figura incrustada del patio; tres guardias y jefe son actores
con reglas, vida y patrullas, no humanos pintados como sustituto de gameplay.

- [Procedencia y límites](../assets/provenance/planta-layered.md).
- [Prompts exactos de ambas pasadas](../assets/provenance/planta-clean-prompt.md).
- Hashes de referencia, intermedio y placa activa en `assets/manifest.json`.
- 72 nodos, 76 aristas, cinco escaleras y seis máscaras en `data/planta.json`.
  La máscara de la grúa oculta pasos detrás de su mástil: no es una pared lógica.
- Suelo y maquinaria proceden de la placa; la válvula y botiquines reutilizan
  frames del atlas acreditado. No se ejecuta IO ni recorte por frame.
- PNG de jefe escalado proporcionalmente, manteniendo su tamaño relativo y arma.

**Redistribución pendiente** de referencias y derivados; no se les atribuye una
licencia libre. La edición no garantiza identidad píxel a píxel fuera del objetivo.
Las capturas SDL dummy y pruebas no equivalen a jugar con audio nativo.

## Aldeano y marco de diálogo industrial — 21/10/2026

Se incorporan dos recursos activos:

- **`villager`**: `assets/images/characters/villager.png`, copia sin editar del
  artesano con taza (1254×1254 RGBA). Frame del cuerpo `[387,56,513,1168]`, ancla
  entre botas `[245,1135]`; escala proporcional al pueblo, sin tinte ni una vista
  trasera inventada. Dos NPC con IDs distintos reutilizan el mismo sprite.
- **`dialogue_frame`**: `assets/images/ui/dialogue-frame.png`, 2172×724 RGBA,
  derivado con la herramienta integrada `image_gen.imagegen`. Se retiraron nombre,
  frase y «Continuar» incrustados, conservando retrato, tuberías, metal oxidado,
  lámparas y telas. Exterior transparente; interior oscuro para texto dinámico.

La referencia original de ventana se conserva sin edición en
`assets/reference/ui/dialogue-reference.png`. El manifest registra hashes,
procedencia y regiones seguras para nombre, texto, continuación e instrucciones.
La prueba de referencias ahora admite `assets/reference/` (escenarios e interfaz),
sin aceptar rutas externas al proyecto. No hay IO ni reescalado de la skin por frame.

[Procedencia](../assets/provenance/villager-dialogue.md) ·
[Prompt exacto](../assets/provenance/dialogue-frame-prompt.md).

Los originales y el derivado tienen **redistribución pendiente de confirmación**;
no se les atribuye CC0/BY-SA. El archivo del aldeano y la referencia se conservan
sin modificar bytes. El prompt no garantiza identidad píxel a píxel del marco.

## Ataques de combate — 21/10/2026

Tres hojas originales suministradas (`vera_attack`, `guard_attack`, `boss_attack`)
de 2172×724 RGBA, copiadas sin cambiar bytes en `assets/images/characters/`.
El manifiesto añade hashes, rectángulos explícitos, polígonos de aislamiento,
anclas, referencia corporal y duraciones. No se usa grilla uniforme ni colorkey
negro; el alfa real y los colores interiores se conservan. Se preparan las dos
orientaciones y escalas por mapa al cargar, sin I/O por frame.

[Procedencia y derivación técnica](../assets/provenance/combat-attacks.md) ·
[Alcance, pruebas y límites](ATAQUES.md). Derechos de redistribución **pendientes**,
sin atribuirles la licencia de otros packs. No se incorporaron caminar ni ciclos
traseros; los dos ataques lógicos de Vera reutilizan su única secuencia aportada.
