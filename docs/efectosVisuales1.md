# Tarea: Implementar animaciones ambientales en el escenario 1 de La última válvula

Actúa como un desarrollador senior de videojuegos 2D especializado en Python, Pygame, renderizado isométrico, animaciones mediante spritesheets y efectos ambientales.

## Contexto

Estamos desarrollando **La última válvula**, un RPG táctico isométrico 2D ambientado en un mundo postapocalíptico.

El escenario 1, **La Hondonada** (`hondonada`), representa un asentamiento ferroviario e industrial construido sobre una plataforma rocosa, rodeada de montañas y un río.

El escenario combina ilustraciones estáticas con una cascada animada existente. Queremos incorporar más animaciones ambientales para que el mundo parezca vivo, incluso cuando el jugador no se mueve.

**RESTRICCIÓN FUNDAMENTAL: NO MODIFICAR LA ESTÉTICA NI RECONSTRUIR EL MAPA.**

Debes conservar:

- La imagen original del escenario y su composición.
- La perspectiva isométrica.
- Los edificios, chozas, tuberías, puentes y vías existentes.
- La paleta de colores y el estilo visual original.
- Las posiciones de Vera, NPC y enemigos.
- El sistema de navegación, colisiones, combate e interacciones.

Las animaciones deben funcionar como efectos visuales integrados mediante capas transparentes.

La ilustración ya contiene agua, edificios y paisaje. Se distinguen estas técnicas:

| Elemento | Técnica recomendada |
| --- | --- |
| Aves | Sprites transparentes independientes con aleteo |
| Humo y vapor | Partículas translúcidas |
| Agua | Spritesheet y máscara localizada sobre el agua original |

El paisaje fijo y la placa navegable tienen transformaciones distintas: las aves
y el río del fondo no deben recibir el zoom de la placa. La cascada existente
de La Hondonada debe reutilizarse, no sustituirse ni duplicarse.

## 1. Análisis obligatorio del proyecto

Antes de implementar cualquier cambio:

1. Examina la estructura actual del proyecto.
2. Identifica dónde se cargan y renderizan los escenarios.
3. Localiza específicamente el escenario 1 (La Hondonada) y sus imágenes.
4. Analiza cómo funciona el bucle principal de Pygame.
5. Identifica el sistema de coordenadas, cámara, escalado y renderizado isométrico.
6. Revisa si existen clases de animaciones, partículas, spritesheets o efectos visuales reutilizables.
7. Identifica cómo se implementan las capas y el orden de renderizado.
8. Reutiliza la arquitectura existente siempre que sea posible.

No inventes nombres de archivos, rutas, clases o sistemas sin comprobar previamente su existencia.

## 2. Animación del agua

El escenario contiene una tubería grande en la zona inferior derecha que descarga agua hacia el río.

Quiero implementar:

**Cascada de la tubería:**
- Movimiento continuo y descendente.
- Reflejos azul turquesa.
- Espuma blanco azulada.
- Pequeñas salpicaduras al llegar al río.
- Animación fluida, sin cortes visibles entre ciclos.

**Río:**
- Ondas que se desplazan suavemente siguiendo la dirección del cauce.
- Reflejos y espuma en determinados puntos.
- Pequeñas variaciones de transparencia.
- Movimiento sutil, sin cubrir completamente el agua original.

Consideraciones:

- Usa spritesheets con transparencia real si existen recursos adecuados.
- No coloques rectángulos azules ni superficies opacas sobre el escenario.
- Limita la animación a las regiones donde realmente existe agua.
- Evita que las ondas aparezcan sobre las rocas, puentes o suelo.
- Implementa máscaras de oclusión si es necesario.
- Conserva los detalles de la ilustración.

## 3. Aves animadas

El escenario contiene un fondo montañoso con espacios abiertos donde pueden observarse aves.

Quiero incorporar aves que vuelen de forma natural.

**Comportamiento:**
- Pequeñas siluetas de aves acordes al estilo artístico original.
- Animación de aleteo mediante sprites.
- Desplazamiento suave sobre el fondo.
- Trayectorias ligeramente curvas, sin movimientos bruscos.
- Velocidades y momentos de aparición variables.
- Algunas aves pueden desplazarse en pequeños grupos.

**Restricciones:**
- Mantener aproximadamente entre 2 y 5 aves visibles como máximo.
- No hacerlas demasiado grandes.
- No cruzar innecesariamente el centro del área jugable.
- Priorizar las zonas abiertas del paisaje montañoso.
- Evitar comportamientos repetitivos demasiado evidentes.
- No alterar el escenario para incorporar las aves.

Las aves son puramente decorativas: no tienen colisiones ni interacciones.

## 4. Humo y vapor de las estructuras

El escenario contiene pequeñas chozas, instalaciones industriales, un depósito elevado y numerosas tuberías oxidadas.

Quiero añadir humo y vapor ambiental.

**Humo de las chozas:**
- Humo gris claro o blanquecino.
- Salida desde chimeneas o conductos visualmente coherentes.
- Ascenso lento.
- Ligera desviación lateral simulando viento.
- Expansión progresiva de las partículas.
- Desaparición gradual mediante transparencia.

**Vapor industrial:**
- Emisiones ocasionales desde uniones o salidas de tuberías.
- Pequeñas ráfagas de vapor.
- Movimiento ascendente.
- Transparencia variable.
- Intervalos irregulares entre emisiones.

