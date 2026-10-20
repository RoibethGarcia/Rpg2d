# La Hondonada — placa limpia y capas registradas

## Origen y derechos

El usuario eligió su ilustración de La Hondonada para recorrerla **por capas,
incluyendo escaleras transitables**, el 19 de octubre de 2026. Esta autorización
de implementación sustituye el límite anterior de escaleras decorativas para
este mapa; no amplía por sí sola el alcance de los otros escenarios.

El adjunto `Imagen de ChatGPT 19 oct 2026, 11_54_08.png` coincide byte a byte con
`assets/reference/scenarios/hondonada.png` (SHA-256
`0caa874784d4c72fb2157aa7f67e7cd0271b01292bea14938a587cbb723eee7b`).
Se conserva sin cambios, como referencia suministrada por el usuario.

Se editó esa referencia mediante `image_gen.imagegen` para retirar el personaje
incrustado en la plaza, evitando duplicarlo con Vera. [Prompt exacto](hondonada-clean-prompt.md).
La salida original, sin edición posterior, se encuentra en
`assets/images/environments/hondonada_clean.png`, clave `images.hondonada_plate`.
SHA-256: `66f3860cbc13438dd0159ce4197f33753620bce22d8d01329d06720b54fede85`.
Es una **edición generativa**, no un original nuevo aportado por el usuario ni
un pack CC0/BY-SA. No se inventa autor humano ni licencia pública.
**Redistribución pendiente de confirmación** para fuente y derivado: no publicar.

## Contrato del recurso

PNG de **1448×1086, RGB de 24 bits, fondo negro opaco**, sin alfa. La esquina
superior izquierda contiene `(2,2,2)`, no negro RGB exacto; no usar un colorkey
negro global, que eliminaría sombras interiores. La política `background:
opaque_black` es explícita y específica de esta placa; no elimina el requisito
de transparencia de sprites, atlas y demás imágenes existentes.

La composición completa sirve de base. Los elementos que deben ocultar a Vera
se recortan con polígonos registrados y se cachean en memoria durante la carga;
no se distribuyen PNG de capas pintadas por separado. Las rutas y superficies
transitables se describen aparte del bitmap: una escalera pintada no concede
movimiento ni una pared pintada bloquea automáticamente. Véase
[contrato jugable](../../docs/integracion-assets/01-la-hondonada.md).

La edición generativa puede cambiar detalles respecto del original: no afirmar
identidad píxel a píxel salvo los archivos copiados. Ni este recurso ni los
tests automáticos certifican todos los solapamientos o calidad artística final.

## Evidencia local de presentación

Capturas de la aplicación real con SDL dummy, no nuevos recursos de producción:
[vista general](../../artifacts/hondonada-overview.png),
[rutas de diagnóstico](../../artifacts/hondonada-navigation.png),
[escaleras](../../artifacts/hondonada-stairs-contact.png) y
[terrazas/puente](../../artifacts/hondonada-platforms-contact.png).
Las hojas de contacto colocan a Vera mediante fixtures visuales en extremos y
puntos intermedios; no representan una partida manual. `artifacts/` está excluido
de Git y puede faltar en otro checkout: la ejecución solo necesita los recursos
y datos del proyecto, no estas capturas. Ver [validación](../../docs/VALIDACION.md).
