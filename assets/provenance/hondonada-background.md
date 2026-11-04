# Paisaje de fondo de La Hondonada — 04/11/2026

Imagen aportada por el usuario en esta conversación:
`450d10ea-6825-48a2-b2fa-906d7214f749.png`, PNG RGB opaco de **1448×1086**.
Se copia sin modificar sus bytes a
`assets/images/environments/hondonada_background.png`; SHA-256 en el manifiesto.
No hay autoría, modelo de generación, licencia ni enlace público verificados.
**Redistribución pendiente de confirmación**, sin atribuirle una licencia libre.

## Composición en ejecución

- Se prepara una vez: escala proporcional para cubrir `WORLD_RECT` y recorte
  central, sin deformar la imagen. Solo aparece en La Hondonada.
- Es una capa fija de pantalla detrás del mundo, sin animación ni seguimiento
  de cámara. No se amplía con el zoom del escenario.
- La placa original `hondonada_clean.png` es RGB con negro opaco, NO RGBA. Sus
  bytes y hash permanecen intactos. Una máscara cacheada elimina solo los píxeles
  casi negros (cada canal RGB ≤ 12) conectados al borde, incluyendo zonas que
  ya tengan alfa cero. Se prepara antes de escalar tanto base como primeros planos.
- No se aplica un colorkey global: las sombras negras interiores cerradas y el
  alfa existente se conservan. El umbral está ajustado a esta placa; cambiar de
  ilustración requiere revisar su silueta. No es una segmentación semántica.
- El mundo se compone con alfa en los buffers reutilizables y se superpone al
  paisaje después del recorte/zoom. Proyección, anclas, actores, objetos, UI,
  navegación, colisiones y mapas restantes no cambian.

El fondo no añade casillas seleccionables ni transitables. Las capturas y pruebas
con SDL dummy no sustituyen la revisión visual nativa de bordes y legibilidad.
