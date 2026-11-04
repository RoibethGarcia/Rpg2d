# Cascada ambiental de La Hondonada — 30/10/2026

Recurso aportado por el usuario en esta conversación: **«Sprite de cascadas
pixeladas transparentes.png»**, generado con ChatGPT según su declaración.
Se conserva una copia de los bytes originales en
`assets/images/effects/waterfall.png`; dimensiones **1774×887**, alfa real,
ocho poses en cuatro columnas y dos filas. Hash SHA-256 en `assets/manifest.json`.
No se atribuye una licencia libre: **redistribución pendiente de confirmación**.
No hay enlace público de origen ni autoría humana independientemente verificada.

## Preparación en ejecución

- La hoja no cumple los 1024×512 pedidos. Las fronteras de celda se calculan con
  división entera para repartir correctamente los píxeles impares, sin perder la
  última fila/columna ni mezclar poses.
- En cada celda se usa el MISMO recorte relativo `[140,18,210,400]`; no se centra
  cada silueta por su caja alfa, evitando desplazar la caída entre cuadros.
- Se preparan ocho superficies una sola vez, a la escala del mapa, con máscara
  de agua y opacidad 150/255. No se vuelve a cargar, recortar ni escalar por frame.
- `data/hondonada.json` declara la posición en píxeles de autoría de la placa y
  el polígono que excluye la tubería/rocas. Esta máscara NO concede transitabilidad.
- El reloj existente de partida, en segundos, selecciona un cuadro cada **0.1 s**;
  ciclo de **0.8 s**, sin callbacks sobre combate, PA ni movimiento. Durante el
  diálogo se pausa junto al mundo y una partida nueva vuelve al primer cuadro.
- Se compone sobre la base y detrás de los actores/capas delanteras, antes del
  zoom. Puesto y planta no tienen esta configuración ni reciben el efecto.

Es una superposición sobre el agua que ya estaba pintada: no se redibuja la placa
ni se pretende animar toda la superficie del arroyo. La continuidad artística
entre poses depende de la hoja aportada; un ciclo matemático no certifica un
movimiento perfecto. Las capturas con SDL dummy no equivalen a una partida
manual nativa ni a comprobar sonido.
