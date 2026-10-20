# Personajes aportados por el usuario — 19 de octubre de 2026

Origen: seis PNG compartidos por el usuario en la conversación del proyecto,
generados con ChatGPT según su descripción. No se verificó una autoría humana
ni se recibió una licencia pública específica. **Redistribución pendiente de
confirmación:** no publicar estos archivos ni atribuirles CC0 o CC BY-SA por
herencia de los packs anteriores. Esto registra procedencia, no concede permisos.

| Recurso | Nombre original aportado |
| --- | --- |
| `vera_front` | `Mecánica superviviente con llave inglesa.png` |
| `vera_rear` | `Imagen de ChatGPT 19 oct 2026, 11_54_50.png` |
| `guard_front` | `Imagen de ChatGPT 19 oct 2026, 11_54_02-1.png` |
| `guard_rear` | `Imagen de ChatGPT 19 oct 2026, 11_54_02-2.png` |
| `boss_front` | `Imagen de ChatGPT 19 oct 2026, 11_52_25-1.png` |
| `boss_rear` | `Imagen de ChatGPT 19 oct 2026, 11_52_26-2.png` |

Los archivos en `assets/images/characters/` son copias byte a byte de los
originales. Cada SHA-256, dimensión, subrectángulo y ancla se registra en
`assets/manifest.json`. No hay derivados raster guardados ni dependencia de la
carpeta Downloads al ejecutar el juego.

## Adaptación exclusivamente en render

- Subrectángulos que incluyen la silueta y el arma: caja alfa >= 128 más 2 píxeles
  de margen. No convertir negro en transparencia ni modificar el alfa fuente.
- Ancla local al subrectángulo, situada entre los contactos de las botas: ajuste
  visual explícito para que el arma no desplace el cuerpo al centrar su caja.
- Escala proporcional con `pygame.transform.smoothscale`, altura de 64 px para
  Vera/guardias y 72 px para el jefe. Escalar también el ancla, sin tintes.
- Dos vistas estáticas, no animaciones ni cuatro direcciones originales. La
  orientación anterior de la lógica de movimiento se conserva.
- Preparar las superficies una sola vez al construir el renderer. Las barras e
  indicadores se ubican por encima del rectángulo del arte, no sobre el torso.

Las láminas de caminata/ataque, el aldeano, los tres escenarios y el mockup de
combate siguen pendientes de sus fases. Este reemplazo no altera mapa, reglas,
PA, turnos, vida, inventario ni cantidad de enemigos.
