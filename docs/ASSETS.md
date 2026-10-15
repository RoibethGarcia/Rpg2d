# Recursos de la primera iteración

Selección descargada el 15 de octubre de 2026 mediante los controles públicos de descarga gratuita de itch.io. Sin cuentas, pagos ni compras. No se redistribuyen archivos ZIP completos ni metadatos privados. `assets/manifest.json` es el contrato de carga; todos sus `path` son relativos a la raíz del proyecto, NO al directorio de trabajo. Incluye origen, autor, archivo original, licencia, modificaciones y SHA-256.

## Recursos integrados

| Recursos locales | Fuente y autor | Licencia | Cambios |
|---|---|---|---|
| `assets/images/human_front.gif`, `human_rear.gif` | [32px Isometric Modern Character Template — intellikat](https://intellikat.itch.io/isometric-character-template) | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) | Renombrado, bytes originales de `cycles/template-{front,rear}-stand.gif`. |
| `assets/images/pipes.png` | [Isometric Pipes — Darkmoonfire](https://darkmoonfire.itch.io/isometric-pipes) | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | Ninguno; hoja original `Isometric_Pipes.png`. Selección de rectángulo en tiempo de ejecución. |
| `assets/sounds/{click,confirm,error,back}.ogg` | [Interface SFX Pack 1 — ObsydianX](https://obsydianx.itch.io/interface-sfx-pack-1) | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) | Renombrado, bytes originales. Rutas originales precisas en manifiesto. |

Textos de licencia completos: `assets/licenses/CC0-1.0.txt` (incluido en ZIP de intellikat) y `assets/licenses/CC-BY-SA-4.0.txt` (texto oficial Creative Commons). Para tuberías se conserva autor, enlace y licencia; cualquier modificación artística derivada debe identificarse y compartirse bajo BY-SA 4.0. No aplicar esa licencia indiscriminadamente a todo el código del juego.

### Contrato gráfico

- `images.human_front` y `human_rear`: GIF indexado 32×32, color transparente magenta `(255,0,255)`, apoyo `[16,31]`. Pygame detecta el colorkey; al convertir, preservar transparencia (`convert_alpha` o copia con colorkey). Los PNG gigantes del ZIP están ampliados y NO se usan.
- Solo dos orientaciones originales: frente y espalda. Espejo horizontal permite las direcciones laterales; no implica cuatro vistas originales ni animaciones completas.
- Son plantillas humanas monocromas, NO diseños terminados de Vera o La Custodia. Se distinguen mediante color/etiqueta/círculo del rol en el render. No incluir armas adicionales por las animaciones de ejemplo del pack.
- `images.pipes`: hoja RGBA 192×512; 6 columnas de 32 px, 16 filas. Cuatro variantes, en bandas de cuatro filas: estándar, óxido, plata, azul. `frame:[32,128,32,32]` selecciona un segmento oxidado. Apoyo local `[16,28]` para esa celda; no usarlo para toda la hoja.
- Dibujar suelo 2:1 de 64×32 mediante código. Escalado humano a 64×64 con nearest-neighbor si se desea; escalar también el anclaje. Lógica del mapa independiente del arte.

### Contrato sonoro

`sounds.click`, `confirm`, `error` y `back` son OGG decodificables por el mixer de Pygame. Los originales duran 6 segundos (incluyen cola/silencio); no se recortaron. Volumen inicial discreto y canales limitados en la UI para evitar acumulación. Las pruebas usan audio dummy: verifican decodificación, NO calidad audible ni adecuación musical. Revisión con dispositivo real pendiente.

## Recursos NO integrados

[SBS Floor Pack](https://screamingbrainstudios.itch.io/isotilepack), [Wall Pack](https://screamingbrainstudios.itch.io/isowallpack) y [Object Pack](https://screamingbrainstudios.itch.io/isometric-object-pack) anuncian CC0 en sus páginas. La descarga de piso respondió HTTP 429; no se reintentó ni se cambió de vía para eludirlo. NO hay archivos SBS integrados y no deben presentarse como tales.

Suelo, paredes, bomba, depósito, panel, credencial, llave y botiquín son representaciones geométricas provisionales dibujadas por código Pygame del proyecto. No se generó arte raster. Se distinguen expresamente de los tres packs realmente incorporados.

## Verificación

`python -m unittest tests.test_assets -v` comprueba existencias, rutas confinadas, procedencia, licencias, hashes, dimensiones, transparencia, frame y anclaje, además de decodificación de audio. No descarga nada durante las pruebas. `view_image` permitió revisar visualmente la hoja de tuberías y la plantilla; la calidad de composición en juego y el sonido real requieren revisión manual.
