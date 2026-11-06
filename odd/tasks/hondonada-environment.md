# Efectos ambientales de La Hondonada

Implementación autorizada: escenario 1; sin reconstruir mapas, sin builds,
instalaciones, commits, publicaciones ni subagentes. TDD estricto, Python -B y SDL
dummy. Documento de alcance: `docs/efectosVisuales1.md`.

## Specs

- S1 — «modifica el documento para que efectivamente diga escenario 1, luego
  implementa». Todas sus referencias deben identificar La Hondonada.
- S2 — «NO MODIFICAR LA ESTÉTICA NI RECONSTRUIR EL MAPA». Conservar bytes de
  ilustraciones, navegación, colisiones, AP, turnos, actores e interacciones.
- S3 — «Aves: Sprites transparentes independientes»; aleteo, curvas suaves,
  velocidades/fases variadas, máximo configurable de 0–5, lejos del centro.
- S4 — «Humo: Sistema de partículas translúcidas»; expansión, viento y fundido;
  emisiones desde conductos existentes y vapor intermitente; cupo acotado.
- S5 — «Agua: Spritesheet y máscara localizada sobre el agua original»;
  reutilizar cascada, añadir ondas sutiles en río, no cubrir rocas ni suelo.
- S6 — «Utilizar delta time», «No cargar imágenes desde disco en cada frame»,
  «Permitir activar o desactivar los efectos», no actualizar mapas inactivos;
  configurar intensidad, aves, emisión y velocidad de agua sin menú nuevo.
- S7 — Fidelidad y estabilidad antes que cantidad: pruebas de FPS, máscara,
  pausa/reset/viaje, caché, transformaciones, clip y aislamiento del gameplay;
  inspeccionar capturas sin atribuirles validación manual nativa.

## Tasks

| ID | Specs | Ruta | Estado | Evidencia |
| --- | --- | --- | --- | --- |
| T1 | S1 | docs/efectosVisuales1.md | completo | Referencias corregidas y tabla de técnicas añadida. |
| T2 | S2–S7 | tests/test_environment_effects.py, tests/test_waterfall.py | completo | 17 pruebas nuevas GREEN en 1.489 s; RED válido de feature y correcciones. Cascada aislada sin debilitar sus aserciones. |
| T3 | S3–S6 | game/ambient.py, data/hondonada.json | completo | Sprites/texturas cacheados, PNG de aves opcional, cupos/configuración/tiempos. Emisores verificados: estufa y junta de depósito; río localizado lejos de orilla. |
| T4 | S2,S5–S7 | game/environment.py, game/render.py, game/scenes.py | completo | Fondo fijo antes de mundo; humo/cascada antes de actores/capas. Reloj por delta del tiempo simulado, actualización solo mapa activo, reset por contexto. |
| T5 | S1–S7 | docs/efectosVisuales1.md, docs/EFECTOS_AMBIENTALES.md, README.md | completo | 300 pruebas OK en 96.527 s; diff, enlaces y datos previos verificados. Capturas finales 100%/150% y máscaras inspeccionadas; revisión humana nativa pendiente y explícita en documentación. |

## Log

- Solicitud original: «lee efectosVisuales1.md, toma las siguientes
  recomendaciones» (aves: sprites transparentes; humo: partículas translúcidas;
  agua: spritesheet y máscara localizada), con imagen de referencia.
- Autorización posterior textual: «modifica el documento para que efectivamente
  diga escenario 1, luego implementa».
- Exploración: `WaterfallAnimation` ya cachea ocho poses con máscara;
  `draw_layered` dibuja cascada tras base y antes de actores/capas. El paisaje es
  fijo, recortado para cubrir viewport; placa y cascada pasan por zoom. Solo hay
  un spritesheet ambiental (`waterfall.png`). Se inspeccionaron ambas imágenes
  y captura inicial `/tmp/rpg-ambient-before.png` con SDL dummy.
- Enfoque: siluetas de aves lejanas con alas curvas antialias, texturas de humo
  suaves irregulares y hoja de ondas RGBA generadas una vez desde código, sin
  editar imágenes originales ni incorporar recursos externos. Datos de río en
  coordenadas de su imagen; emisores en coordenadas de la placa. Reutilizar
  `WaterfallAnimation` también para preparar la hoja de ondas localizada.
- Estado inicial: únicamente docs/efectosVisuales1.md estaba sin seguimiento.
- RED: `.venv/bin/python -B -m unittest discover -s tests -p
  test_environment_effects.py -v` con SDL dummy y PYTHONDONTWRITEBYTECODE=1:
  12 fallos de aserción por `LayeredEnvironmentArt.effects` ausente, 1.130 s.
- GREEN inicial: 12 pruebas nuevas correctas en 1.407 s; sin builds. Un error de
  sintaxis durante la implementación fue corregido antes del GREEN (no se cuenta
  como RED). Suite completa ejecutada posteriormente, resultados abajo.
- Inspección visual: el supuesto conducto de techo en (505,46) es un pórtico,
  NO chimenea; retirado. Emisor principal ajustado a (330,464) y vapor a junta
  real (838,157). Máscaras de río desplazadas al interior del agua. RED observado
  con prueba de emisor inexistente; GREEN de 15 pruebas en 1.346 s.
- Ráfagas: prueba adicional detectó intervalos uniformes (RED). Se añadió una
  secuencia de silencios distintos, compartida por partículas del emisor y
  determinista respecto al tiempo, no a los FPS: GREEN 16 pruebas en 1.513 s.
- Refactor: `WaterfallAnimation` movida SIN cambiar comportamiento a
  `game/ambient.py`, reexportada desde `game/environment.py`; evita dependencia
  circular y permite reutilizar su preparación/máscara para el río.
- Primera suite completa: 295 pruebas OK, 99.223 s (antes de últimas correcciones).
- Segunda suite: 299 pruebas OK en 96.147 s; capturas finales inspeccionadas a
  100%/150%, máscaras dentro de zonas de agua. Humo con textura algo más amplia
  para evitar puntos aislados; retirado emisor del techo. Sin validación nativa.
- Configuración extrema: nueva prueba detectó reciclado prematuro de humo con
  frecuencia 3 (RED: desaparecía en etapa 14 antes del fade-out). Se limita el
  periodo mínimo de cada plaza a su vida completa + .02 s; la frecuencia se
  satura en lugar de cortar partículas. Prueba de regresión añadida; GREEN de
  17 pruebas en 1.489 s.
- Cierre: `.venv/bin/python -B -m unittest discover -s tests -v` con
  PYTHONDONTWRITEBYTECODE=1, SDL_VIDEODRIVER=dummy y SDL_AUDIODRIVER=dummy:
  **300 pruebas OK en 96.527 s**. `git diff --check`, whitespace de archivos
  nuevos y enlaces locales correctos. JSON previo byte-semánticamente idéntico
  al excluir `ambient`; clase de cascada trasladada byte-idéntica. No imágenes
  modificadas, builds, instalaciones, commits, publicaciones ni subagentes.
- Guía `docs/EFECTOS_AMBIENTALES.md`: parámetros, capas, importación opcional de
  PNG de aves, procedencia y límites. Recursos actuales completos, efectos
  procedurales pequeños; no es animación ilustrada de alto detalle ni todo el
  río. Solo dos salidas justificadas, no todas las chozas. Revisión humana en
  ventana nativa pendiente (cadencia, fidelidad, viajes/diálogo y tres zooms).
