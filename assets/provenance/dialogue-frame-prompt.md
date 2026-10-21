# Prompt exacto — ventana de diálogo sin texto

Fecha: 21 de octubre de 2026. Herramienta integrada `image_gen.imagegen`,
`transparent_background: true`. Objetivo de edición: la imagen aportada por el
usuario, conservada en `assets/reference/ui/dialogue-reference.png`.
Salida seleccionada: `assets/images/ui/dialogue-frame.png`.

```text
Use case: precise-object-edit. Asset type: transparent PNG dialogue-window skin for a Pygame post-apocalyptic RPG. Edit target: the attached 2172x724 dialogue panel. Keep the exact same industrial pixel-art metal frame, rusty pipes, orange lamps, blue/red hanging cloth, left villager portrait, composition, panel positions and proportions. Remove ALL baked lettering: the title 'Aldeano', the entire Spanish dialogue sentence, and 'Continuar'. Also remove the small triangle beside Continuar. Reconstruct the blank dark textured nameplate and blank dark dialogue interior seamlessly, leaving these interiors opaque so dynamic text stays readable. Do NOT remove the portrait, decorate the empty text region, add any lettering, redraw the character or change the framing. Outside the frame must remain genuinely transparent RGBA (not an opaque black rectangle). All holes outside and around hanging ornaments remain transparent; inside portrait and name/text plates stay opaque. Preserve the 3:1 aspect and 2172x724 pixel canvas if possible. No text anywhere, no watermark, no UI labels.
```

Se verificó visualmente la ausencia del texto y el exterior transparente. Los
originales no se alteran; hashes y regiones de texto dinámico en el manifest.
