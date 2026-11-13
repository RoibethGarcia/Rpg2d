# La última válvula

RPG isométrico postapocalíptico con Python y Pygame, construido sobre el motor de clase 8. Vera, técnica de La Hondonada, debe recuperar la credencial de La Custodia y restablecer el agua desde el panel de la planta.

**Incremento de campaña:** tres mapas ilustrados de 24×16 (Hondonada ↔ puesto ↔ planta), persistentes por partida; dos guardias en el puesto y **tres guardias más el jefe en la planta**, combates 1 contra 1 sobre el suelo de exploración, suministros limitados, victoria, derrota y nueva partida. Vera, guardias y jefe usan PNG frente/espalda y ataques one-shot, sin tintes y con escala corporal proporcional. Los tres escenarios tienen placas por capas y navegación autorada independiente de la imagen. La planta incorpora escaleras, pasarelas, dos botiquines, distribución, registro y **válvula final activable con credencial**. [Diseño](HistoriaYMecanicas.md) · [Implementación por fases](docs/IMPLEMENTACION.md) · [Validación y límites](docs/VALIDACION.md).

La base compartida ya implementa campaña y viajes, pero NO la fase 0 completa:
el render visual, los aldeanos con diálogo y el primer incremento de ataques ya están integrados; arena lateral y animaciones de caminar siguen pendientes en el
[plan por escenarios](docs/integracion-assets/README.md).

## Instalación

Entorno comprobado: macOS ARM64, Python 3.13.15 y `pygame==2.6.1`. Las instrucciones de terminal siguientes asumen macOS/Linux y se ejecutan desde la carpeta que contiene este README. Instalar dependencias requiere autorización del responsable del equipo; no compilar ni instalar desde fuentes si no hay wheel compatible.

```sh
python3.13 --version
python3.13 -m venv .venv
.venv/bin/python -m pip install --only-binary=:all: --no-compile -r requirements.txt
```

