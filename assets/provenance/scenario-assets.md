# Recursos modulares de escenarios — incremento anterior

La integración posterior de Hondonada usa [su placa limpia por capas](hondonada-layered.md).
Este documento conserva la procedencia del atlas, que sigue activo en puesto y planta.

## Qué se incorporó

El usuario aportó tres ilustraciones completas. Se conservan byte a byte como
referencias locales en `assets/reference/scenarios/{hondonada,puesto,planta}.png`.
**No son tilemaps ni se dibujan como fondos completos.** Sus personajes incrustados
no se representan como actores. Nombres de originales, hashes y registro de
producción: [prompt y procedencia de generación](scenario-atlas-prompt.md).

A partir de esas referencias se produjo con `image_gen.imagegen` un atlas nuevo,
`assets/images/environments/scenario_atlas.png`. No es arte original suministrado
por el usuario ni pertenece a un pack CC0/BY-SA. El PNG generado se conserva sin
alterar bytes; su hash y los hashes de las referencias figuran en el manifiesto.
Redistribución: **pendiente de confirmación**. No se publicó ningún recurso.

## Preparación durante la carga, no por frame

El resultado mide 1254×1254 y no respeta casillas uniformes de 4×4. El manifiesto
registra 16 recortes explícitos con margen de 2 px alrededor de componentes de
alfa >127. No usar `ancho/4` ni el bounding box de alfa mínima (hay ruido tenue).
Las anclas de módulos son centro inferior; se escalan junto al recorte. Los tres
suelos se remapean a 48×24 y se limitan con máscara de rombo en memoria Pygame;
una base geométrica intencional evita huecos en las juntas. No se guarda una
segunda imagen editada ni se modifica el original con scripts.

## Límites jugables y visuales

La geometría y las patrullas existentes no cambian. Casetas, toldos, cajas,
depósitos y máquinas solo ocupan huellas ya bloqueadas, sin invadir apariciones,
objetos o salidas. La Hondonada sigue siendo un mapa provisional casi vacío: sus
módulos pequeños se colocan en el borde bloqueado; esto NO reconstruye el pueblo
completo de la referencia. Se ordenan módulos y personajes por el pie proyectado.

El radio/registro, señalizaciones, indicadores de estado y rutas conservan marcas
geométricas explícitas. La fixture `legacy` conserva el entorno geométrico previo.
No se añadieron NPC, nuevos guardias, arena lateral, animaciones ni desniveles.
