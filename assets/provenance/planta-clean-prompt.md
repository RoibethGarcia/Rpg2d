# Prompt exacto — placa limpia de la Planta

Fecha: 20 de octubre de 2026. Herramienta integrada: `image_gen.imagegen`.
`transparent_background: false`. Referencia original conservada sin cambios:
`assets/reference/scenarios/planta.png`. Salida copiada sin editar sus bytes a
`assets/images/environments/planta-clean.png`. No se utilizó CLI/API alternativa.

```text
Use case: precise-object-edit. Edit target: the supplied isometric industrial plant illustration, 1448 x 1086 pixels. Remove ONLY the tiny painted human guard standing near source x274,y530 in the lower-left inner entry yard (blue/gray clothing, beside the wooden crate and vertical gate structure). Seamlessly reconstruct the floor behind that one person. Do not remove crates, pipes, barrels, machinery, lights, posts, fences or control consoles. Invariants: EXACT same pixel-registered framing, composition, dimensions, isometric geometry, all floor/stair/walkway/rail/tank/reactor positions, lighting, texture, sharpness and opaque black surrounding background. No people, no new objects, no text, no labels, no HUD. This image is a game background registered to hand-authored navigation: absolutely no camera shift or redesign. Keep all other content as unchanged as possible.
```

El prompt expresa las restricciones solicitadas, no una garantía de conservación
píxel a píxel. Procedencia, hashes y derechos pendientes en el manifest y
`planta-layered.md`.

## Segunda pasada — salida activa

La primera inspección aún mostraba la pequeña figura. Segunda edición sobre
`planta-clean.png`, misma herramienta y fondo opaco, copiada sin editar sus bytes
a **`assets/images/environments/planta-clean-v2.png`**. Esta es la placa cargada;
la primera salida queda como intermedio documentado.

```text
Use case: precise-object-edit. The edit target is the supplied 1448x1086 isometric factory image. There is STILL a small blue-uniform HUMAN standing in the left inner courtyard at approximately x272,y529 (head near x273,y514, boots near x274,y543), just RIGHT of the wooden crate at x244,y530, LEFT of the tall crane pillar at x312,y510, below the suspended hook. REMOVE THIS ENTIRE SMALL PERSON, including head, blue torso, arms, legs, boots and shadow; replace their pixels with the natural tan courtyard floor and background wall. It must be visibly empty floor where this blue person stands, not a recolored person, not another cylinder or barrel. This is the ONLY requested change. Pixel-registered geometry is critical for game navigation. Preserve 1448x1086 dimensions, opaque black background, ALL stairs/floors/railings/crates/tanks/reactor/valves/pipes/lighting/camera positions/composition and sharpness. Do not redesign the environment. No people, no text, no UI.
```
