# Fase 0 — Base compartida de campaña, mapas y arena

**Estado: implementación parcial — tareas 1–2 automatizadas; tareas 3–6 pendientes.** [Índice y originales](README.md) ·
[Siguiente: La Hondonada](01-la-hondonada.md).

## Objetivo, dependencias y límites

Permitir tres mapas reversibles y encuentros aislados sin duplicar vida, inventario
ni lógica. Entregar primero un circuito con geometrías provisionales explícitas.
Depende del juego actual; no requiere arte final. Las otras fases dependen de esta
base, por lo que deben consumir sus contratos, no reconstruirlos.

El primer incremento separa campaña y mapas persistentes: `GameState` conserva una
Vera/inventario/credencial y delega los datos de mundo a `MapState`. `PlayScene`
sigue sirviendo a exploración y combate en rejilla; la aplicación detecta terminales
desde esa escena. La ampliación conserva el motor con `Scene`/`GameObject`, **un solo
bucle** y `dt` en segundos. La arena lateral es una adaptación propia, no del curso.

## Contratos de datos e interfaces a implementar

Los contratos siguientes son el objetivo completo. Campaña, mapas y viaje ya tienen
un primer incremento; encuentro separado y arena siguen PENDIENTES:

| Responsabilidad | Fuente única de verdad y entradas/salidas |
| --- | --- |
| Campaña | Una Vera, botiquines, credencial, mapa activo y colección de estados por ID. Nueva partida crea todo limpio; no hay guardado en disco. |
| Estado de mapa | Rejilla, enemigos reales, NPC, objetos, recogidos, mecanismos abiertos e índices/esperas de patrulla. Se crea una vez por partida, no al entrar. |
| Encuentro activo | Referencia al enemigo del mapa, ID de origen, casilla de retorno de Vera y posiciones tácticas 0…11. No copiar unidades/HP ni sobreescribir sus casillas de exploración. |
| Viaje | Entrada: salida señalizada e interacción E vecina. Valida exploración, ausencia de ruta/paso pendiente y requisito de salida. Resultado: mapa destino y aparición reservada, sin curación ni recursos nuevos. |
| Contacto | Intento de entrar en rival quieto; crea exactamente un encuentro, sin ocupar su casilla, cobrar un paso ni atacar. En tránsito/reservado es bloqueo ordinario. |
| Comandos | La fachada `game.state` delega movimiento, ataque, curación, interacción, fin de turno y actualización según contexto; devuelve resultado válido/rechazado para la UI. No dos estados mutables divergentes. |

Usar IDs estables `hondonada`, `puesto` y `planta`. Las salidas conectan
Hondonada ↔ puesto ↔ planta, sin viaje directo pueblo/planta. La salida puesto →
planta exige mantenimiento abierto; el regreso queda permitido. Reservar las
casillas de aparición en los datos de mapa: transitables, sin objetos bloqueantes
ni rutas de patrulla. Rechazar datos inválidos; no teletransportar al azar.

Los mapas inactivos no avanzan. Durante un encuentro no avanza ninguna patrulla ni
movimiento de exploración. Al contacto se cancelan rutas, órdenes preparadas y
pasos visuales sin adelantar casillas lógicas. Al viajar/entrar/salir de arena se
limpian hover, rutas, movimientos, selección y cachés de actores que pertenezcan
al contexto anterior. Tras victoria del encuentro, volver a la casilla de origen
de Vera, mantener HP y consumos y dejar al enemigo derrotado en su mapa. No hay
huida, recuperación automática ni restauración de vida al viajar.

## Reglas de arena y de presentación

- Una línea de 12 casillas, índices 0…11. Vera comienza en 6 y el rival en 7;
  Vera recibe el primer turno. Alcance de ataque: distancia absoluta igual a 1.
- A/D desplazan un paso; clic ordena el tramo alcanzable sin cruzar al rival.
  Cada paso cuesta 1 PA. No wrap de 11 a 0, saltos ni diagonales; W/S no mueven.
  Cancelar remanentes al terminar turno; no continuar la ruta en el turno siguiente.
- Espacio o botón termina voluntariamente el turno, incluso con 0 PA. Llegar a
  cero no cambia automáticamente de turno. Ataques/curación requieren turno propio
  y movimiento detenido. Validar todo antes de consumir PA/ítems.
