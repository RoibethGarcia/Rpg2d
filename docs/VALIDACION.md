# Validación — primera iteración

Fecha: **15 de octubre de 2026**. Resultado automatizado final de esta revisión: **70 pruebas correctas, salida 0**. No equivale a certificar todos los entregables ni a afirmar que una persona completó la partida.

## Pruebas ejecutadas

Desde la raíz del proyecto, con el intérprete del entorno que contiene Pygame:

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m unittest discover -s tests -v
```

Ejecución final: `Ran 70 tests in 1.019s`, `OK`, exit 0. Usar un Python global sin Pygame no es este comando; un fallo de importación por intérprete equivocado no constituye RED válido ni éxito.

| Área | Archivo de pruebas | Cantidad | Evidencia |
|---|---|---:|---|
| Motor | `test_engine.py` | 11 | Segundos, sobrante de animación, API sonora, botones, QUIT y limpieza ante excepción; recursos relativos al JSON. |
| Mundo | `test_world.py` | 3 | Límites, obstáculos, proyección/inversa, negativos, cámara y BFS estable. |
| Modelo | `test_model.py` | 17 | Reservas, contacto, PA, alcance, curación, turnos, derrota, credencial, interacción y patrullas. |
| Contenido y partida completa | `test_playthrough.py` | 3 | Balance y datos independientes; patrullas válidas; partida real con mapa y recursos aprobados. |
| QA independiente de dominio | `test_regressions.py` | 12 | Contacto a mitad del tick, bloqueo/reserva, atomicidad, terminales, reset anidado, tiempos y selección desplazada. |
| UI | `test_ui.py` | 11 | Herencia, menú, nueva partida, clic UI aislado, transiciones, carga única, audio/canal e interpolación sin mover casilla lógica. |
| Integración independiente | `test_integration.py` | 9 | Otro directorio, import sin efectos, equivalencia clic/WASD, botones y turnos, derrota, panel/victoria y reinicio. |
| Recursos | `test_assets.py` | 4 | Manifiesto, procedencia, hashes, licencias, dimensiones, transparencia, frames y decodificación OGG. |
| **Total** | | **70** | Sin builds ni compilación de validación. |

La integración UI de victoria usa una **fixture de jefe** para aislar transiciones; no debe confundirse con recorrer todo el mapa mediante la UI. El recorrido completo usa comandos públicos del dominio, sin teletransportar, alterar vida, inventario ni balance: vence a los tres guardias y al jefe de **48 de vida**, obtiene credencial y activa panel. Termina con **2 de vida y 0 botiquines**. Prueba existencia de una estrategia con maniobra, no dificultad adecuada para principiantes.

## Hallazgo independiente y corrección RED → GREEN

**Impacto alto, corregido:** contacto con enemigo al completar un paso podía cerrar la aplicación con `KeyError: 'patrol'`.

- Repro: Vera `(2,2)` ordena ruta hasta el guardia quieto `(5,2)`. Otra patrulla parte de `(7,5)` hacia `(7,4)` con pausa de 0.14 s. Dos llamadas públicas `state.update(.14)` sincronizan el segundo paso de Vera con el de la patrulla.
- **RED real:** `test_contact_mid_tick_cancels_other_motion_without_stale_commit_or_crash` falló en `game/model.py`, `_tick`, al ejecutar `del self.motions[uid]`. No fue error de importación, dependencia ni sintaxis.
- Causa: el contacto cancela todos los movimientos, pero `_tick` continuaba consumiendo una instantánea anterior del diccionario; podía confirmar posición y cobrar PA de un paso ya cancelado antes de borrar una clave inexistente.
- Corrección realizada por el propietario de dominio: comprobar identidad del movimiento todavía activo antes de avanzar tiempo, confirmar posición o cobrar costo. La revisión QA no editó archivos de implementación ajenos.
- **GREEN:** la regresión conserva Vera `(4,2)`, rival `(5,2)`, patrulla `(7,5)`, vida intacta, 6 PA, sin rutas ni movimientos pendientes; suite independiente y suite completa aprobadas.

Otros 11 casos independientes ampliaron cobertura del comportamiento existente; no se presentan como nuevas correcciones inventadas. Durante la integración también se avisó una referencia temporal a `state` en el render del menú; el propietario la corrigió antes de la suite final y los tests de dibujo del menú pasan.

## Inspección estática y arranque real

- Leídos mundo, modelo, carga de contenido, datos y pruebas; contrastados con los valores y contratos aprobados. Actualizados diseño, instalación, controles, estado por fases y procedencias sin modificar los acuerdos futuros de grupo.
- `bash -n scripts/grabar_video.sh`: salida 0. Consultada la ayuda local de `/usr/sbin/screencapture`: confirma `-v`, `-V<seconds>` e `-i`. **No se ejecutó captura de pantalla/video** en esta revisión; solo se preparó el script opt-in.
- El propietario del motor realizó un **smoke GUI nativo autorizado**, sin SDL dummy: driver `cocoa`, mixer `(44100,-16,2)`, nueva partida y llamada al sonido de confirmación, cierre QUIT tras 2.2 s; exit 0. Captura exclusiva de la superficie del juego en `artifacts/smoke-real.png`, no del escritorio.
- El coordinador inspeccionó capturas de menú, partida, combate y smoke real. Comprobó legibilidad general de esas capturas; no es una prueba exhaustiva de profundidad o interacción.
- Capturas de victoria/derrota generadas como fixtures de render no prueban que una persona haya ganado/perdido manualmente una partida completa.

## No ejecutado / pendiente

- **Partida manual completa** con teclado/ratón, calidad de maniobra, accesibilidad, profundidad en todos los solapamientos y ajuste de dificultad.
- **Percepción sonora real:** cargar mixer y llamar a reproducción no demuestra que una persona oyera ni evaluara el resultado. SDL dummy solo comprueba contratos/decodificación.
- **Video de 15–40 segundos:** todavía no existe `artifacts/demo.mov`. Script de 25 s y guion preparados; seleccionar únicamente ventana del juego requiere usuario y permisos de macOS. No instala encoder, no usa micrófono ni publica archivos.
- Permiso de **redistribución del motor docente**, no declarado en notebook; publicar repositorio requiere además autorización expresa. GitLab, commit y publicación no realizados.
- Tests en Windows/Linux y otros tamaños de pantalla no ejecutados. No afirmar compatibilidad validada fuera del entorno macOS ARM64/Python 3.13 comprobado.
- Arte final de personajes/maquinaria y packs SBS pendientes; geometría provisional explícita y archivos reales acreditados en [ASSETS](ASSETS.md).

No se ejecutaron builds, `py_compile`, `compileall`, empaquetado ni compilación de dependencias. Compañeros y combate múltiple no forman parte de la aceptación inicial.

## Reemplazo estático de personajes — 19 de octubre de 2026

Alcance: seis originales de Vera, guardias y jefe, frente/espalda. No se cambió
el dominio ni el mapa. Escenarios, aldeano, arena/menú y animaciones no integrados.

### TDD realmente ejecutado

Prefijo de todos los comandos siguientes:

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy
```

