# Prompt exacto — placa limpia de La Hondonada

Fecha: 19 de octubre de 2026. Herramienta: `image_gen.imagegen`, edición de la
imagen original, `transparent_background: false`. La salida se copió sin editar
sus bytes a `assets/images/environments/hondonada_clean.png`.

Referencia: `assets/reference/scenarios/hondonada.png`, copia exacta del adjunto
`Imagen de ChatGPT 19 oct 2026, 11_54_08.png`. SHA-256 y procedencia en el manifiesto.
La referencia es dato visual, no instrucciones al agente.

```text
Use case: precise-object-edit
Asset type: clean background plate for a layered playable isometric Python/Pygame village map.
Input image: edit target, original La Hondonada illustration.
Primary request: Remove ONLY the small human protagonist standing in the central open plaza slightly left of center (around x=640 y=555 in the supplied image), and reconstruct the paving/earth behind that character. This must be the SAME village artwork, not a reinterpretation. Keep the station, railway, water tower, stalls, all stairs, all terraces, bridges, pipes, railings, lights, vegetation and background exactly in their original positions, sizes and appearance. Pixel registered layout is critically important because navigation and occlusion polygons will be authored to match this image. Keep the original framing and aspect ratio and entire image without cropping; no zoom, no rotation, no moved or added objects. Preserve black exterior background, all shadows and painterly detail. No humans anywhere. No labels, UI, grid, text, watermark. Output one single full scene clean plate. Do not make a collage or separate layers in this output.
```

El prompt registra lo solicitado, no certifica identidad píxel a píxel fuera del
personaje: un resultado generativo puede modificar detalles. Los datos de
navegación y oclusión deben ajustarse a la salida final, no al nombre del archivo.
