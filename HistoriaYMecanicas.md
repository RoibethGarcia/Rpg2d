# Historia y mecánicas — La última válvula

Documento de diseño acordado en conversación, actualizado el **15 de octubre de 2026**.
Describe la historia y los contratos aprobados. El estado implementado y sus límites se registran
en [IMPLEMENTACION](docs/IMPLEMENTACION.md) y [VALIDACION](docs/VALIDACION.md).
Los valores numéricos de combate son iniciales de prueba, no requisitos oficiales.

## 1. Marco del proyecto y alcance

### Requisitos de la consigna

Según la [referencia local de la consigna, páginas 3–4](Codex/references/curso-y-consigna.md):

- Juego táctico/RPG **postapocalíptico**, con perspectiva isométrica **2.5D**.
- Exploración de mapas por casillas, interacción con objetos del entorno y derrota de enemigos.
- Movimiento del jugador y enemigos sobre rejilla; combate por turnos con puntos de acción.
- Vida, daño y alcance como atributos básicos.

Los requisitos compartidos de menú, victoria/derrota, motor del curso, sonido,
documentación y entregables siguen vigentes en esa referencia. Este documento no los sustituye.
**Python y Pygame** son la base elegida. La adaptación local comprobada del motor de clase 8
y la autorización pendiente para publicarlo se describen en [MOTOR](docs/MOTOR.md).

### Decisiones propias

La historia es **La última válvula**. El alcance inicial será compacto: una protagonista,
un mapa de **24×16** dividido en tres sectores, **tres guardias y un jefe** y un único final.
No se necesitan cinemáticas, ramificaciones narrativas ni múltiples mapas.

El **primer incremento jugable** mantiene el núcleo de Vera contra un enemigo por combate.
La ampliación a un grupo tiene reglas aprobadas de seguimiento, control, incapacitación
y recuperación (sección 8), pero no implica implementar compañeros en ese primer incremento
ni fija su cantidad. Más enemigos simultáneos, armas y cofres son posibilidades futuras,
no compromisos de implementación.

**Aclaración vigente:** el usuario corrigió su aclaración anterior: el mundo debe ser
postapocalíptico, en concordancia con la consigna. La historia original ya está acordada;
no se busca una variación temática ni se atribuye una aprobación docente no verificada.

## 2. Historia: La última válvula

*El mundo terminó hace treinta años. El agua dejó de llegar ayer.*

### Mundo y premisa

Hace treinta años, una guerra destruyó las ciudades y contaminó los ríos.
Las comunidades supervivientes dependen de antiguas instalaciones de purificación
que aún funcionan entre los restos industriales.

**La Hondonada** es un asentamiento construido en una estación ferroviaria abandonada.
Recibe agua de una planta situada al otro lado del distrito industrial. Una mañana,
las tuberías quedan secas. Nadie explica qué ocurrió y la radio de la planta repite:

> «El suministro se restablecerá cuando las condiciones sean seguras».

Las reservas apenas alcanzan para unos días. Esa urgencia motiva la aventura;
no implica implementar un reloj de supervivencia ni una simulación de sed.

### Protagonista y motivación

**Vera** mantiene las bombas y generadores de La Hondonada. No es una soldado ni una elegida:
es una técnica que aprendió reparando los restos del mundo anterior y nunca ha entrado
en la planta principal.

Sale con herramientas, un arma recuperada y un plano incompleto. Su objetivo es
**descubrir por qué se cortó el agua y restablecer el suministro de su comunidad**.

### Conflicto

La planta sigue funcionando. La controla **La Custodia**, un grupo armado que originalmente
protegía sus instalaciones, pero ahora exige combustible, alimentos o trabajadores
a cambio del agua. La Hondonada dejó de pagar porque no tenía qué entregar.

La Custodia activó un antiguo protocolo de emergencia: concentra el agua en el depósito
central y bloquea los conductos comunitarios. Su jefe conserva la única credencial
que permite revertirlo.

La escasez es real, pero su administración se ha convertido en una herramienta de dominio.
El tono combina supervivencia, deterioro industrial y esperanza: Vera no salva el mundo,
sino que resuelve un problema concreto que afecta a su hogar y a sus vecinos.

### Recorrido y escenarios