1. RED: `.venv/bin/python -m unittest tests.test_character_assets -v` →
   **5 fallos de aserción**, por faltar los seis recursos del manifiesto.
2. Tras copiar originales y registrar metadata, antes de cambiar el renderer,
   el mismo comando confirmó **8 fallos de aserción y 1 error de API aún ausente**:
   tamaños 64×64 incorrectos, barra sobre el torso, falta de error cuando no existe
   `vera_front` y ausencia de anclas por vista. El RED válido corresponde a las
   aserciones, no al error de atributo.
3. GREEN: `.venv/bin/python -m unittest tests.test_character_assets tests.test_assets -v`
   → **9 pruebas correctas**.
4. Regresión: `.venv/bin/python -m unittest discover -s tests -v`
   → **75 pruebas correctas**, incluido el recorrido completo actual.

Se comparan buffers RGBA contra los PNG preparados con el mismo subrect y escala,
se prueban frente/espalda por movimiento en los tres roles, pie estable sin alterar
casillas, carga única, barras encima del arte, hashes y procedencia diferenciada
sin inventar licencia. Los packs anteriores conservan sus validaciones de licencia.

### Inspección y límites

Se inspeccionaron los seis PNG originales mediante visor. Se dibujó una partida
real `LastValveGame(audio_enabled=False)` con SDL dummy y se capturó
`/tmp/rpg2d-new-characters.png`; también `/tmp/rpg2d-character-views.png`, galería
diagnóstica de las superficies del renderer sobre gris. Se inspeccionaron ambas:
los personajes nuevos son visibles, con siluetas completas y sin fondo negro,
y las seis vistas conservan anclas y proporción. Son capturas temporales de
validación, no nuevos assets ni evidencia permanente versionada.

