# Planta de distribución — ilustración explorable

- Fuente: `assets/reference/scenarios/planta.png`, aportada por el usuario.
- Original conservado sin editar; dimensiones: 1448×1086. Placa activa:
  `assets/images/environments/planta-clean-v2.png`, edición con `image_gen` para
  retirar una pequeña figura incrustada del patio, sin sustituir el original.
  `planta-clean.png` conserva el primer intento intermedio (no se carga).
- Autoría declarada por el usuario: generada con ChatGPT. No se atribuye autoría
  humana verificada ni una licencia CC0/BY-SA. **Redistribución pendiente de
  confirmación**, igual que los personajes aportados.
- Registro y SHA-256: `images.planta_plate` en `assets/manifest.json`.
- Prompts exactos de ambas pasadas: `planta-clean-prompt.md`. El primer intento
  aún mostraba la figura; la segunda pasada la retira visualmente. La edición no garantiza igualdad
  píxel a píxel fuera del objetivo. Se revisa la navegación contra la placa final.
- Derivados en memoria: escala proporcional y máscaras RGBA de los depósitos,
  reactor y baranda.
- `data/planta.json` define suelo, escaleras, conexiones, máscaras, encuentros y
  objetos independientemente del bitmap. No se deducen colisiones por color.
- Vera, tres guardias y jefe son actores reales; los suministros y la válvula
  final son objetos interactivos. La válvula reutiliza el frame del atlas ya
  acreditado, sin convertir la maquinaria pintada en actores o recursos.
- La entrada jugable está dentro del portón cerrado: el exterior inferior,
  superficies de agua y tejados no se presentan como caminos transitables.

Revisión mediante capturas SDL dummy separada de una partida manual nativa.