| Sector del mapa | Narración ambiental | Objetivo jugable |
| --- | --- | --- |
| Acceso industrial | Camiones oxidados, controles abandonados y pertenencias de quienes esperaron agua | Explorar, encontrar suministros y abrir un acceso de mantenimiento |
| Patio de distribución | Depósitos llenos junto a tuberías comunitarias cerradas | Superar patrullas e interactuar con mecanismos |
| Sala de control | Instalación que sostiene y somete a las comunidades | Derrotar al jefe, obtener su credencial y revertir el protocolo |

Los objetos deben tener contexto: herramientas en el taller, botiquines en el puesto
de seguridad y registros de distribución que permitan comprender lo sucedido.
La introducción, mensajes de radio y objetos examinables bastan para contar la historia.

### Desenlace único inicial

Vera derrota al jefe, recupera la credencial y abre los conductos comunitarios.
La radio recibe voces de otros asentamientos: tampoco tenían agua.
Lo que comenzó como una misión para salvar un hogar devuelve a varias comunidades
la posibilidad de sobrevivir sin pedir permiso.

La escasez no desaparece y la planta necesita mantenimiento. La última transmisión
desde La Hondonada cierra la aventura:

> «El agua llegó. Ahora dime qué necesitas para mantenerla corriendo».

La victoria técnica exige obtener automáticamente la **credencial al derrotar al jefe**,
colocarse en una casilla vecina al **panel de la sala de control** y activarlo con **E**,
fuera de combate y sin movimiento pendiente. Vencer al jefe por sí solo no termina la partida.
La derrota ocurre cuando todos los integrantes del grupo participante están incapacitados
(sección 8); en el núcleo de una sola protagonista, cuando Vera llega a 0 de vida.
En victoria/derrota se bloquea gameplay y se permite volver al menú o crear nueva partida.

## 3. Dos estados jugables

| Estado | Movimiento | Enemigos | Recursos |
| --- | --- | --- | --- |
| Exploración | WASD o clic; desplazamiento por casillas con animación suave | Patrullas por rutas fijas | Moverse no consume PA |
| Combate | WASD o clic, únicamente durante el turno propio | Actúa el guardia contactado en su turno; las otras patrullas se pausan | Movimiento y habilidades comparten PA |

El combate ocurre **en el mismo mapa**, sin trasladar unidades a otra arena.
La animación representa el desplazamiento; no sustituye la casilla lógica como fuente de verdad.
La tabla describe el núcleo inicial. En la ampliación de grupo, los compañeros siguen
automáticamente a Vera durante exploración y los controla el jugador durante combate,
no una IA. El orden de turnos grupal y los detalles de selección siguen pendientes.

## 4. Controles y rejilla

| Entrada | Función acordada |
| --- | --- |
| WASD | Movimiento directo, una casilla por paso; interrumpe el recorrido automático |
| Clic en el mapa | Ordenar un recorrido automático hacia una casilla |
| Clic en un guardia durante exploración | Aproximarse para provocar contacto, sin ataque gratuito |
| E | Examinar, recoger o activar un objeto cercano válido |
| Espacio | Terminar voluntariamente el turno, sin costo |
| Escape | Cancelar los pasos pendientes de un recorrido |

Se usan **cuatro vecinos lógicos**, sobre los ejes de la rejilla. Su representación
diagonal en pantalla isométrica no añade diagonales entre casillas. El mapeo acordado es
**W: fila −1; S: fila +1; A: columna −1; D: columna +1**. Las habilidades se activan con
botones de UI; el clic sobre un enemigo en combate lo señala, no ejecuta un ataque.

Paredes, maquinaria y objetos grandes bloquean el paso. WASD y clic comparten
transitabilidad, ocupación y costos: ningún control permite atravesar obstáculos
ni conseguir movimiento más barato. Un clic sobre la interfaz no mueve a Vera.
No se han acordado atajos numéricos para habilidades.
Estos controles describen a Vera en el núcleo inicial; la selección y aplicación
concreta de controles a compañeros se definirán antes de implementar el grupo.

## 5. Patrullas y comienzo del combate

Cada guardia sigue una secuencia determinada de casillas, con pausas en puntos definidos.
Ejemplo de ruta: **puesto de control → depósito → generador → puesto de control**.
Si una casilla de su recorrido está bloqueada, espera. Observar las rutas permite
elegir cuándo cruzar un pasillo o acercarse a un objeto.