No se ejecutó partida manual nativa, no se verificó sonido físico, no se editaron
las imágenes fuente y no se generaron bitmaps derivados de producción. No se
instaló nada, no se ejecutaron builds/compilación, no se creó commit ni se publicó.
La redistribución de los PNG aportados sigue pendiente de confirmación.

## Base de campaña — primer incremento, 19 de octubre de 2026

**Alcance implementado: tareas 1–2 de fase 0, NO fase 0 completa.** Una Vera,
inventario y credencial compartidos; tres `MapState` provisionales persistentes;
viajes Hondonada ↔ puesto ↔ planta mediante E vecino, con mantenimiento para
puesto → planta. Combate conservado en rejilla, sin arena nueva. Distribución
provisional conservada: un guardia en puesto, dos y jefe en planta, dos botiquines
recogibles en total; no equivale a las cantidades finales del plan.

### Comandos y evidencia TDD

Todos los comandos usan el prefijo:

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy
```

- Baseline: `.venv/bin/python -m unittest discover -s tests -v` →
  `Ran 75 tests in 3.921s`, `OK`.
- RED: `.venv/bin/python -m unittest tests.test_campaign -v` →
  primero **1 fallo de aserción** por colección de mapas ausente; siguiente
  incremento **2 fallos** porque E vecino no viajaba. GREEN de ambos incrementos
  con la misma selección y pruebas de modelo: **18**, después **20** correctas.
- RED: `.venv/bin/python -m unittest tests.test_campaign.CampaignTests.test_invalid_initial_spawn_is_rejected_not_relocated -v`
  → **1 fallo**, no lanzaba `ValueError`. Tras validar datos, selección campaña/modelo:
  **21 correctas**.
- RED: `.venv/bin/python -m unittest tests.test_campaign_ui -v` →
  **2 fallos de aserción**, hover y actores persistían al cambiar de mapa.
  GREEN tras sincronizar revisión de contexto, sin recargar imágenes.
- RED: `.venv/bin/python -m unittest tests.test_campaign.CampaignTests.test_runtime_invalid_exit_cell_or_malformed_spawn_is_rejected_atomically -v`
  → **1 fallo**, salida bloqueada permitía viajar. Corregido validando salida y
  formato de aparición antes de mutar. Selección campaña/UI/modelo: **30 correctas**.
- Recorrido nuevo: `.venv/bin/python -m unittest tests.test_playthrough.FullPlaythroughTests.test_campaign_public_commands_travel_both_ways_and_complete_current_combat tests.test_character_assets tests.test_campaign_ui -v`
  → **8 correctas**. Comandos públicos, sin teletransportes ni modificar recursos:
  ida/vuelta en ambos enlaces, progreso conservado, tres guardias y jefe vencidos,
  credencial y panel final; **2 HP y 0 botiquines**.
- Regresión final: `.venv/bin/python -m unittest discover -s tests -v` →
  **`Ran 89 tests in 4.194s`, `OK`, salida 0**.
- Inspección estática: `git diff --check` → salida 0.

La campaña añade 14 pruebas (11 dominio, 2 UI dummy, 1 recorrido completo).
Cubren independencia de mutables, reinicio, viajes válidos/rechazados atómicos,
reserva de apariciones y vecinos, mapas inactivos congelados (incluyendo esperas,
índices y reloj fraccional), congelación de patrullas durante combate actual,
limpieza de hover/actores y carga única. El recorrido histórico conserva todas
sus aserciones con fixture explícita `new_legacy_game()`. La prueba visual de tres
roles también usa esa fixture, sin modificar sus aserciones: Hondonada ya no
contiene enemigos y no sería una fixture suficiente para probar todos los sprites.

### Límites de esta ejecución

No se realizó partida manual, arranque nativo ni nueva inspección de capturas.
Dummy NO certifica legibilidad de señales, profundidad, sonido audible ni balance
humano. No se implementaron encuentros separados, arena de 12 casillas, NPC,
contenido/cantidades finales, metadatos por contexto ni render modular. Cada viaje
requiere que no quede ningún paso pendiente, incluidos los pasos de patrulla;
si una patrulla está animándose, esperar y reintentar E. Viajar no cura, no repone
PA y no restaura consumibles. No hubo builds, empaquetado, instalaciones ni commits.
Los cambios previos de sprites, manifiesto y procedencias se conservaron.

## Incremento visual modular de escenarios — 19 de octubre de 2026

**Alcance:** atlas generado nuevo a partir de tres referencias locales del usuario;
16 piezas con recortes explícitos, suelos/muros y decoración por mapa. No es un
fondo completo ni un cambio de navegación, colisiones, enemigos, PA o balance.
Hondonada sigue casi vacía y sus módulos pequeños se apoyan en el borde bloqueado.
NPC, arena lateral, animaciones y layouts finales no están implementados.

### TDD realmente ejecutado

Desde la raíz del juego se ejecutó:

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m unittest tests.test_environment_assets -v
```

