# La última válvula

RPG isométrico postapocalíptico con Python y Pygame, construido sobre el motor de clase 8. Vera, técnica de La Hondonada, debe recuperar la credencial de La Custodia y restablecer el agua desde el panel de la planta.

**Incremento de campaña:** tres mapas ilustrados de 24×16 (Hondonada ↔ puesto ↔ planta), persistentes por partida; dos guardias en el puesto y **tres guardias más el jefe en la planta**, combates 1 contra 1 sobre el suelo de exploración, suministros limitados, victoria, derrota y nueva partida. Vera, guardias y jefe usan PNG estáticos frente/espalda, sin tintes y con escala proporcional. Los tres escenarios tienen placas por capas y navegación autorada independiente de la imagen. La planta incorpora escaleras, pasarelas, dos botiquines, distribución, registro y **válvula final activable con credencial**. [Diseño](HistoriaYMecanicas.md) · [Implementación por fases](docs/IMPLEMENTACION.md) · [Validación y límites](docs/VALIDACION.md).

La base compartida ya implementa campaña y viajes, pero NO la fase 0 completa:
el render modular visual ya está integrado; aldeanos, arena lateral y animaciones siguen pendientes en el
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

Para **probar directamente el puesto** con una partida fresca (30 de vida,
un botiquín y los dos guardias vivos):

```sh
.venv/bin/python -B main.py --map puesto
```

Sube la escalera desde la entrada inferior y haz clic en un guardia para acercarte
e iniciar combate. Usa «Potente» o «Llave» cuando esté en un nodo conectado vecino;
Espacio cede el turno. No hay golpe automático al contacto. El menú y «Nueva partida»
conservan el inicio normal en Hondonada; el argumento no cura una partida existente.

Para **probar directamente la planta**, con tres guardias y el jefe vivos, 30 de
vida, un botiquín inicial y sin credencial:

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
| W / S | Fila −1 / +1 |
| A / D | Columna −1 / +1 |
| Clic en casilla | Seguir una ruta; en combate, solo el tramo permitido por los PA |
| Clic en enemigo durante exploración | Aproximarse e iniciar contacto; no ataca gratis |
| Botones «Llave», «Potente», «Botiquín» | Ejecutar habilidades durante el turno de combate |
| E o «Interactuar» | Recoger/examinar/activar objetos; viajar desde un vecino de una salida señalizada, fuera de combate y sin pasos/ruta pendientes |
| Espacio o «Fin turno» | Ceder voluntariamente el turno |
| Escape en partida | Cancelar pasos futuros; termina el paso en curso |
| F3 en cualquier escenario | Alternar diagnóstico de rutas y escaleras; apagado al iniciar |
| «Volver al menú» | Regresar al menú; «Comenzar» crea estado limpio |
| Escape en victoria/derrota | Volver al menú |
| Cerrar ventana / «Salir» en menú | Cerrar Pygame ordenadamente |

Las direcciones se refieren a la **rejilla**, no a arriba/abajo de la pantalla isométrica. WASD cancela el recorrido y prepara un paso nuevo después del actual. El clic en paneles de UI no atraviesa al mundo. No hay atajos numéricos de habilidades.

En **los tres escenarios**, la navegación usa conexiones autoradas sobre la ilustración:
clic en suelo o escalera sigue una ruta válida; WASD selecciona un vecino conectado
según los ejes isométricos (W noreste, D sureste, S suroeste, A noroeste), no suma
coordenadas a ciegas. Hondonada incluye seis escaleras entre caminos/terrazas; el puesto conecta la entrada inferior por los peldaños reales a dos corredores de carretera que rodean el camión. No permite
atravesar paredes, subir tejados ni entrar en el agua. La vista se encuadra completa
sin zoom ni cámara libre. [Hondonada](docs/integracion-assets/01-la-hondonada.md) · [Puesto y límites](docs/integracion-assets/02-puesto-de-control.md).

### Objetivo y táctica

1. Desde Hondonada, acercarse a la salida señalizada `(5,10)` y pulsar E para llegar al puesto.
2. Subir la escalera del puesto, observar sus **dos guardias** y combatir o evitarlos por el corredor alternativo. Recoger el botiquín `(6,10)` y activar mantenimiento `(6,9)` con E, junto al portón del noreste. Usar la salida `(8,8)` desde un vecino para viajar a planta. Allí hay **tres guardias** y dos botiquines: `(1,10)` en el patio y `(8,7)` junto a la pasarela, antes del jefe. Mantenimiento y salida no exigen bajas.
3. Vencer al jefe para obtener automáticamente su credencial.
4. Llegar a una casilla **conectada vecina** a la válvula final `(22,14)` y pulsar E, fuera de combate y sin pasos pendientes. Solo entonces vuelve el agua; derrotar al jefe no termina la campaña automáticamente.