Inicialmente no hay detección visual, persecución ni un sistema completo de sigilo.
El combate se activa por **contacto lógico**: Vera o el guardia intenta entrar en
la casilla ocupada por el rival. Ambos conservan sus casillas; nunca se superponen
lógicamente ni se usa el solapamiento visual de sprites como criterio.

Al comenzar un enfrentamiento:

1. Se cancela el recorrido de exploración pendiente.
2. Se pausa el resto de las patrullas y participa solo el guardia contactado.
3. Vera recibe el primer turno y debe dar una nueva orden.

Estas reglas de inicio corresponden al núcleo 1 contra 1. La incorporación de compañeros
al enfrentamiento y si su contacto puede iniciarlo todavía no están acordadas.

Una orden dada en exploración nunca continúa automáticamente gastando PA en combate.
Un bloqueo ordinario detiene el movimiento; un intento válido de contacto hostil
activa la transición. Reservas de destino y actores en tránsito son bloqueos ordinarios,
no disparan contacto. El contacto requiere un rival quieto en la casilla objetivo.
Al iniciar combate se cancelan rutas, órdenes preparadas y movimientos de exploración
sin completar; las posiciones lógicas no se adelantan ni se cobran pasos cancelados.

## 6. Turnos, habilidades y puntos de acción

Se probará con **6 PA por unidad al inicio de su propio turno**.
Los puntos sobrantes no se acumulan: el siguiente turno comienza con el presupuesto
restablecido, no con una suma de sobrantes y puntos nuevos.

| Acción | Costo inicial de prueba | Condición |
| --- | --- | --- |
| Caminar una casilla | 1 PA | Paso válido a una casilla transitable y libre |
| Golpe con llave de mantenimiento | 2 PA | Enemigo en una casilla vecina válida |
| Golpe potente | 3 PA | Enemigo vecino válido; causa mayor daño que el golpe básico |
| Usar botiquín | 2 PA | Turno propio de combate, ítem disponible y vida por debajo del máximo |
| Terminar turno | Gratis | Turno propio |

Vera puede combinar movimiento y habilidades en el orden que prefiera. Espacio
termina su turno, aunque conserve PA. Después actúa el enemigo y vuelve a comenzar
un turno de Vera. Durante el turno enemigo no se aceptan órdenes de movimiento o ataque.
**El turno termina automáticamente al llegar a 0 PA** tras una acción válida;
en movimiento, al completar el último paso. Si el golpe derrota al enemigo,
se vuelve a exploración sin cederle un turno. Espacio permite cederlo antes.
Esta alternancia es la del núcleo inicial; no fija el orden de turnos de la ampliación.

Una acción inválida o sin PA suficientes no consume puntos ni ítems y no produce
su efecto. Tampoco se cobra por intentar caminar contra una pared.
### Balance inicial confirmado, sujeto a pruebas

| Parámetro | Valor |
| --- | --- |
| Vera | 30 de vida; básico 4 de daño; potente 7 |
| Tres guardias | 16 de vida y 3 de daño cada uno |
| Jefe | **48 de vida** y 4 de daño |
| Ataque enemigo | 2 PA; solo vecino, mismo alcance Manhattan 1 |
| Botiquines | Cura hasta 8; uno inicial y dos recogibles antes del jefe |

No se curan ni consumen botiquines fuera de combate; con vida máxima, sin ítems o sin
PA suficientes se rechaza sin efectos. La IA enemiga se acerca por una ruta válida,
ataca cuando está adyacente y termina cuando no puede actuar. La cadencia visual es
0.22 segundos entre decisiones; el costo no depende de esos segundos.

Un enemigo con vida 0 deja de ocupar y actuar. Al vencer se vuelve a exploración,
conservando vida, inventario, consumos y progreso; si es el jefe se obtiene la credencial.
Una **nueva partida**, a diferencia del final de combate, sí reinicia todo el estado.

El jefe de 48 de vida exige aprovechar geometría y retirada. La prueba automatizada del
recorrido completo vence a los tres guardias y al jefe, recoge los dos suministros,
usa tres botiquines y activa el panel con **2 de vida y 0 botiquines**. Esto demuestra
un recorrido posible, NO equilibrio validado ni dificultad adecuada para jugadores nuevos.
No cambiar cifras silenciosamente si una prueba de balance falla.

## 7. Movimiento por clic y costo de recorrido