- **RED:** 7 fallos de aserción `Falta el renderer modular de escenarios`; aplicación
  inicializable con dependencias presentes, sin fallos de importación/sintaxis.
- **GREEN:** mismo comando, 7 pruebas correctas tras incorporar `EnvironmentArt`,
  configuración por mapa y atlas real.
- **REFACTOR/regresión final:** runner completo de README, **96 pruebas correctas**
  (5.654 s, SDL dummy); incluye viajes/campaña, fixtures legacy y las nuevas pruebas.
  El conteo anterior de campaña era 89; se añadieron 7 pruebas de entorno.
- Auditoría de `tests.test_assets` extendida: atlas `ai_generated` no se presenta
  como PNG suministrado ni como pack CC0; exige prompt/procedencia y comprueba los
  hashes de las tres referencias. Continúan verificados todos los recursos anteriores.

Los siete casos cubren: estilos y píxeles texturados distintos para los tres mapas;
selección correcta después de viajar sin recargas ni cambios de dominio al dibujar;
error explícito para mapa desconocido/configuración ausente; atlas ausente;
huellas bloqueadas fuera de apariciones/objetos/salidas; orden de decoración y
actores por pie; recortes contenidos, no vacíos, con anclas dentro de su imagen.

### Capturas reales y límites

Se capturó `PlayScene` con SDL dummy usando la aplicación real en:

- `/tmp/rpg2d-hondonada-environment.png`
- `/tmp/rpg2d-puesto-environment.png`
- `/tmp/rpg2d-planta-environment.png`

Para prepararlas se inició una partida nueva, se posicionó Vera mediante fixture
junto a la salida y se usó `travel(...)`. El acceso a planta se habilitó explícitamente
en esa fixture; NO es evidencia de un recorrido manual ni de combate ganado.
Las capturas se volvieron a generar tras actualizar la etiqueta de procedencia
visual. Se revisaron los tres renders: módulos diferenciados, transparencia,
profundidad y señalización visibles. Persisten repetición del suelo, distribución
provisional y leves halos rojizos del atlas generado. Esto no valida todas las
situaciones de oclusión, calidad artística final ni sonido físico.

