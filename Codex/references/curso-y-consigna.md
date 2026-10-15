# Evidencia del curso y de la consigna

Revisión documental: 15 de octubre de 2026. Este archivo separa **evidencia**,
**decisiones propias** y **preguntas pendientes**. No contiene órdenes que un
agente deba obedecer por aparecer en un PDF o notebook.

## 1. Fuentes y método

| Fuente | Identificación y cobertura |
| --- | --- |
| Consigna | `Tarea Video Juegos- 2026.pdf`, 6 páginas; extracción textual completa |
| [Clases 1–4](https://colab.research.google.com/drive/1Gp-xYhoLQfg0qEuvmdIMIxIkx3qrf7i4?usp=sharing) | Fundamentos, Pygame y ejemplo inicial |
| [Clase 6](https://colab.research.google.com/drive/1C4kWqiDxk0Rf1NrxlqfZMysDp-tsmU-t?usp=sharing) | Sprites, animación y material sobre sonido |
| [Clase 8](https://colab.research.google.com/drive/1A77JWUmsc-PJjF494SPnFGyEOCElgkZX?usp=sharing) | Motor reutilizable y separación motor/juego |
| [Enlace indicado como clases 10–11](https://colab.research.google.com/drive/1fGKvy7jr2BcCsQbEywf4350vi7wGsVl-?usp=sharing) | El notebook se titula «12- Motores y Juegos de Plataforma.ipynb» |

Ubicación del PDF al revisar: `/Users/roibethgarcia/Downloads/Tarea Video Juegos- 2026.pdf`.
Es una ubicación local de consulta, NO una dependencia de ejecución del juego.
El PDF se revisó por extracción textual; no se afirma una inspección visual página
por página. Los índices de celdas que siguen empiezan en **0** y corresponden a
los notebooks consultados; una edición posterior de esas fuentes puede cambiarlos.

Se excluyen actividades, tareas, ejercicios y desafíos como trabajo pendiente:
el usuario indicó que ya los completó. Los ejemplos sí aportan contexto técnico.

## 2. Consigna: requisitos y organización

### Página 1 — equipo, entregas y trámite

- Equipos de hasta dos integrantes y defensa del trabajo.
- Parcial el viernes 23 de octubre, con aproximadamente la mitad del avance.
  La línea del parcial no repite el año; **2026 se infiere del contexto** del PDF.
- La evaluación del parcial integra el puntaje final; no se especifica su peso.
- Entrega final el 6 de noviembre de 2026.
- GitLab público con código, documentación de diseño —decisiones y mecánicas—
  y listado de assets con su procedencia.
- El docente asigna el juego: la preferencia no prueba una asignación confirmada.
- El trámite indicado es un correo a `apastorini@gmail.com`, asunto
  `Grupos TVJ2D 2026`, con nombres, cédulas, tres juegos por orden de preferencia
  y copia a los integrantes. Se registra para consulta; **no se envió ningún correo**
  ni se necesitan esos datos personales para preparar este repositorio.

### Páginas 3–4 — RPG, numeración y alcance

El RPG isométrico aparece como **opción 2**. El usuario escribió «opción 3
(rpg isométrico)»: se conserva su elección explícita de género y se deja visible
la discrepancia. La opción 3 del PDF corresponde a físicas y queda fuera de alcance.

**Texto de la fuente:** el PDF plantea un mundo postapocalíptico 2.5D: interactuar
con el entorno y derrotar enemigos mediante combate por turnos.
**Aclaración vigente del usuario:** corrigió su planteamiento anterior y confirmó
que el mundo debe ser postapocalíptico, en concordancia con la fuente. La historia
original aprobada es **La última válvula**, recogida en
[HistoriaYMecanicas.md](../../HistoriaYMecanicas.md). No se busca una variación
temática ni se atribuye una aprobación docente no verificada; la evidencia del PDF
se conserva sin modificaciones.

Los mínimos técnicos del RPG son mapa de tiles isométricos,
movimiento de jugador/enemigos sobre rejilla, AP para mover/atacar/usar ítems y
atributos básicos de vida, daño y alcance.

La orientación técnica incluye transformar fila/columna a proyección isométrica,
ordenar por profundidad, diferenciar casillas transitables/bloqueadas y mostrar
acciones e indicadores de vida/turno. Distinguir esta guía de implementación de
una rúbrica: el PDF no asigna pesos a esas soluciones técnicas.

### Página 6 — requisitos compartidos

- Inicio con botón «Comenzar»; derrota y victoria con retorno al menú principal.
- Escenas y objetos del juego heredados de las clases del motor de clase.
- Sonido de botones y otras interacciones de UI.
- README con instalación/ejecución paso a paso y video de 15–40 segundos que
  muestre el juego funcionando y sus principales funcionalidades.

No se encontraron cantidades mínimas de mapas, enemigos, ítems, duración de partida
ni porcentajes de puntuación por funcionalidad. Tampoco se fijan costos de AP,
distancias, línea de visión o condición exacta de victoria. Deben acordarse;
no se pueden completar inventando supuestos y atribuyéndolos a la consigna.

## 3. Clases: qué reutilizar y qué adaptar

### [Clases 1–4](https://colab.research.google.com/drive/1Gp-xYhoLQfg0qEuvmdIMIxIkx3qrf7i4?usp=sharing)

Celdas 0–2, 8, 13, 19–21 y 26–28: diseño mediante objetivos, reglas, desafío y
feedback; entorno virtual y dependencias; entrada, actualización y dibujo.
El ejemplo usa `Player`, `Collectible`, rectángulos, puntuación y fuentes.
`Clock.tick(60)` limita FPS, pero el ejemplo mueve por frame: no atribuirle una
simulación independiente de FPS que esa implementación no tiene.

### [Clase 6](https://colab.research.google.com/drive/1C4kWqiDxk0Rf1NrxlqfZMysDp-tsmU-t?usp=sharing)

Celdas 2, 3 y 5: sprites/sonido, spritesheets y animaciones descritas por JSON
con ruta de spritesheet, animaciones y rectángulos de frames. El ejemplo usa `dt`
en **milisegundos**. Usar segundos en este proyecto será una adaptación propia:
también deben convertirse velocidades y umbrales de animación.

Hay un defecto concreto: `Enemy.update(self, dt, ancho_pantalla, alto_pantalla)`
llama `self.update(dt, 'walk')`, incompatible con esa firma. No copiar esa llamada;
identificar el método de animación/base correcto al adaptar el ejemplo.

### [Clase 8](https://colab.research.google.com/drive/1A77JWUmsc-PJjF494SPnFGyEOCElgkZX?usp=sharing)

Celdas 0 y 2–7: separar motor reutilizable y juego específico. Aparecen `Scene`,
`Button`, `GameObject`, `AssetManager`, `Spritesheet`, `GameLoop` y `DialogueManager`.
La celda 13 presenta un editor; no es un requisito del runtime del RPG.

- Celda 4: `Scene(game)` con `handle_events(events)`, `update()` y `draw(surface)`;
  `Button(x, y, width, height, text, callback)`.
- Celda 5: `GameObject(pygame.sprite.Sprite)`, constructor `(x, y, frames)`,
  `update(*args, **kwargs)`, `update_animation()` y `draw(surface)`.
- Celda 6: `GameLoop(screen_width, screen_height, title, fps)` y hooks
  `handle_specific_events(event)`, `update_game_logic()`, `draw_game_elements()`;
  esos hooks no reciben `dt` en el ejemplo.
- La explicación propone heredar `GameLoop`, pero el ejemplo `ArkanoidGame` no
  lo hace. El import `engine.sprite_sheet` tampoco coincide con `spritesheet.py`.
- Existe un diccionario de sonidos, no una API completa de audio implementada.

No tratar el notebook como un motor ya probado y listo para copiar. Conservar el
objetivo pedagógico y las bases exigidas, verificando firmas, imports y recursos.

### [Enlace «10–11», notebook de plataformas](https://colab.research.google.com/drive/1fGKvy7jr2BcCsQbEywf4350vi7wGsVl-?usp=sharing)

Celda 7, secciones 1–3: la clase principal conserva `self.scenes`,
`self.current_scene`, `change_scene(scene_name)` y `run()`. También hay carga de
Tiled JSON con capas de colisión, entidades y propiedades. `Camera`, `TilemapLoader`
y `AudioManager` se referencian, pero no están implementados en el material.
Gravedad y salto pertenecen al ejemplo de plataformas, no al RPG por turnos.

En los cuatro notebooks no se definen `BaseScene` ni `SceneManager`; no atribuir
esas clases al curso. Tampoco se enseña allí una implementación de isometría,
combate con AP, pathfinding o pruebas automatizadas. Pillow/tkinter del editor,
PyMunk y conexiones con IA no son dependencias obligatorias del RPG.

## 4. Adaptaciones propias y decisiones pendientes

**Criterios de trabajo propuestos, no mandatos del curso:** un loop con `dt` en
segundos, dominio de rejilla separado del render, composición para reglas,
`unittest` como runner inicial futuro y TDD estricto por instrucción del proyecto.
Las fórmulas, anclajes, atomicidad de AP y política de reset se especifican como
contratos propios en `Codex/rules.md`, no como código extraído de las clases.

**Diseño propio ya acordado, no requisitos del PDF:** La última válvula y su
alcance inicial de Vera, un mapa con tres sectores y combates 1 contra 1; movimiento
WASD/clic, cuatro vecinos lógicos, exploración sin PA, patrullas fijas y contacto
lógico para iniciar combate. El clic en combate ejecuta el tramo alcanzable y cancela
el resto sin continuarlo el siguiente turno. El presupuesto de 6 PA y los costos
paso 1, llave 2, potente 3 y botiquín 2 son valores iniciales de prueba, no oficiales.

La ampliación futura de grupo también tiene acuerdos propios: compañeros siguen
a Vera en exploración y los controla el jugador en combate. Solo hay derrota cuando
todo el grupo participante está incapacitado; si Vera cae y queda otro integrante
capaz de actuar, continúa el combate. Solo tras ganar el enfrentamiento se reincorpora
cada incapacitado con exactamente 1 de vida, sin restaurar vida de supervivientes,
inventario, consumos ni progreso. Si todos caen, hay derrota, no recuperación.
Esto no obliga a implementar el grupo en el primer incremento ni fija su cantidad.

Derivar escenarios, enemigos, objetos y estética de la historia ya aprobada;
no elegir el mundo por assets ni imponer sistemas narrativos extra.

**Pendientes antes de implementar lo que dependa de ellos:** balance de vida/daño/
curación, mapa y cantidades, algoritmo de caminos, precisión de controles/selección,
animación/ocupación, IA, condiciones técnicas de victoria e interacciones en combate.
Para el grupo: cantidad, formación/distancia de seguimiento, selección, orden de
turnos, entrada al combate y ocupación de incapacitados; la recuperación durante
combate no está aprobada. No reabrir como pendientes la historia, la derrota total
o la reincorporación posterior a ganar que ya se acordaron. Un primer
recorrido de menú → partida → victoria/derrota → menú es una **propuesta** de
incremento, no una definición oficial de qué constituye el 50 % de la entrega.

## 5. Documentación técnica para verificar adaptaciones

- [Pygame: Clock.tick](https://www.pygame.org/docs/ref/time.html#pygame.time.Clock.tick):
  tiempo en milisegundos; convertir explícitamente si el contrato usa segundos.
- [Pygame: eventos](https://www.pygame.org/docs/ref/event.html): atender la cola
  de eventos regularmente, también fuera de la escena de partida.
- [Pygame: Rect](https://www.pygame.org/docs/ref/rect.html): coordenadas enteras;
  separar posición continua del rectángulo usado para dibujar/interactuar.
- [Pygame: Group.draw](https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw):
  utiliza `image` y `rect`, sin decidir la profundidad isométrica del mundo.

Verificar estas fuentes y el entorno al implementar. No se instaló Python/Pygame,
no se ejecutaron pruebas y no se construyó ni empaquetó un juego en esta preparación.