- Enemigo se acerca por la línea y ataca mientras alcance y PA lo permitan; usa
  el presupuesto de 6 PA por su turno. Sin detectar otros enemigos ni invocarlos.

| Valor inicial conservado | Cantidad |
| --- | --- |
| Vera: vida máxima/inicial; botiquines iniciales | 30 HP; 1 |
| PA por turno; paso | 6; 1 PA |
| Llave básica | 4 daño, 2 PA |
| Potente | 7 daño, 3 PA |
| Botiquín, solo combate | Hasta 8 HP, 2 PA, consume 1 |
| Guardia | 16 HP, 3 daño, ataque 2 PA |
| Jefe | 48 HP, 4 daño, ataque 2 PA |

Mantener una escena de exploración parametrizada por mapa y una escena de arena,
sin tres clases de exploración duplicadas ni loops anidados. Adaptar la detección
de victoria/derrota de la aplicación para incluir la arena. Bloquear gameplay en
terminales y mantener retorno a menú/nueva partida.

Mundo industrial: 24×16 por mapa, tiles 48×24, cuatro vecinos lógicos y un plano navegable.
**Excepción autorizada el 19 de octubre:** La Hondonada conserva casillas lógicas,
pero usa superficies/pies visuales autorados y conectividad explícita para unir
terrazas mediante escaleras transitables. La adyacencia numérica sola NO permite
atravesar paredes ni saltar desniveles. Este cambio no implementa una física 3D
ni altera los mapas industriales. Ver [contrato actualizado](01-la-hondonada.md).
Dominio por casillas, independiente de `Rect` o píxeles. Render modular: suelo;
edificios/obstáculos/objetos/actores con profundidad por pie y desempate estable;
elementos delanteros de ocultación; UI aparte. No dibujar todos los edificios por
encima de todos los actores. Separar render isométrico de arena lateral.

Recurso humano por rol/personaje, orientación y contexto (`world`/`arena`), con
rectángulo de origen, escala proporcional y ancla local configurable. El pie
escalado acompaña la escala. Eliminar el supuesto universal 64×64/ancla (32,62)
sin reemplazar las imágenes compartidas `human_*` globalmente. No tintar los PNG
nuevos por rol. Cargar/cachear recursos fuera del frame desde la raíz del proyecto.

## Assets disponibles y faltantes

Consultar inventario en [índice](README.md). Ya existen plantillas y geometrías
provisionales que permiten probar contratos. Los PNG nuevos son originales locales
de referencia, todavía sin derivados incorporados por esta entrega. Faltan módulos
reutilizables, sprites normalizados, fondo de arena limpio y UI por capas.

En la implementación, registrar en manifiesto/créditos origen declarado, nombre
original, derivado, hash, dimensiones, transparencia, rectángulos/anclas y cambios.
No inventar autor/licencia ni extender CC0/BY-SA a los PNG aportados. La ejecución
no dependerá de Downloads. Un recurso obligatorio inválido debe fallar claramente;
los placeholders del prototipo se declaran como tales, no mediante excepciones
amplias que silencien problemas.

## Tareas ordenadas — progreso incremental

1. **Implementada y automatizada:** pruebas RED de campaña nueva y viaje ida/vuelta; separar estado de mapa
   de campaña y mantener la fachada de comandos. Conservar tests actuales aplicables.
2. **Implementada y automatizada:** congelación de mapas, reservas y viajes inválidos; tres mapas
   provisionales y salidas reversibles con el bloqueo de mantenimiento.
3. **Pendiente:** probar contacto y contexto de retorno; implementar encuentro sin copiar HP ni
   trasladar casillas de exploración a índices tácticos.
4. **Pendiente:** probar arena, turnos, alcance y acciones inválidas; implementar reglas y escena
   mínima usando gráficos provisionales. Integrar terminales y reinicio global.
5. **Pendiente:** probar metadatos/selección/transformaciones; preparar render modular y recursos
   por rol/contexto. Integrar entrada de UI sin propagación al mundo.
6. **Pendiente para la fase completa:** refactorizar, ejecutar runner del índice y comprobar manualmente transiciones.
   Documentar resultados y límites sin dar por terminado el arte.

## Pruebas y checklist de aceptación