**No se ejecutaron builds, empaquetado, instalaciones ni compilación de validación.**
No se modificó el `assets.md` del usuario. No se publicó ni creó commit.

## La Hondonada por capas y escaleras — 19 de octubre de 2026

El usuario autorizó usar su ilustración como escenario recorrible por capas,
incluidas escaleras. Esta autorización sustituye el límite anterior de plano único
para Hondonada; no marca fases 0–1 completas ni añade NPC/diálogos o arena.

### Auditoría del nuevo recurso: RED → GREEN

Desde la raíz del juego:

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m unittest discover -s tests -p test_assets.py -v
```

1. **RED real:** 5 pruebas ejecutadas, 1 fallo de aserción en
   `test_hondonada_clean_plate_is_registered_with_exact_source_and_prompt`:
   `'hondonada_plate' not found`. No fue un error de importación ni dependencia.
2. Se copió la salida de `image_gen.imagegen` sin modificar bytes; se registraron
   ruta, SHA-256, referencia exacta, prompt, dimensiones y política de fondo opaco.
3. **GREEN:** mismo comando, **5 pruebas correctas** (`Ran 5 tests in 0.233s`,
   `OK`, salida 0). Continúan verificados los hashes y la transparencia de los
   recursos anteriores. Las imágenes IA requieren referencias no vacías, no una
   cantidad universal de tres que solo correspondía al atlas.

Pygame confirmó placa **1448×1086 RGB de 24 bits, sin alfa**, esquina `(2,2,2,255)`;
no se convirtió negro en transparencia. La fuente aportada coincide SHA-256 con
`assets/reference/scenarios/hondonada.png`. Los hashes completos y el prompt
exacto figuran en manifiesto/procedencia. El prompt documenta lo solicitado,
no garantiza identidad píxel a píxel del resultado generativo fuera del personaje.
Se inspeccionó la placa completa en visor: plaza sin el personaje incrustado,
estación, terrazas, escaleras y exterior oscuro visibles. Esta inspección del
recurso no demuestra todavía el render jugable ni los solapamientos de Vera.

### Límites de la auditoría de recursos

Este bloque registra solo los comandos ejecutados para los recursos. Las pruebas
de navegación, escaleras, selección y oclusión se documentan aparte al verificar
el incremento completo; 5 pruebas de assets NO prueban por sí solas la jugabilidad.
No se ejecutaron builds, compilación, instalaciones, publicación ni commits.
No se certifica partida manual nativa, sonido físico o revisión de cada oclusión.

### Navegación, escaleras y presentación: incremento completo

El contrato final de `data/hondonada.json` contiene **228 nodos, 234 conexiones
bidireccionales, seis escaleras y 12 máscaras delanteras**, con coordenadas fuente
relativas a la placa 1448×1086, sin rutas de Downloads ni del equipo del autor.
Los niveles fraccionarios de peldaños son metadatos; no se implementó física 3D.
F3 alterna un overlay de rutas/escaleras; comienza apagado.

La QA independiente recorrió desde aparición las seis escaleras usando comandos
públicos `set_destination` y `move_direction`: **44 pasos de peldaño ida/vuelta**,
con 30 HP, 6 PA y un botiquín intactos. Es una comprobación automatizada, no una
partida manual. La prueba persistente comprueba cada tramo y sentido, vecinos
direccionales, rechazo de atajos de acantilado y reservas de destino.

**Regresión de oclusión RED → GREEN:**

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m unittest discover -s tests -p test_hondonada.py -v
```