El clic está disponible tanto en exploración como en combate. Requiere buscar una
secuencia de casillas transitables que rodee los obstáculos; no desplazar a Vera
en línea recta a través de ellos. Se usa **BFS de cuatro vecinos**, con desempate
estable W, D, S, A; el origen no cuenta como paso. Adyacencia y alcance usan Manhattan.

Cada paso reserva el destino, tarda inicialmente **0.14 segundos** y confirma posición
y costo al completarse. Mientras se anima no se acepta otra acción de combate ni un clic
que duplique movimiento. WASD puede preparar una dirección siguiente; Escape la cancela.
La proyección es 2:1, con ancla en vértice superior del rombo; la inversa selecciona mediante
`floor`, incluidos negativos, y se validan los límites del mapa antes de ordenar movimiento.

Al señalar una casilla se muestra el destino y la ruta prevista. En combate también
se muestran costo y PA restantes, por ejemplo: **«Movimiento: 4 PA · Restantes: 2 PA»**.
El clic ejecuta el recorrido permitido por las reglas del estado actual.

**Costo de movimiento = casillas realmente recorridas × 1 PA por casilla.**

| Pasos válidos realizados en combate | PA consumidos |
| --- | --- |
| 2 | 2 |
| 4 | 4 |
| 6 | 6 |

Se cobra el camino real, no la distancia recta, los píxeles ni la distancia visual.
Rodear maquinaria puede costar más que alcanzar otra posición aparentemente más lejana.
No existe un recargo progresivo por alejarse: cada paso mantiene el mismo precio.
Seis pasos con WASD y seis pasos con un clic cuestan lo mismo.

Ejemplo con 6 PA: acercarse dos casillas (**2**), golpear con la llave (**2**) y
retroceder dos casillas (**2**) consume **6 PA**. Quedarse cerca para atacar más
es una alternativa táctica, no una obligación.

### Destino más lejano que los PA disponibles — decisión confirmada

**Vera avanza hasta donde alcancen los PA, en lugar de rechazar todo el movimiento.**

Si una ruta válida cuesta **9 PA** y Vera tiene **6 PA**:

1. La vista previa distingue el tramo alcanzable del que excede el presupuesto.
2. Marca claramente el destino efectivo: la sexta casilla del recorrido.
3. El clic ejecuta como máximo esos seis pasos, cobrando solo los realizados.
4. El resto se cancela; **no continúa automáticamente en el siguiente turno**.

Si tiene 0 PA, no avanza. Un destino fuera del mapa, bloqueado por una pared o sin
ruta válida no produce movimiento ni gasto; no se inventa un destino alternativo.
El clic sobre un guardia en exploración es el caso específico de aproximación
y contacto descrito antes, no permiso para ocupar su casilla.

### Cancelaciones y cambios durante el recorrido

- WASD o Escape cancelan los pasos pendientes al terminar el paso actual.
- Los pasos realizados conservan su costo; los pendientes no se cobran.
- Si una patrulla bloquea la ruta, Vera se detiene: no la atraviesa ni paga pasos no hechos.
- No hay recálculo automático ante un bloqueo nuevo: se descartan los pasos restantes.
- Si se activa un combate por contacto válido, se cancela la ruta de exploración
  y se exige una nueva orden antes de consumir PA.

## 8. Grupo, incapacitación y recuperación

### Seguimiento y control — ampliación acordada

- En exploración, los compañeros siguen automáticamente a Vera por casillas válidas,
  respetando obstáculos y ocupación; seguir no permite teletransportarse ni compartir casilla.
- En combate, el jugador controla a los integrantes capaces de actuar; los compañeros
  no combaten mediante IA aliada.
- No se han fijado cantidad de compañeros, formación, distancia de seguimiento,
  selección de unidad, orden grupal de turnos ni reglas de entrada al combate por compañero.

### Incapacitación y derrota

Un integrante aliado con **vida <= 0** queda **incapacitado**, no puede moverse ni ejecutar
acciones. Esto no equivale a una muerte definitiva ni debe confundirse con un enemigo
derrotado. El combate continúa si queda al menos un integrante capaz de actuar,
incluso si Vera está incapacitada: el jugador controla a los supervivientes.