- [x] Campaña nueva instancia mapas independientes; reiniciarla borra todo progreso.
- [x] Ida/vuelta conserva HP, PA, consumos, recogidos, mecanismos y enemigos derrotados.
- [x] Viajes rechazados en combate actual, terminales, movimiento/ruta/orden preparada
  o sin requisito; rechazo sin modificar mapa, HP, PA, inventario ni posición.
- [ ] Extender la comprobación a arena cuando exista.
- [x] Mapas inactivos congelados, incluyendo espera/índice de patrulla y reloj fraccional.
- [x] Combate actual pausa patrullas; no avanza mapas inactivos.
- [ ] Comprobar congelación del mundo desde la futura arena.
- [ ] Contacto desde Vera o enemigo inicia exactamente un duelo sin paso/ataque gratis.
- [ ] Arena prueba extremos 0/11, ocupación, presupuesto, rechazo sin mutación,
  tramo de clic, cancelación y fin voluntario con 0 PA.
- [ ] Victoria de encuentro restaura exploración; derrota en arena abre pantalla
  de derrota; nueva partida no conserva referencias agotadas.
- [x] Viajes limpian contexto visual/hover/actores sin recargar imágenes; rechazan órdenes pendientes.
- [ ] Extender limpieza de contexto a entrada/salida de arena.
- [ ] Prototipo permite visitar mapas y completar un encuentro con placeholders
  explícitos, sin necesitar los recursos nuevos.
- [ ] Metadatos y rutas se validan; UI no transmite clics; revisión manual separada
  de pruebas dummy. Registrar evidencias antes de marcar.


## Evidencia del primer incremento — 19 de octubre de 2026

Se implementan SOLO tareas 1–2. `MapState` posee rejilla, enemigos, objetos,
recogidos, mecanismos y progreso temporal de patrullas; la fachada delega por
referencia, sin sincronizar copias. `GameState.new()` crea todo nuevamente.
No se guarda en disco. Las apariciones/vecinos seguros se reservan en datos y
la carga rechaza reservas bloqueadas/ocupadas, patrullas sobre ellas y salidas
inválidas con `ValueError`. Un destino inválido al viajar se rechaza sin buscar
otra casilla. Cualquier paso pendiente, incluso de patrulla, impide viajar.

Circuito provisional:

| Mapa | Salida (casilla señalizada; pulsar E desde un vecino) | Aparición en destino |
| --- | --- | --- |
| Hondonada | `(5,10)` → puesto | `(2,10)` |
| Puesto | `(1,11)` → Hondonada | `(4,10)` |
| Puesto | `(8,8)` → planta, tras mantenimiento `(6,9)` | `(9,8)` |
| Planta | `(8,8)` → puesto, regreso sin requisito | `(9,8)` |

En ese primer incremento, Hondonada usaba geometría simple; el posterior escenario
por capas y escaleras sustituye solo ese layout, según su documento. Puesto y planta reutilizan geometría industrial
provisional del prototipo, NO layouts ni cantidades finales: un guardia en puesto,
dos guardias y jefe en planta, un recogible por mapa industrial. No hay aldeanos.
Las señales de salida y el encabezado indican el mapa; el render modular sigue
pendiente. Los seis PNG humanos previamente integrados se conservan intactos.

El combate sigue en la rejilla original: no se implementó arena lateral, encuentro
separado, retorno de arena ni recursos por contexto. La regresión del mapa único
se conserva como fixture `new_legacy_game()`, no como partida inicial. Hay además
un recorrido NUEVO de campaña mediante comandos públicos, sin teletransportes ni
alterar HP/inventario: visita ambos sentidos, conserva progreso, vence tres guardias
y jefe y activa panel; termina con **2 HP y 0 botiquines**. Esto NO valida las
cantidades/balance finales del plan de cinco guardias ni una experiencia humana.

TDD registrado: RED por colección de mapas ausente; RED por E vecino sin viaje;
RED por aparición inválida aceptada; RED por hover/actores antiguos conservados;
RED por salida bloqueada que permitía viajar. Después de cada cambio se repitieron
las pruebas pertinentes hasta GREEN. Comandos y resultado completo en
[VALIDACION](../VALIDACION.md). Sin builds, instalaciones ni revisión manual nativa.