La aserción de comportamiento en
`test_bridge_and_west_porch_do_not_lose_vera_behind_their_own_facades` falló con
`0.2197452229299363 not greater than 0.3 : ((4, 6), [164.0, 633.0])`:
el porche ocultaba indebidamente el cuerpo. Ajustar su profundidad de 635 a 600
y el centro final del puente de `(1200,565)` a `(1200,582)` restauró el apoyo y
la visibilidad; la misma selección dio **8 pruebas correctas** (`1.668s`).
Una prueba posterior de metadatos de nivel falló porque los extremos de la
escalera de madera declaraban `(1,1)` en vez de `(1,2)`; se corrigieron los niveles
de peldaños y extremos, y la selección quedó en **9 pruebas correctas**.
No se cuenta como RED válido un primer diagnóstico del test pixelero con división
por cero: se corrigió esa prueba antes del fallo real de comportamiento.

**Regresión final independiente**, después de los ajustes:

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m unittest discover -s tests -v
```

Resultado definitivo: **`Ran 106 tests in 10.530s`, `OK`, salida 0**.
`git diff --check`: sin salida, correcto. Los conteos históricos 75/89/96 y los
GREEN intermedios de esta revisión no sustituyen esta ejecución final.

Capturas locales generadas con la aplicación real y SDL dummy:

- [Vista general](../artifacts/hondonada-overview.png).
- [Rutas de diagnóstico F3](../artifacts/hondonada-navigation.png).
- [Escaleras: extremos y puntos medios](../artifacts/hondonada-stairs-contact.png).
- [Mercado, puente y terrazas](../artifacts/hondonada-platforms-contact.png).

Las hojas de contacto usan colocación directa mediante fixtures para aislar el
render, NO prueban que una persona haya recorrido esos puntos. Se inspeccionaron
ambas hojas: Vera permanece visible y apoyada en los puntos capturados de
escaleras/terrazas. No demuestra alineación ni oclusión perfectas en todo el mapa.
Las capturas son diagnósticas locales, excluidas de Git mediante `artifacts/`;
no son assets obligatorios ni el video de entrega.

El muestreo independiente de 234 aristas, ambos sentidos y cinco fracciones por
arista revisó **2340 posiciones renderizadas**: ninguna quedó completamente
invisible. El mínimo de cuerpo visible fue aproximadamente 19 % detrás de
`mercado_sur`; esa ocultación parcial intencional no demuestra por sí sola que
cada máscara sea artísticamente perfecta. La regresión específica de puente y
porche exige más de 30 % del cuerpo visible en sus casillas para impedir que
las fachadas oculten de forma incorrecta a Vera.

No se repitió arranque nativo, no se jugó una partida manual completa ni se evaluó
sonido audible. No hay NPC, diálogos nuevos, arena lateral ni animaciones de
caminar/ataque en este incremento. Las fases 0–1 siguen parcialmente pendientes.

## Puesto ilustrado explorable — 19 de octubre de 2026

Incremento posterior a Hondonada: `data/puesto.json` registra **42 nodos, 46
conexiones y cuatro máscaras de primer plano** sobre la placa limpia 1448×1086.
Dos guardias reales (`guard1`, `guard2`) patrullan el puesto; `guard3` y el jefe
permanecen en planta. Se conserva el combate 1 contra 1 **in situ**, sin arena
lateral ni cambios de costes/daño. La fase 2 del plan sigue parcialmente pendiente.

### TDD y correcciones verificadas

- RED de dos guardias y navegación autorada, seguido de implementación de datos.
- RED de presentación: faltaban arte por capas y proyección del puesto.
- RED de alcance: ataques/IA dependían de distancia Manhattan entre identificadores
  de nodos. Ahora consultan conexiones reales mediante `grid.can_step`; no hay
  ataques entre casillas numéricamente vecinas pero desconectadas.
- RED de inicio directo: `--map puesto` no iniciaba partida antes del loop.
  Ahora crea una campaña fresca con 30 HP, un botiquín y dos guardias a 16 HP;
  el arranque normal mantiene el menú y una nueva partida comienza en Hondonada.
- QA visual detectó un acceso que cruzaba roca/valla y nodos sobre el camión.
  Se sustituyó por los peldaños reales y corredores alineados con la carretera;
  los tests rechazan el atajo anterior y comprueban centros seleccionables.
- RED de oclusión: el camión dejaba visible solo **13,17 %** de Vera en un nodo
  delantero. Su profundidad pasó de 373 a 350; la regresión exige más de **65 %**
  de píxeles visibles tanto en ese nodo como en el punto medio del tramo.
- RED de preview: una ruta por capas informaba siete pasos alcanzables con dos
  PA, provocando números negativos en la UI. Se limita a `min(longitud, PA)`;
  el resto se muestra ámbar, sin modificar los PA del dominio.

### Pruebas automatizadas definitivas

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -B -m unittest discover -s tests -v
```

