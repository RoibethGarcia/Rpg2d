# La última válvula

RPG isométrico postapocalíptico con Python y Pygame, construido sobre el motor de clase 8. Vera, técnica de La Hondonada, debe recuperar la credencial de La Custodia y restablecer el agua desde el panel de la planta.

**Primera iteración:** mapa de 24×16 con acceso industrial, patio de distribución y sala de control; tres guardias y un jefe, combates 1 contra 1, suministros limitados, victoria, derrota y nueva partida. Arte industrial **provisional**, no una entrega artística terminada. [Diseño](HistoriaYMecanicas.md) · [Implementación por fases](docs/IMPLEMENTACION.md) · [Validación y límites](docs/VALIDACION.md).

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
| E o «Interactuar» | Recoger/examinar/activar objetos cercanos fuera de combate |
| Espacio o «Fin turno» | Ceder voluntariamente el turno |
| Escape en partida | Cancelar pasos futuros; termina el paso en curso |
| «Volver al menú» | Regresar al menú; «Comenzar» crea estado limpio |
| Escape en victoria/derrota | Volver al menú |
| Cerrar ventana / «Salir» en menú | Cerrar Pygame ordenadamente |

Las direcciones se refieren a la **rejilla**, no a arriba/abajo de la pantalla isométrica. WASD cancela el recorrido y prepara un paso nuevo después del actual. El clic en paneles de UI no atraviesa al mundo. No hay atajos numéricos de habilidades.

### Objetivo y táctica

1. Explorar el acceso, conseguir suministros y activar con E el mantenimiento para abrir el paso al patio.
2. Superar los guardias del acceso y del patio; recoger los dos botiquines del mapa antes del jefe.
3. Vencer al jefe para obtener automáticamente su credencial.
4. Llegar a una casilla **vecina** al panel final y pulsar E, fuera de combate. Solo entonces vuelve el agua.

Cada turno dispone de **6 PA**: caminar 1, llave 2 (daño 4), potente 3 (daño 7), botiquín 2 (cura hasta 8). Vera comienza con 30 de vida y un botiquín; guardias 16 de vida/daño 3; jefe **48** de vida/daño 4. Enemigos gastan 2 PA por ataque. El botiquín se usa solo en combate. Llegar a 0 PA **NO termina el turno**: pulsa Espacio.

**Maniobrar importa:** combinar un potente y tres pasos de retirada puede impedir que el rival gaste todo su turno atacando. Intercambiar golpes inmóvil contra el jefe no es la estrategia de aceptación. Existe una partida automatizada por los tres guardias y jefe que gana con **2 de vida y ningún botiquín**; demuestra posibilidad, no balance cómodo ni validación con jugadores.

## Pruebas, sin builds

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m unittest discover -s tests -v
```

Resultado registrado: **70 pruebas correctas**. Incluye dominio, mapa real completo, recursos y contratos de escenas. Se comprobó además el arranque nativo macOS con ventana y mixer reales, y el coordinador inspeccionó capturas. SDL dummy no demuestra sonido audible, profundidad correcta en todas las situaciones ni experiencia de juego manual; el smoke nativo tampoco equivale a una partida completa jugada por una persona. No ejecutar builds, `py_compile`, `compileall` ni empaquetado para validar. Detalles en [VALIDACION](docs/VALIDACION.md).

## Recursos y publicación

Se usan recursos gratuitos redistribuibles: humanos CC0 de intellikat, sonidos CC0 de ObsydianX y tuberías BY-SA 4.0 de Darkmoonfire. Suelo, paredes y maquinaria son geometrías propias provisionales dibujadas en Pygame; los packs SBS no están integrados. Créditos, licencias, originales y modificaciones: [ASSETS](docs/ASSETS.md) y `assets/manifest.json`.

**No publicar todavía:** el notebook docente no declara licencia de redistribución. Debe confirmarse permiso para publicar el motor, además de autorizar expresamente la publicación del repositorio. No se creó commit ni se publicó GitLab. [Procedencia y cambios del motor](docs/MOTOR.md).

## Video de entrega: pendiente

El requisito es un video de **15–40 segundos**. Existe un guion y un script preparado; **el video todavía no fue capturado**. Las capturas PNG de pruebas no son el video de entrega.

Con el juego abierto y datos privados ocultos, desde otra terminal macOS:

```sh
bash scripts/grabar_video.sh --record
```

El script inicia selección interactiva nativa de 25 segundos. Selecciona **SOLO la ventana del juego**; usa Espacio para cambiar a selección de ventana si aparece un rectángulo. Cancela con Escape si no puedes aislarla. El sistema puede pedir permiso de grabación de pantalla. Nunca seleccionar el escritorio completo, otras ventanas, notificaciones ni información privada. El script no se ejecuta durante pruebas, no instala herramientas y no activa micrófono; comprobar después si la entrega necesita incorporar sonido del juego. Resultado: `artifacts/demo.mov`, excluido de Git por defecto. Preparar el archivo para entrega explícitamente después de revisarlo.

Guion sugerido de 25–35 segundos, con cortes si es necesario: menú y «Comenzar» (3 s); exploración/ruta e interacción de mantenimiento (6 s); contacto, PA, potente y retirada (8 s); credencial/panel y victoria (6 s); nueva partida o derrota y regreso al menú (4 s). No fingir que ese tramo es una partida completa ni acelerar reglas para grabarlo. Para cubrir todo en un solo clip, preparar previamente los momentos o realizar una edición externa autorizada.
