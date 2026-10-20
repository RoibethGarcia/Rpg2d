# Procedencia del atlas modular de escenarios

## Generación

- Fecha: 2026-10-19.
- Modo: herramienta integrada `image_gen.imagegen`, sin CLI, API ni claves.
- Tipo: nuevo atlas modular inspirado en tres referencias del usuario; no es un recorte ni una reproducción completa de los escenarios.
- Solicitud: `transparent_background: true`; `referenced_image_paths` contiene las tres rutas originales indicadas abajo.
- Resultado de producción: `assets/images/environments/scenario_atlas.png`, PNG RGBA de **1254 × 1254** píxeles.
- SHA-256: `c0d05847b334edd2cee168a7a2b00b75c0afe8fb8169ca32dadae6605647d032`.
- Artefacto de origen: `/Users/roibethgarcia/.codex/generated_images/01a154ea-eb4a-7322-939a-368bcbc76d9d/exec-825147dd-d1af-44d7-b7c7-8ffbfd209fd9.png`.
- El archivo de producción es una copia byteidéntica del resultado generado, sin posprocesado ni edición del bitmap. El juego debe consumir la copia del proyecto, no depender de `.codex` ni Downloads.
- Las referencias provienen del usuario; no se ha establecido una licencia pública ni se les atribuye la licencia de los assets anteriores. Confirmar derechos y condiciones antes de redistribuir.

## Referencias conservadas

| Uso | Original suministrado | Copia byteidéntica en el proyecto |
| --- | --- | --- |
| Pueblo y estación | `/Users/roibethgarcia/Downloads/Imagen de ChatGPT 19 oct 2026, 11_54_08.png` | `assets/reference/scenarios/hondonada.png` |
| Puesto de control | `/Users/roibethgarcia/Downloads/Imagen de ChatGPT 19 oct 2026, 11_54_23.png` | `assets/reference/scenarios/puesto.png` |
| Planta final | `/Users/roibethgarcia/Downloads/Imagen de ChatGPT 19 oct 2026, 11_54_30.png` | `assets/reference/scenarios/planta.png` |

## Inspección y recortes de consumo

La generación produjo 16 módulos separados con alfa real, comprobado en metadatos PNG/Pygame y visualmente. Las esquinas tienen alfa cero. **No respetó una cuadrícula exacta de 256 × 256 ni la resolución solicitada**: no se debe dividir el atlas uniformemente entre cuatro. No se regeneró ni se pintó una cuadrícula alternativa: los consumidores deben utilizar los recortes explícitos siguientes `(x, y, ancho, alto)`, medidos sobre componentes de máscara con alfa mayor que 127.

Hay píxeles con alfa muy bajo dispersos fuera de las figuras; `get_bounding_rect(min_alpha=1)` no identifica los módulos correctamente. Las coordenadas siguientes recogen la silueta opaca relevante sin incluir otros módulos. El atlas permanece intacto.

Se observan halos rojos residuales en algunos bordes a escala fuente. No aplicar un filtro global por color rojo: eliminaría partes legítimas de la barrera, el botiquín y otros detalles. El renderer puede ampliar los recortes **2 píxeles por cada lado** para preservar el contorno sin mezclar figuras vecinas.

| Fila temática | Módulo | Rectángulo explícito |
| --- | --- | --- |
| Pueblo | Suelo de piedra | `(16, 168, 289, 155)` |
| Pueblo | Muro bajo | `(343, 120, 252, 194)` |
| Pueblo | Caseta de estación | `(629, 52, 295, 272)` |
| Pueblo | Puesto de mercado | `(960, 62, 270, 259)` |
| Control | Suelo de hormigón | `(16, 483, 290, 157)` |
| Control | Barrera | `(363, 480, 218, 161)` |
| Control | Caseta de guardia | `(654, 331, 254, 308)` |
| Control | Cajas | `(971, 432, 252, 199)` |
| Planta | Suelo de rejilla | `(16, 796, 290, 155)` |
| Planta | Muro con tubería | `(353, 701, 248, 230)` |
| Planta | Tanque | `(687, 649, 208, 305)` |
| Planta | Bomba | `(952, 712, 278, 233)` |
| Comunes | Botiquín | `(102, 1074, 115, 113)` |
| Comunes | Panel | `(358, 981, 205, 215)` |
| Comunes | Válvula | `(660, 1029, 236, 164)` |
| Comunes | Vías | `(947, 1030, 293, 171)` |

Para props y obstáculos usar el centro inferior de la base como ancla; para suelos, alinear el centro del rombo con el centro de la casilla. Las dimensiones finales y el recorte de suelo a rombo navegable pertenecen al renderer y no cambian las colisiones. El atlas contiene ilustraciones, no metadatos de navegación.

## Prompt exacto

```text
+Use case: stylized-concept
Asset type: Production modular isometric pixel-art game environment sprite atlas, one PNG, square 1024x1024.
Input images: Image 1 is STYLE AND MATERIAL REFERENCE ONLY for town station / market with teal cloth; Image 2 is STYLE AND MATERIAL REFERENCE ONLY for guarded industrial checkpoint with red cloth and concrete barriers; Image 3 is STYLE AND MATERIAL REFERENCE ONLY for final rusted machinery plant with pipes and tanks. Do not reproduce any full scene. Do not alter original reference files.
Primary request: Reconstruct useful individual modular environment pieces from the references into a SINGLE TRANSPARENT 4 columns by 4 rows uniform sprite atlas: 16 isolated complete sprites, exactly one per 256x256 cell. No visible grid. Every sprite wholly inside its cell with at least 16px transparent margin; no touching adjacent sprite or crossing cell edge. Position each base centered near the lower part of its cell, consistent isometric ground plane. 
Read cells left to right, top to bottom:
Row 1 TOWN: (1) cracked sandstone pavement ground diamond, exact isometric 2:1 top footprint, flat tile with minimal thickness; (2) one-tile low weathered stone wall block with rusty metal patches; (3) small compact railway station kiosk with teal awning; (4) compact market stall with teal fabric canopy.
Row 2 CHECKPOINT: (1) worn concrete pavement ground diamond, exact isometric 2:1 top footprint, flat tile minimal thickness; (2) one-tile low concrete security barrier with red industrial diagonal markings; (3) compact guard booth with red cloth canopy; (4) small stack of rugged industrial metal crates.
Row 3 PLANT: (1) rusty metal grate pavement ground diamond, exact isometric 2:1 top footprint, flat tile minimal thickness; (2) one-tile low industrial wall block with attached horizontal pipe; (3) compact vertical cylindrical rusty storage tank; (4) compact industrial pump machine with pipes.
Row 4 SHARED: (1) small red and white metal first-aid kit; (2) freestanding industrial control panel with amber and teal lights; (3) compact rusty pipe valve assembly with red hand wheel; (4) a short straight rail segment with sleepers on a flat isometric 2:1 diamond tile.
Style: Cohesive crisp hand-crafted pixel art matching the references, restrained amber/rust/tan/teal palette, readable at 48 pixel game scale, consistent 2:1 isometric orthographic camera, light from upper left. Do not use perspective. Structures modestly tall and compact; all floors consistent 2:1 diamond.
Background: GENUINE fully transparent alpha, not black, white, gray, checkerboard or a backdrop. No cast floor shadow outside objects. Padding transparent.
Constraints: NO characters, NO text, NO labels, NO logos, NO watermark, NO visible panels or gridlines, NO complete landscape, NO tall cliffs, NO stairs, NO multi-level walkways, NO overlapping cells. Each cell contains one module only.
```