Implementación: **123 pruebas correctas en 14,392 s**. Repetición independiente
después de congelar código/datos/tests: **`Ran 123 tests in 14.279s`, `OK`, salida
0**. `git diff --check`: sin errores. Los resultados anteriores de 106/119/122
son históricos o intermedios, no sustituyen este resultado definitivo.

La QA independiente verificó además mediante comandos públicos:

- Campaña completa hasta victoria, terminando con **2 HP y cero botiquines**,
  sin adulterar vida ni consumibles para ganar.
- Hondonada → puesto → recogida del kit → mantenimiento → planta → puesto,
  evitando patrullas con espera: **30 HP, dos botiquines y ambos guardias vivos
  a 16 HP**; no es obligatorio matar para progresar.
- Persistencia de derrotas, objetos y recursos al viajar; contacto de cada
  patrulla inicia un solo duelo con 6 PA. Esperar cinco segundos durante el turno
  del jugador no modifica HP/PA ni mueve otras patrullas o mapas inactivos.

### Inspección visual y límites

Capturas de la aplicación real con SDL dummy, inspeccionadas por implementación,
QA y coordinación; no representan una partida manual nativa:

- [Vista general, F3 apagado](../artifacts/puesto-overview.png).
- [Combate con guardia real](../artifacts/puesto-combat.png).
- [Diagnóstico de rutas](../artifacts/puesto-qa-overview.png).
- [Peldaños y puntos medios](../artifacts/puesto-qa-stairs-contact.png).

Se comprobaron **42/42 centros seleccionables** y 21 muestras por cada una de las
46 aristas, sin cruces de máscaras de obstáculos. El muestreo de actores en nodos
y puntos medios confirmó la corrección del camión. Queda ocultación parcial por
el prop de mantenimiento en un punto medio (aproximadamente 35,9 % visible),
sin bloqueo de navegación; no se afirma oclusión perfecta en todos los píxeles.
Las hojas de contacto usan fixtures de posición para aislar el dibujo.

El modo de prueba se ejecuta con `.venv/bin/python -B main.py --map puesto`.
**No se ejecutaron builds, compilación, instalaciones ni commits.** Pendientes:
partida nativa y sonido audible, animaciones, arena lateral del plan y confirmación
de permisos de redistribución de referencia/derivado. Los originales se conservaron;
la placa limpia es una edición mediante `image_gen.imagegen`, con prompt y hashes
en `assets/provenance/puesto-clean-prompt.md` y `puesto-layered.md`.

## Planta ilustrada, jefe y válvula final — 20/10/2026

### Implementación y evidencia RED/GREEN

- RED inicial: planta carecía de grafo autorado, de arte por capas y de los
  guardias/kits adicionales. GREEN: `data/planta.json` registra 72 nodos,
  76 aristas, cinco escaleras, seis máscaras, tres guardias y jefe reales.
- RED de interacción: dirección preparada y pasos de patrulla permitían activar
  el final. Ahora la válvula rechaza esos estados sin mutar recursos/progreso.
  Vecindad usa `grid.can_step`, no Manhattan sobre IDs arbitrarios.