El entorno `.venv` ya preparado localmente no se versiona. No es necesario activarlo: usar su Python explícitamente evita confundirlo con otros intérpretes del IDE. En Windows los ejecutables equivalentes están en `.venv\Scripts\`; ese entorno no se verificó en esta sesión.

## Ejecutar

```sh
.venv/bin/python main.py
```

**Ajuste temporal para pruebas:** Vera recibe **3 botiquines** al iniciar cualquier
partida en la aplicación, incluido el reinicio y los accesos directos por mapa.
No se reponen al viajar ni cambian curación, costos o recogida. El balance base
del dominio y sus pruebas históricas conservan un botiquín inicial.

Para **probar directamente el puesto** con una partida fresca (30 de vida,
tres botiquines y los dos guardias vivos):

```sh
.venv/bin/python -B main.py --map puesto
```

Sube la escalera desde la entrada inferior y haz clic en un guardia para acercarte
e iniciar combate. Usa «Potente» o «Llave» cuando esté en un nodo conectado vecino;
Espacio cede el turno. No hay golpe automático al contacto. El menú y «Nueva partida»
conservan el inicio normal en Hondonada; el argumento no cura una partida existente.

Para **probar directamente la planta**, con tres guardias y el jefe vivos, 30 de
vida, tres botiquines iniciales y sin credencial:

```sh
.venv/bin/python -B main.py --map planta
```

Desde el patio interior sube las escaleras hacia distribución y la sala superior.
Hay dos botiquines recogibles y corredores para evitar guardias. Derrota al jefe,
acércate a la válvula señalizada junto a los controles al oeste del reactor y
pulsa **E**. **F3** muestra los caminos y las escaleras transitables. El portón
exterior está cerrado: agua, tejados y patio exterior inferior son decorativos.
Este acceso rápido no concede el botiquín del puesto ni abre mantenimiento.

Para ejecutarlo desde otro directorio, pasar rutas absolutas tanto al Python del entorno como a `main.py`; los recursos se resuelven desde la raíz del proyecto, no desde el directorio actual. La ventana es de 1280×800 y el inicio normal utiliza audio real. Los errores de recursos/audio no se ocultan.

### Controles

| Entrada | Acción |
|---|---|
| «Comenzar» o Enter en el menú | Crear una partida nueva |
| «Opciones» en el menú | Ajustar por separado música y efectos con −/+ en pasos de 10 % |
| «Volver al menú» o Escape en opciones | Regresar al menú conservando el volumen elegido |
| W / S | Fila −1 / +1 |
| A / D | Columna −1 / +1 |
| Clic en casilla | Seguir una ruta; en combate, solo el tramo permitido por los PA |
| Clic en enemigo durante exploración | Aproximarse e iniciar contacto; no ataca gratis |
| Botones «Llave», «Potente», «Botiquín» | Ejecutar habilidades durante el turno de combate |
| E o «Interactuar» | Hablar con aldeanos a 1–2 pasos transitables o viajar desde una salida o hasta 2 pasos de ella; recoger/examinar/activar otros objetos conserva su alcance; fuera de combate y sin pasos/ruta pendientes |
| E / Enter / Espacio o clic en «Continuar» durante diálogo | Avanzar página; la última página cierra la ventana |
| Escape durante diálogo | Cerrar la conversación, sin mover a Vera |
| Espacio o «Fin turno» | Ceder voluntariamente el turno; al agotar los PA termina automáticamente |
| Escape en partida | Cancelar pasos futuros; termina el paso en curso |
| F3 en cualquier escenario | Alternar diagnóstico de rutas y escaleras; apagado al iniciar |
| Botones «Zoom +» / «Zoom −» sobre el mapa | Acercar/alejar entre 100 %, 125 % y 150 % |
| «Volver al menú» | Regresar al menú; «Comenzar» crea estado limpio |
| Escape en victoria/derrota | Volver al menú |
| Cerrar ventana / «Salir» en menú | Cerrar Pygame ordenadamente |

Las direcciones se refieren a la **rejilla**, no a arriba/abajo de la pantalla isométrica. WASD cancela el recorrido y prepara un paso nuevo después del actual. El clic en paneles de UI no atraviesa al mundo. No hay atajos numéricos de habilidades.

El zoom comienza en **100 % (vista general)**. Al acercar, la cámara sigue el pie
de Vera durante el movimiento y se limita a los bordes de la vista general; cerca
de ellos Vera no queda necesariamente centrada. El nivel se conserva al viajar
entre mapas, pero volver al menú o comenzar otra partida restablece el 100 %.
Los clics seleccionan las casillas visibles con la transformación inversa de la
cámara. Los paneles, botones y diálogos mantienen su tamaño y el diálogo captura
también los botones de zoom. No cambia alcance, movimiento, PA ni turnos.

Se amplía la composición raster del mundo ya preparada (incluidas capas,
personajes, ataques y marcadores), no los paneles. Es una solución acotada para
estos niveles de zoom: **aumenta el tamaño, pero no recupera detalle original** y
puede suavizar la imagen. Reutiliza dos buffers fijos; no carga recursos ni vuelve
a preparar sprites por cada cambio de nivel.

### Primer incremento de ataques

Llave y Potente reproducen los cuatro frames de ataque suministrados para Vera;
los guardias y el jefe usan sus propias secuencias. Se orientan horizontalmente
hacia el rival, con pie y profundidad estables. **Daño, PA y turno se resuelven
una sola vez al aceptar el comando**, no en el frame de impacto.

El clip dura **0.20 segundos**, conservando la cadencia enemiga existente de
0.22 s. Durante ese breve feedback se rechazan órdenes tácticas nuevas; el menú
y cerrar la ventana siguen disponibles. Al cerrar combate (también por golpe
letal), viajar, cambiar escena o reiniciar se cancela: por ahora un golpe letal
NO garantiza mostrar el clip completo. Movimiento y espalda conservan estáticos;
no hay arena nueva ni ciclos de caminar. La legibilidad del ritmo queda pendiente
de evaluación humana. [Contrato y evidencias](docs/ATAQUES.md).

### Fondo de La Hondonada

El paisaje aportado se dibuja detrás del escenario inicial, fijo al área del
mundo incluso con zoom. No tiene colisiones ni zonas explorables. Se conserva
la placa original: una máscara de presentación vuelve transparente únicamente
su negro exterior conectado a los bordes, sin eliminar sombras interiores ni
cambiar posiciones de personajes, objetos o interfaz.
[Procedencia y límites](assets/provenance/hondonada-background.md).

### Fondo del Puesto de Control

El segundo escenario utiliza `Paisaje industrial al atardecer.png` como fondo
estático, con el mismo sistema de transparencia exterior y composición fuera
del zoom. No modifica navegación, colisiones ni posiciones. La imagen de ejemplo
con personajes y textos se usa solo como referencia visual, no como placa.
[Procedencia y límites](assets/provenance/puesto-background.md).

### Fondo de la Planta

El último escenario utiliza `Cañón industrial al atardecer (1).png`
como fondo fijo detrás de su placa original, con transparencia exterior y sin
colisiones ni exploración adicionales. Mantiene zoom, personajes, objetos y UI
en sus posiciones actuales. Este cañón con terrazas rocosas sustituye al fondo
anterior de lago. `Instalación industrial al atardecer.png` se usa
solo como referencia visual, para no duplicar personajes y etiquetas pintados.
[Procedencia y límites](assets/provenance/planta-background.md).

### Cascada de La Hondonada

La cascada del extremo sudeste del pueblo tiene una superposición ambiental de
**ocho cuadros a 10 FPS**, integrada sobre el agua pintada y detrás de los
primeros planos. Respeta el zoom, se pausa durante los diálogos y vuelve al primer
cuadro al iniciar una partida nueva. No cambia navegación, PA ni turnos. El
recurso se prepara una sola vez.
[Procedencia y límites de la cascada](assets/provenance/waterfall.md).

### Agua viva en puesto y planta, y fondo del menú

El **Puesto** y la **Planta** animan las caídas y piletas pintadas en su placa
(estelas de agua y brillos generados por código, sin recursos nuevos), el agua
visible del paisaje y unas pocas aves; la Planta añade las caídas de la represa.
El **menú** y «Opciones» usan el paisaje de la planta como fondo vivo (agua,
caídas, aves), un velo oscuro para que el texto se lea y un fundido de entrada.
Todo es decorativo: no toca colisiones, rutas, PA ni turnos, y se ajusta desde
`data/*.json`. [Detalle y parámetros](docs/EFECTOS_AMBIENTALES.md). Las capturas
SDL dummy comprueban que el agua se mueve donde debe, no cómo se ve en pantalla.

### Menú, teclado y «Cómo jugar»

El menú se navega con **flechas o W/S + Enter** (o con el mouse): la entrada
seleccionada se resalta, «Comenzar» destaca, el emblema de la válvula gira
lento y los elementos aparecen en secuencia sin bloquear el input.
«Cómo jugar» (`game/howto.py`) resume controles, PA, Llave/Potente, botiquín,
el truco de retirada contra el jefe y el objetivo de cada nivel; sus números
salen de `game/config.py`, así que no se desactualizan. La lógica de selección
y de aparición es pura (`game/menu_nav.py`) y está cubierta por
`tests/test_menu_polish.py`.

Al ganar, el flujo es **cierre → créditos → menú**: `game/ending.py` muestra
«Fin del primer nivel» (resumen de vida, botiquines y credencial, y el aviso de
que es la prueba del juego y vienen más niveles) con la misma estética del menú;
la primera pulsación salta la animación y recién la siguiente navega.
Cubierto por `tests/test_ending.py`.

### Ambientación sonora por escenario

En **menú → Opciones** puedes bajar o subir **Música** y **Efectos** por
separado, entre 0 % (silencio) y 100 % (mezcla original). Efectos incluye los
botones y todos los golpes de combate. Los porcentajes y barras reflejan el
ajuste actual; se aplica sin reiniciar pistas ni volver a cargar sonidos.
Los valores se mantienen al viajar, volver al menú o comenzar otra partida,
pero **no se guardan al cerrar el juego**. No se añade música al menú.

| Escenario | Pista |
|---|---|
| La Hondonada (inicial) | `prologue.mp3` |
| El Puesto de Control (segundo) | `Heroic Demise (New).mp3` |
| Planta (tercero) | `Gran Batalla.mp3` |

Las pistas se reproducen en bucle, con volumen inicial del 35 %, separadas del
canal de efectos de botones. Continúan durante exploración, combate y diálogos;
no se recargan por frame. Al viajar se sustituye la pista por la del destino;
al regresar o comenzar otra partida se reproduce desde el principio.
Volver al menú, ganar, perder o cerrar detiene la ambientación.
Los inicios directos `--map puesto` y `--map planta` también usan la pista
correspondiente a su escenario.

El menú, los créditos y la derrota no tienen ambientación propia. Para asociar
futuras pistas se añade una entrada por ID de mapa en `ambiences` de
`assets/manifest.json`, con volumen y procedencia. Los tres MP3 aportados se
conservan intactos dentro del proyecto: **autoría y condiciones de redistribución
pendientes de confirmar**. Las pruebas SDL dummy verifican
reproducción y transiciones, no la mezcla audible ni la unión del bucle.
[Procedencia de prologue](assets/provenance/prologue.md) ·
[Procedencia de Heroic Demise](assets/provenance/heroic-demise.md) ·
[Procedencia de Gran Batalla](assets/provenance/gran-batalla.md).

### Sonidos por golpe de combate

Vera usa `hit01.mp3.flac` para **Llave** y `hit02.mp3.flac` para **Potente**;
los guardias usan `hit03.mp3.flac` y el jefe `hit07.mp3.flac`. Son asignaciones
fijas, sin selección aleatoria, con volumen inicial del 55 % por efecto.

Se reproduce una muestra por cada golpe válido que aplica daño, también en los
ataques sucesivos del mismo turno y en los letales. Dibujar cuadros de animación
o rechazar una orden no repite el golpe. Los efectos pueden solaparse sin cortar
sus colas ni la música; el ataque válido ya no añade el tono UI de confirmación.
No cambia daño, PA ni ritmo de la IA. Menú, viaje, reinicio y cierre limpian los
efectos; el último golpe puede terminar al pasar a derrota.

Los cuatro FLAC se conservan intactos: **licencia y redistribución pendientes
de confirmar**. Las pruebas SDL dummy no sustituyen la escucha nativa para
evaluar volumen y sincronización. [Procedencia y límites](assets/provenance/combat-sounds.md).

### Aldeanos de La Hondonada

Hay **dos habitantes** que reutilizan el artesano con taza: el de la plaza recorre
el ramal del mercado de ida y vuelta; el de la terraza permanece quieto.
La ruta está en `data/hondonada.json`, dentro de `villager_plaza.patrol`:
`cells` define los pasos, `pause` la espera (1.2 s) y `duration` cada paso (0.48 s).
El aldeano espera si Vera ocupa o reserva su siguiente casilla; durante el paso
bloquea origen y destino. El recorrido no consume recursos ni bloquea los viajes.
Acércate a **1–2 pasos
transitables** y pulsa **E**: cuenta el camino conectado, no la distancia visual.
Muros, ocupantes y objetos bloqueantes impiden hablar a través de ellos. No se puede atravesar
su casilla ni iniciar combate con ellos. Tienen dos páginas propias y no conceden
vida, botiquines, PA ni misiones nuevas.

La conversación usa el marco industrial y retrato de la imagen aportada, con
nombre, texto y continuación dinámicos. Mientras está abierta, el mundo se pausa
y no se puede mover, combatir ni pulsar botones del HUD a través de ella.
E/Enter/Espacio o «Continuar» avanza; Escape cierra. El historial de cada aldeano
persiste al viajar, al igual que su posición y recorrido; «Comenzar» crea un estado
limpio. El desplazamiento se interpola con la imagen existente: no se han añadido
fotogramas de piernas ni una vista de espalda del aldeano.
[Assets y procedencia](assets/provenance/villager-dialogue.md).

Entre aldeanos y salidas se elige el objetivo alcanzable más cercano; en empate,
la salida conserva prioridad. Si no se puede viajar, se permite otra interacción
válida. Se puede viajar estando sobre la salida; los ataques y demás objetos
mantienen su alcance anterior.

En **los tres escenarios**, la navegación usa conexiones autoradas sobre la ilustración:
clic en suelo o escalera sigue una ruta válida; WASD selecciona un vecino conectado
según los ejes isométricos (W noreste, D sureste, S suroeste, A noroeste), no suma
coordenadas a ciegas. Hondonada incluye seis escaleras entre caminos/terrazas; el puesto conecta la entrada inferior por los peldaños reales a dos corredores de carretera que rodean el camión. No permite
atravesar paredes, subir tejados ni entrar en el agua. La vista se encuadra completa
sin zoom ni cámara libre. [Hondonada](docs/integracion-assets/01-la-hondonada.md) · [Puesto y límites](docs/integracion-assets/02-puesto-de-control.md).

### Objetivo y táctica

1. Desde Hondonada, acercarse a la salida señalizada `(5,10)` y pulsar E para llegar al puesto.
2. Subir la escalera del puesto, observar sus **dos guardias** y combatir o evitarlos por el corredor alternativo. Recoger el botiquín `(6,10)` y activar mantenimiento `(6,9)` con E, junto al portón del noreste. Usar la salida `(8,8)` desde su casilla o hasta 2 pasos transitables para viajar a planta. Allí hay **tres guardias** y dos botiquines: `(1,10)` en el patio y `(8,7)` junto a la pasarela, antes del jefe. Mantenimiento y salida no exigen bajas.
3. Vencer al jefe para obtener automáticamente su credencial.
4. Llegar a una casilla **conectada vecina** a la válvula final `(22,14)` y pulsar E, fuera de combate y sin pasos pendientes. Solo entonces vuelve el agua; derrotar al jefe no termina la campaña automáticamente.

Cada turno dispone de **6 PA**: caminar 1, llave 2 (daño 4), potente 3 (daño 7), botiquín 2 (cura hasta 8). Vera comienza con 30 de vida y **3 botiquines temporalmente para pruebas** (balance base: uno); guardias 16 de vida/daño 3; jefe **42** de vida/daño 4. Enemigos gastan 2 PA por ataque. El botiquín se usa solo en combate. Agotar los PA con una acción válida **termina el turno automáticamente**; Espacio permite cederlo antes.

**Ajuste del jefe (6/11/2026):** su vida baja de 48 a 42, sin cambiar daño, PA,
costos ni guardias. En un duelo aislado sobre el mapa real, Vera entrando con
30 de vida vence con dos potentes por turno durante tres turnos y conserva
**6 de vida**, sin curarse ni retirarse. La fixture histórica de `data/world.json`
conserva 48 de vida; la campaña carga al jefe desde `data/planta.json`.

**Maniobrar importa:** combinar un potente y tres pasos de retirada puede impedir que el rival gaste todo su turno atacando. La campaña automatizada del dominio, con un botiquín inicial de balance base, vence a **cinco guardias y el jefe**, activa la válvula y termina con **2 de vida y ningún botiquín**. Contra cada guardia hace potente+retirada en los primeros dos turnos y remata con básica (curando antes en guardias 2–5); contra el jefe se retira en el primer turno y después combina dos potentes. Demuestra posibilidad, no balance cómodo ni validación con jugadores.

### Créditos al ganar

Al activar la válvula final se muestra la imagen de créditos aportada por el
usuario, completa y sin deformación. Haz clic en **«Volver al menú»**, o pulsa
**Escape/Enter**; desde el menú, «Comenzar» crea una partida limpia. La pantalla
de derrota conserva sus botones.

Desde el 06/11/2026 se utiliza **«Pantalla de créditos en ruinas pixel art.png»**,
con sus textos de sonido y música integrados. Se muestra el PNG completo, sin
el panel superpuesto de la versión anterior. El botón ilustrado conserva su
zona clicable adaptada al nuevo diseño. Las atribuciones impresas no verifican
licencias: [procedencia](assets/provenance/credits.md), [ASSETS](docs/ASSETS.md)
y manifiesto conservan los registros reales y los pendientes de redistribución.

## Pruebas, sin builds

Efectos del escenario 1: [comportamiento, parámetros y límites visuales](docs/EFECTOS_AMBIENTALES.md).

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m unittest discover -s tests -v
```

Resultado de campaña con los tres escenarios por capas y aldeanos: **150 pruebas correctas**
(SDL dummy; incremento de diálogo). Incluye los recorridos de campaña y fixture
histórica, recursos, sprites, las seis escaleras, selección por superficies,
interpolación, viajes, inicio directo de pruebas, alcance de combate sobre el grafo, presupuesto de PA y regresiones de visibilidad en puente/porche/camión. Evidencia
RED/GREEN y límites en [VALIDACION](docs/VALIDACION.md).

Las capturas de SDL dummy permiten inspeccionar el render, pero NO equivalen a
una partida manual nativa, sonido audible ni revisión exhaustiva de todos los
solapamientos. No se repitió el arranque nativo en este incremento; el anterior
smoke macOS tampoco prueba una partida completa. No ejecutar builds, `py_compile`,
`compileall` ni empaquetado para validar.

## Recursos y publicación

Los personajes activos son siete PNG aportados por el usuario, incluido el aldeano, con **redistribución pendiente de confirmación**; no se les atribuye CC0 ni BY-SA. Las plantillas humanas CC0 de intellikat se conservan como referencias legacy. Se mantienen sonidos CC0 de ObsydianX y tuberías BY-SA 4.0 de Darkmoonfire. Los tres escenarios usan placas limpias editadas con IA a partir de las imágenes elegidas, con capas delanteras y navegación autoradas; el atlas modular conserva los props interactivos. Referencias y derivados tienen redistribución pendiente, procedencia, prompt y caché. Las placas no son por sí solas tilemaps: superficies, escaleras y oclusión se definen por separado. No hay packs SBS integrados. Créditos y modificaciones: [ASSETS](docs/ASSETS.md) y `assets/manifest.json`.

**No publicar todavía:** confirmar las condiciones de redistribución de los PNG aportados y los derivados generados. El notebook docente no declara licencia de redistribución. Debe confirmarse permiso para publicar el motor, además de autorizar expresamente la publicación del repositorio. No se creó commit ni se publicó GitLab. [Procedencia y cambios del motor](docs/MOTOR.md).

## Video de entrega: pendiente

El requisito es un video de **15–40 segundos**. Existe un guion y un script preparado; **el video todavía no fue capturado**. Las capturas PNG de pruebas no son el video de entrega.

Con el juego abierto y datos privados ocultos, desde otra terminal macOS:

```sh
bash scripts/grabar_video.sh --record
```

El script inicia selección interactiva nativa de 25 segundos. Selecciona **SOLO la ventana del juego**; usa Espacio para cambiar a selección de ventana si aparece un rectángulo. Cancela con Escape si no puedes aislarla. El sistema puede pedir permiso de grabación de pantalla. Nunca seleccionar el escritorio completo, otras ventanas, notificaciones ni información privada. El script no se ejecuta durante pruebas, no instala herramientas y no activa micrófono; comprobar después si la entrega necesita incorporar sonido del juego. Resultado: `artifacts/demo.mov`, excluido de Git por defecto. Preparar el archivo para entrega explícitamente después de revisarlo.

Guion sugerido de 25–35 segundos, con cortes si es necesario: menú y «Comenzar» (3 s); exploración/ruta e interacción de mantenimiento (6 s); contacto, PA, potente y retirada (8 s); credencial/panel y victoria (6 s); nueva partida o derrota y regreso al menú (4 s). No fingir que ese tramo es una partida completa ni acelerar reglas para grabarlo. Para cubrir todo en un solo clip, preparar previamente los momentos o realizar una edición externa autorizada.