Cada turno dispone de **6 PA**: caminar 1, llave 2 (daño 4), potente 3 (daño 7), botiquín 2 (cura hasta 8). Vera comienza con 30 de vida y un botiquín; guardias 16 de vida/daño 3; jefe **48** de vida/daño 4. Enemigos gastan 2 PA por ataque. El botiquín se usa solo en combate. Llegar a 0 PA **NO termina el turno**: pulsa Espacio.

**Maniobrar importa:** combinar un potente y tres pasos de retirada puede impedir que el rival gaste todo su turno atacando. La campaña automatizada vence a **cinco guardias y el jefe**, activa la válvula y termina con **2 de vida y ningún botiquín**. Contra cada guardia hace potente+retirada en los primeros dos turnos y remata con básica (curando antes en guardias 2–5); contra el jefe se retira en el primer turno y después combina dos potentes. Demuestra posibilidad, no balance cómodo ni validación con jugadores.

## Pruebas, sin builds

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m unittest discover -s tests -v
```

Resultado de campaña con los tres escenarios por capas: **136 pruebas correctas**
(SDL dummy; incremento de planta). Incluye los recorridos de campaña y fixture
histórica, recursos, sprites, las seis escaleras, selección por superficies,
interpolación, viajes, inicio directo de pruebas, alcance de combate sobre el grafo, presupuesto de PA y regresiones de visibilidad en puente/porche/camión. Evidencia
RED/GREEN y límites en [VALIDACION](docs/VALIDACION.md).

Las capturas de SDL dummy permiten inspeccionar el render, pero NO equivalen a
una partida manual nativa, sonido audible ni revisión exhaustiva de todos los
solapamientos. No se repitió el arranque nativo en este incremento; el anterior
smoke macOS tampoco prueba una partida completa. No ejecutar builds, `py_compile`,
`compileall` ni empaquetado para validar.

## Recursos y publicación

Los personajes activos son seis PNG aportados por el usuario, con **redistribución pendiente de confirmación**; no se les atribuye CC0 ni BY-SA. Las plantillas humanas CC0 de intellikat se conservan como referencias legacy. Se mantienen sonidos CC0 de ObsydianX y tuberías BY-SA 4.0 de Darkmoonfire. Los tres escenarios usan placas limpias editadas con IA a partir de las imágenes elegidas, con capas delanteras y navegación autoradas; el atlas modular conserva los props interactivos. Referencias y derivados tienen redistribución pendiente, procedencia, prompt y caché. Las placas no son por sí solas tilemaps: superficies, escaleras y oclusión se definen por separado. No hay packs SBS integrados. Créditos y modificaciones: [ASSETS](docs/ASSETS.md) y `assets/manifest.json`.

**No publicar todavía:** confirmar las condiciones de redistribución de los PNG aportados y los derivados generados. El notebook docente no declara licencia de redistribución. Debe confirmarse permiso para publicar el motor, además de autorizar expresamente la publicación del repositorio. No se creó commit ni se publicó GitLab. [Procedencia y cambios del motor](docs/MOTOR.md).

## Video de entrega: pendiente

El requisito es un video de **15–40 segundos**. Existe un guion y un script preparado; **el video todavía no fue capturado**. Las capturas PNG de pruebas no son el video de entrega.

Con el juego abierto y datos privados ocultos, desde otra terminal macOS:

```sh
bash scripts/grabar_video.sh --record
```

El script inicia selección interactiva nativa de 25 segundos. Selecciona **SOLO la ventana del juego**; usa Espacio para cambiar a selección de ventana si aparece un rectángulo. Cancela con Escape si no puedes aislarla. El sistema puede pedir permiso de grabación de pantalla. Nunca seleccionar el escritorio completo, otras ventanas, notificaciones ni información privada. El script no se ejecuta durante pruebas, no instala herramientas y no activa micrófono; comprobar después si la entrega necesita incorporar sonido del juego. Resultado: `artifacts/demo.mov`, excluido de Git por defecto. Preparar el archivo para entrega explícitamente después de revisarlo.

Guion sugerido de 25–35 segundos, con cortes si es necesario: menú y «Comenzar» (3 s); exploración/ruta e interacción de mantenimiento (6 s); contacto, PA, potente y retirada (8 s); credencial/panel y victoria (6 s); nueva partida o derrota y regreso al menú (4 s). No fingir que ese tramo es una partida completa ni acelerar reglas para grabarlo. Para cubrir todo en un solo clip, preparar previamente los momentos o realizar una edición externa autorizada.