La derrota ocurre **solo si todos los integrantes del grupo participante están
incapacitados**. Se evalúa antes de cualquier recuperación; no se reincorpora a nadie
para evitar una derrota total. Si Vera participa sola y cae, el grupo completo ha caído.

### Recuperación después de ganar un enfrentamiento

**Solo si el grupo gana el enfrentamiento**, cada integrante incapacitado se reincorpora
con **exactamente 1 punto de vida**. Los supervivientes conservan la vida que les quedaba.
No se restauran inventario, suministros consumidos ni progreso, ni se reinicia el mundo.
Esta reincorporación no modifica el presupuesto de PA ni su reposición por turno acordados.

Con Vera reincorporada cuando corresponda, ella vuelve a liderar la exploración y los
compañeros la siguen. Si todo el grupo cae, se muestra derrota y **no** se aplica esta regla.
La recuperación o resurrección durante un combate no está aprobada por este acuerdo.

| Situación | Resultado acordado |
| --- | --- |
| Vera cae, pero un compañero puede actuar | Continúa el combate con los supervivientes |
| El grupo gana con Vera u otro aliado incapacitado | Cada incapacitado vuelve con 1 de vida; los demás mantienen la suya |
| Todos los integrantes caen | Derrota; no hay reincorporación automática |
| Vera está sola y cae | Derrota, como caso de un grupo de un integrante |

La condición técnica exacta de victoria de cada enfrentamiento, la ocupación de casillas
por incapacitados y los detalles de transición a exploración deben precisarse antes
de implementar la ampliación. Ganar un enfrentamiento no equivale por sí solo a
completar el objetivo narrativo de la partida.

## 9. Interfaz y relación entre historia y juego

La interfaz debe mostrar vida, PA disponibles, unidad/turno activo, acciones y costos.
La vista previa comunica ruta, destino efectivo y presupuesto; los rechazos deben
explicar problemas como **«Sin ruta»** o PA insuficientes para una habilidad.

La llave de mantenimiento refleja el oficio de Vera. Los botiquines son recursos
limitados por inventario; paneles, válvulas y generadores permiten avanzar por la planta.
Manipular maquinaria durante el combate es una posibilidad futura, no una mecánica
aprobada para la primera versión. Los turnos son una representación de decisiones
tácticas: no necesitan una explicación fantástica dentro de la historia.

## 10. Límites iniciales y decisiones pendientes

**Fuera del primer incremento:** compañeros controlables, cuya ampliación conserva
las reglas aprobadas de la sección 8. No es una exclusión definitiva del diseño.

**Otras ampliaciones no comprometidas:** combates con varios enemigos activados a la vez,
armas adicionales, cofres, visión/persecución, terrenos con costos variables,
diálogos extensos, finales alternativos y grandes sistemas adicionales.
Las referencias a Baldur’s Gate 3 y Divinity: Original Sin 2 expresan una intención
de experiencia para el movimiento; no comprometen a reproducir sus demás sistemas.

### Decisiones cerradas para el primer incremento

- Tamaño 24×16, tres sectores y cuatro encuentros 1 contra 1; patrullas y obstáculos
  definidos en `data/world.json`, con pausa inicial de 1.6 segundos.
- Balance inicial de sección 6; algoritmos, controles, pasos, reserva y contacto de secciones 4–7.
- Interacciones de entorno solo fuera de combate; no tienen costo de PA en exploración.
- Credencial automática, panel adyacente con E, derrota de Vera y reinicio completo.
- Recursos gratuitos con procedencia, sprites humanos provisionales y geometría industrial
  provisional; la selección exacta y sus licencias están en [ASSETS](docs/ASSETS.md).

### Pendientes reales

- Revisión manual de dificultad, legibilidad, profundidad visual, controles y sonido real;
  el recorrido automatizado no sustituye jugar la partida.
- Acabado artístico y posible incorporación futura de los packs SBS, hoy no descargados.
- Capturar el video de 15–40 segundos, confirmar licencia del motor docente antes de publicar,
  autorizar expresamente la publicación y preparar la defensa de la entrega.
- Para la ampliación de grupo: cantidad, formación, seguimiento concreto, selección, turnos,
  incorporación al combate y ocupación de incapacitados; recuperación durante combate
  exige un acuerdo propio. Se conservan íntegramente las reglas aprobadas de sección 8.

Estos pendientes no cambian los acuerdos anteriores ni autorizan a inventar nuevos sistemas.