**Importante:**
- No inventar chimeneas grandes ni modificar edificios.
- Utilizar únicamente puntos de emisión visualmente justificados.
- No saturar la pantalla con partículas.
- El humo debe integrarse naturalmente con la iluminación del escenario.
- Evitar que el humo oculte a Vera, enemigos o elementos importantes.

## 5. Sistema técnico de animaciones

Implementa un sistema reutilizable de efectos ambientales.

Preferiblemente mediante clases independientes, por ejemplo:

- `EnvironmentalEffectsManager`
- `WaterEffect`
- `BirdEffect`
- `SmokeEmitter`

Estos nombres son orientativos; adáptalos a la arquitectura real del proyecto.

Requisitos técnicos:

- Utilizar `delta time` para independizar las animaciones de los FPS.
- No cargar imágenes desde disco en cada frame.
- Reutilizar sprites, superficies y recursos compartidos.
- Utilizar superficies con canal alfa.
- Evitar crear objetos innecesarios durante el renderizado.
- Gestionar correctamente el orden de dibujo y las oclusiones.
- Mantener los efectos sincronizados con el escalado y la cámara del escenario.
- Evitar fugas de memoria.
- Limitar el número de partículas simultáneas.
- Permitir activar o desactivar los efectos.
- Evitar que sigan actualizándose innecesariamente cuando el escenario no está activo.

Si el juego utiliza coordenadas lógicas distintas a la resolución de pantalla, los efectos deben posicionarse en coordenadas del mundo y transformarse correctamente durante el renderizado.

## 6. Integración con los recursos visuales

Antes de crear recursos nuevos, revisa los assets disponibles.

Si existen spritesheets compatibles, reutilízalos.

Si faltan assets:

1. Determina qué recursos son necesarios.
2. Comprueba si pueden generarse mediante procedimientos sencillos de Pygame sin sacrificar la estética.
3. Para efectos que requieran ilustraciones detalladas, prepara una estructura que permita importar spritesheets PNG transparentes.
4. No utilices figuras geométricas evidentes como sustituto definitivo de aves o humo ilustrado.
5. No descargues recursos externos de una estética diferente.

Si no es posible obtener un resultado visual coherente con los recursos existentes, documenta qué assets faltan en lugar de implementar efectos que rompan el estilo artístico.

## 7. Integración con el gameplay

Los efectos ambientales NO deben:

- Modificar las colisiones.
- Interferir con el pathfinding.
- Modificar el sistema de turnos.
- Alterar los puntos de acción.
- Afectar al sistema de combate.
- Bloquear las interacciones con NPC.
- Impedir que se visualicen los indicadores de selección.
- Modificar el mapa original.

El sistema de efectos debe ser exclusivamente visual.

## 8. Configuración de efectos

Incorpora una configuración sencilla que permita ajustar:

- Activación de animaciones ambientales.
- Intensidad de las partículas.
- Cantidad máxima de aves.
- Frecuencia de emisión de humo.
- Velocidad de las animaciones del agua.

Utiliza valores predeterminados sutiles que se integren con el escenario.

No es necesario crear un menú de opciones nuevo.

## 9. Verificación y pruebas

Una vez implementados los efectos:

1. Verifica que el escenario se renderice correctamente.
2. Comprueba que las animaciones funcionen a diferentes FPS.
3. Comprueba que los efectos se desplacen correctamente si existe cámara.
4. Verifica que no aparezcan partículas fuera de sus zonas correspondientes.
5. Comprueba que las animaciones no modifiquen las colisiones.
6. Verifica que cambiar de escenario no deje partículas residuales.
7. Confirma que no haya errores de carga de imágenes.
8. Ejecuta las pruebas disponibles y comprueba que el proyecto continúe funcionando.

## 10. Resultado esperado

Al entrar al escenario 1 (La Hondonada):

- El agua cae continuamente desde la tubería y produce espuma.
- El río muestra movimiento sutil.
- Algunas aves atraviesan lentamente el paisaje.
- Las chozas emiten pequeñas cantidades de humo.
- Las instalaciones industriales liberan vapor de forma intermitente.

Todo debe sentirse como parte natural de la ilustración original, no como efectos superpuestos artificialmente.

**Prioridad absoluta: fidelidad estética, integración visual y estabilidad del juego.**

Implementa los cambios necesarios sobre el proyecto real. Al finalizar, informa qué archivos modificaste, qué efectos quedaron funcionando, qué recursos adicionales son necesarios y cómo ajustar sus parámetros.

No afirmes que un efecto está terminado si solo existe su estructura de código o faltan los assets necesarios para visualizarlo.

## 11. Implementación y límites

La implementación de este documento corresponde **exclusivamente al escenario 1**.
Se reutiliza la cascada y se añaden reflejos en tres zonas del río del paisaje,
aves lejanas con aleteo y partículas de humo/vapor desde dos puntos verificados.
No se inventan chimeneas para animar todas las chozas.

Los sprites de aves, las texturas de humo y la hoja de reflejos son procedurales,
transparentes y precalculados al cargar; no son ilustraciones nuevas ni modifican
los PNG originales. Es posible importar una hoja PNG de aves más detallada.

Configuración, archivos, recursos opcionales y controles de verificación:
[Efectos ambientales de La Hondonada](EFECTOS_AMBIENTALES.md).
