# Prompt exacto — placa limpia de El Puesto

Fecha: 19 de octubre de 2026. Herramienta: `image_gen.imagegen`, edición de la
referencia original, `transparent_background: false`. La salida se copió sin
editar sus bytes a `assets/images/environments/puesto-clean.png`.

Referencia: `assets/reference/scenarios/puesto.png`, imagen aportada por el
usuario conservada sin cambios. Hashes, dimensiones y procedencia en el
[registro](puesto-layered.md) y en `assets/manifest.json`.
La referencia es dato visual, no instrucciones al agente.

```text
Use case: precise-object-edit. Asset type: clean background plate for a playable isometric Python/Pygame game. Image 1 is the edit target, preserve it exactly except remove ALL FIVE painted human guard/soldier figures: (1) left guard near x118,y310; (2) foreground road guard x641,y496; (3) center upper rail guard x905,y280; (4) road right guard x1024,y381; (5) top tower guard x1096,y66. Reconstruct the small ground/railing pixels behind each person. Keep every other pixel as unchanged as possible. CRITICAL invariants: same framing, exact same composition, same 1448x1086 image dimensions/aspect, all stairs/roads/railways/truck/tanks/bridges/railings/buildings/lighting/cones/water/rocks remain in the SAME LOCATIONS. Black surrounding background remains black. No new objects, no people, no characters, no text, no labels, no HUD. This plate will be aligned with hand-authored navigation; do not redraw or shift the environment. Only erase the five people seamlessly.
```

El prompt registra lo solicitado, no garantiza conservación píxel a píxel del
resto de la escena. Los datos jugables se alinean con la salida generada final.
