# Aldeano y ventana de diálogo — 21/10/2026

## Originales aportados por el usuario

- `assets/images/characters/villager.png`: copia sin editar de
  `Artesano del Yermo con Taza.png`, 1254×1254, RGBA. El original tiene algunos
  píxeles aislados de alfa en los bordes; el frame del cuerpo es
  `[387,56,513,1168]`, sin modificar bytes, con ancla local `[245,1135]` entre
  los apoyos de las botas. Se escala proporcionalmente, sin tinte ni espalda inventada.
- `assets/reference/ui/dialogue-reference.png`: copia sin editar de
  `Imagen de ChatGPT 20 oct 2026, 00_25_56.png`, 2172×724, RGBA. Marco industrial
  con retrato, nombre, frase y botón incrustados; se conserva como referencia.

Son recursos aportados por el usuario, declarados generados con ChatGPT. No se
atribuye autoría humana verificada ni una licencia libre. **Redistribución
pendiente de confirmación**, igual que los personajes y escenarios anteriores.

## Derivado e integración

- `assets/images/ui/dialogue-frame.png`: edición integrada con
  `image_gen.imagegen`, sin texto/triángulo incrustado y con exterior transparente.
  Se conserva el retrato del aldeano, metal oxidado, tuberías, luces y telas.
  Interior oscuro de alta opacidad para texto legible. [Prompt exacto](dialogue-frame-prompt.md).
- La salida se copió al proyecto sin editar sus bytes. El prompt no garantiza
  igualdad píxel a píxel fuera de lo solicitado.
- Rutas, hashes SHA-256, dimensiones, anclas y regiones seguras del marco en
  `assets/manifest.json` (`villager`, `dialogue_frame`). Sin dependencia de Downloads
  ni de la caché de generación al ejecutar el juego.
- Dos habitantes con IDs, textos e historial independientes reutilizan el sprite
  estático. No son enemigos ni compañeros y no otorgan suministros, curación o PA.
- La ventana conserva proporción 3:1, dibuja nombre/páginas/continuación mediante
  Pygame y pausa el mundo. Recursos cargados una vez; no hay IO por frame.

La revisión con SDL dummy comprueba representación, no una partida manual nativa
ni sonido audible. No publicar los recursos sin confirmar sus derechos.
