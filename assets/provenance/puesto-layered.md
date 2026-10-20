# El Puesto — placa limpia para exploración y combate

## Origen y derechos

El 19 de octubre de 2026 el usuario pidió hacer explorable su ilustración del
Puesto, con guardias para probar el combate. La referencia
`assets/reference/scenarios/puesto.png` se conserva sin modificaciones.
SHA-256: `231af261fd3b339d62f6ee9cbee136327cad6bd772db8755e3fd393c88e25678`.

Se editó mediante `image_gen.imagegen` para retirar los cinco humanos pintados:
izquierda, carretera delantera, pasarela central, carretera derecha y torre
superior. Así los personajes del juego pueden moverse y recibir daño sin dejar
duplicados estáticos en el fondo. [Prompt exacto](puesto-clean-prompt.md).

La salida original se copió sin modificar sus bytes desde
`exec-f34b61ef-5603-4eba-a191-51a62a9f5eab.png` a
`assets/images/environments/puesto-clean.png`, clave `images.puesto_plate`.
SHA-256: `c485ecfa422a61a1d99b70a737cdf890b4d86b3d142b62a84d73a285470b6242`.
Es una **edición generativa** de la referencia aportada por el usuario; no se
inventa un autor humano ni una licencia CC0/BY-SA. **Redistribución pendiente
de confirmación** para la referencia y el derivado: no publicar todavía.

## Contrato del recurso

PNG de **1448×1086, RGB de 24 bits, fondo negro opaco**, sin alfa. El manifiesto
declara `usage: layered_environment_plate` y `background: opaque_black` como en
La Hondonada. No usar un colorkey negro global, que eliminaría sombras interiores.
La excepción de fondo opaco corresponde a las placas registradas, no a sprites
ni al atlas modular, que conservan sus contratos de transparencia.

La imagen es una composición completa, no un tileset ni un modelo 3D. Las rutas,
conexiones y posiciones de apoyo deben definirse con datos explícitos alineados
con la salida final; una escalera pintada no habilita movimiento automáticamente.
Las máscaras de primer plano son recortes registrados en memoria, no imágenes
independientes con traseras reconstruidas. Los guardias activos utilizan los
recursos de personaje y el estado de combate, no los humanos de la referencia.

La herramienta recibió una instrucción de conservar encuadre y composición,
pero **una edición generativa no garantiza identidad píxel a píxel** respecto
del original fuera de las personas retiradas. El hash certifica los archivos
concretos, no equivalencia artística ni calidad de todas las oclusiones.
Resultados y límites de las comprobaciones en [VALIDACION](../../docs/VALIDACION.md).