- RED de acceso rápido: `--map planta` era rechazado por CLI/aplicación. Ahora
  inicia campaña fresca, 30 HP/1 kit, enemigos vivos y sin credencial; no abre
  mantenimiento ni concede el kit del puesto. Menú/nueva partida conservan inicio normal.
- Revisión de captura corrigió el acceso inferior: los cuatro puntos de escalera
  van de `(385,548)` a `(451,487)` de la placa. La grúa se intercala por profundidad;
  el suelo pasa detrás del mástil, no por su base. La excepción `route_behind`
  es de presentación, no un nuevo tipo de colisión ni un permiso de caminar por paredes.
- Primera placa editada aún mostraba la pequeña figura del patio. Una segunda
  pasada la retiró. Se conserva original, intermedio no cargado y resultado activo
  `planta-clean-v2.png`, con hashes, prompts y redistribución pendiente.

### Automatización ejecutada, sin builds

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -B -m unittest discover -s tests -v
```

**136 pruebas correctas**, salida 0. `git diff --check`: sin errores.
Incluye once pruebas específicas de planta, inicio directo, regresiones de
Hondonada/puesto, fixture legacy y recursos. No hubo builds, `py_compile`,
`compileall`, instalaciones ni commits.

- Todos los centros de suelo son seleccionables. Se muestrean 21 puntos por
  arista frente a las máscaras; solo el paso visual detrás de la grúa se exceptúa
  explícitamente. Agua, reactor, depósito central y exterior no ofrecen caminos.
- Cinco actores se dibujan una vez, sin IO por frame; jefe mantiene escala relativa
  y proporción de su arma. Regresión de siluetas iniciales: más de 65 % visible
  para cada actor. Interpolación de escaleras deriva de los apoyos proyectados.
- Cada patrulla puede iniciar exclusivamente su duelo; otras patrullas/mapas
  quedan congelados en combate. Kits únicos no curan al recoger ni reaparecen.
- Derrota del jefe concede credencial, vuelve a exploración y persiste al viajar.
  La válvula exige credencial, vecino real, exploración y ausencia de pasos/rutas
  pendientes. Rechazos no alteran inventario, HP, PA ni progreso.

### Recorrido integrado y límites

`test_campaign_public_commands_travel_both_ways_and_complete_current_combat`
recorre Hondonada, puesto y planta con comandos públicos y `update`, sin asignar
posiciones, HP, bajas o recursos desde el test. Vence cinco guardias y jefe,
recoge los tres kits del mundo y activa la válvula. Tras guardias 1–5 quedan
**24/26/28/30/30 HP**; jefe: **26/14/2 HP**, final **2 HP/0 kits**.

La estrategia usa potente+retirada de tres pasos en los primeros dos turnos de
cada guardia y remata con básica, curando antes en guardias 2–5. El jefe requiere
retirada inicial y después dos potentes por turno. Una curación en turno separado
gastaba demasiado margen: se corrigió la estrategia del recorrido, NO las cifras
de vida/daño ni los suministros acordados. Ganar con 2 HP demuestra posibilidad,
no comodidad ni aceptación con jugadores.

Capturas locales SDL dummy inspeccionadas:

- [Vista general](../artifacts/planta-overview.png).
- [Navegación F3](../artifacts/planta-navigation.png).
- [Contacto real con jefe](../artifacts/planta-boss-combat.png).
- [Válvula preparada con credencial](../artifacts/planta-valve-ready.png).
- [Victoria tras activar suministro](../artifacts/planta-victory.png).

Las tres últimas se capturaron durante el recorrido por comandos públicos;
no se adulteró la partida para obtener victoria. Las capturas son artefactos
locales ignorados por Git, no parte del código versionado. No se ejecutó una
partida manual nativa ni se comprobó sonido audible. Siguen pendientes la arena
lateral del plan original, animaciones y revisión humana de dificultad y todos
los solapamientos. El portón cerrado y patio exterior inferior son decorativos.
