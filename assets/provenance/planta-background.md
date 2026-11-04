# Paisaje de fondo de la Planta — 04/11/2026

Recurso aportado por el usuario: **«Cañón industrial al atardecer (1).png»**,
PNG RGB opaco de **1448×1086**, copiado sin modificar sus bytes a
`assets/images/environments/planta_background.png`. SHA-256 en el manifiesto.
Autoría, licencia y modelo de generación no verificados; **redistribución
pendiente de confirmación**, sin atribuirle una licencia libre.

**«Instalación industrial al atardecer.png»** es la referencia de composición,
no una imagen activa del juego. Ya contiene personajes, barras y etiquetas:
no se carga como mapa, fondo ni interfaz, para no duplicarlos. Se conserva la
placa limpia jugable actual, no se regenera el escenario para imitar el montaje.

Por cambio explícito del usuario, este cañón con terrazas de terreno sustituye
al fondo anterior **«Atardecer industrial entre montañas y niebla.png»**. El lago
anterior ya no se carga: se reemplazó el contenido de la misma ruta de recurso
y su hash para evitar la apariencia de una instalación flotando sobre el agua.

## Preparación y alcance

- Reutiliza los fondos fijos de Hondonada y puesto: escala proporcional para
  cubrir `WORLD_RECT` y recorte central preparados una sola vez, fuera del
  zoom y seguimiento de cámara. No hay animación ni I/O por frame.
- La placa activa es **`planta-clean-v2.png`**, no el primer intento intermedio
  `planta-clean.png`. Conserva sus bytes, hash, tamaño y coordenadas.
- Como la placa es RGB con negro opaco, se prepara alfa en memoria únicamente
  para el casi negro exterior conectado a los bordes (RGB ≤ 12), antes de escalar
  la base y las capas de oclusión. No se aplica colorkey global ni se borran las
  sombras interiores cerradas no seleccionadas. La semilla `[150,420]`, declarada
  en `planta_plate.exterior_seeds`, identifica además el hueco de paisaje cerrado
  por el pórtico de entrada; elimina solo su componente casi negro y conserva
  la viga y el resto del decorado.
- El paisaje se dibuja detrás del mundo transparente, sin añadir colisiones,
  casillas seleccionables ni exploración. Proyección, navegación, anclas,
  actores, objetos, válvula, etiquetas e interfaz conservan sus posiciones.
- Viajar puesto↔planta selecciona el fondo correspondiente sin recargarlo;
  Hondonada y puesto mantienen sus recursos y máscaras anteriores.

El viewport panorámico recorta arriba/abajo del paisaje sin deformarlo; por ello
la composición no es idéntica píxel a píxel a la referencia de proporción 4:3.
El umbral es una máscara de presentación, no segmentación semántica: otra placa
requiere revisar sus bordes. Capturas SDL dummy no sustituyen revisión nativa.
