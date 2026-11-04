# Paisaje de fondo del Puesto de Control — 04/11/2026

Recurso aportado por el usuario: **«Paisaje industrial al atardecer.png»**,
PNG RGB opaco de **1448×1086**, copiado sin modificar sus bytes a
`assets/images/environments/puesto_background.png`. SHA-256 en el manifiesto.
Autoría, licencia y modelo de generación no verificados; **redistribución
pendiente de confirmación**, sin atribuir una licencia libre.

La segunda imagen, **«Planta industrial al atardecer.png»**, se usa únicamente
como referencia de la composición deseada. Contiene personajes y etiquetas
ya pintados: NO se carga como mapa, fondo ni interfaz, para no duplicarlos.
La composición no es una reproducción píxel a píxel de esa referencia: conserva
la placa jugable actual y utiliza el paisaje independiente del primer adjunto.

## Preparación y alcance

- Reutiliza el fondo fijo de Hondonada: escala proporcional para cubrir
  `WORLD_RECT` y recorte central, preparado una sola vez, fuera del zoom/cámara.
- La placa `puesto-clean.png` conserva bytes, tamaño y coordenadas. Como es RGB
  con negro opaco, se prepara en memoria una máscara para el negro exterior
  conectado a los bordes (RGB ≤ 12), antes de escalar base y capas delanteras.
  La semilla explícita `[100,240]`, declarada en `puesto_plate.exterior_seeds`,
  identifica además el hueco de paisaje cerrado por el cable de la torre oeste:
  elimina solo su componente casi negro, conservando el cable y las sombras
  interiores no seleccionadas. No hay colorkey global.
- Se dibuja detrás del mundo transparente. No añade animación, colisiones,
  casillas seleccionables ni exploración, y no cambia anclas, proyección,
  navegación, enemigos, objetos, etiquetas o posiciones de interfaz.
- Cada escenario mantiene su fondo: viajar Hondonada↔puesto selecciona la
  imagen correspondiente sin recargarla. La planta tiene su propio paisaje,
  incorporado posteriormente y documentado en `planta-background.md`.

El encuadre panorámico de la vista de juego recorta arriba/abajo del paisaje
original. No se deforma ni se modifica el layout para imitar el montaje. El
umbral requiere revisión con otras placas; no constituye segmentación semántica.
Las capturas con SDL dummy no sustituyen la revisión manual en una ventana nativa.
