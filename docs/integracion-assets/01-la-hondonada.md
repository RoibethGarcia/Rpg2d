# Fase 1 — La Hondonada

**Estado: incremento de escenario por capas y escaleras; fase completa pendiente.** [Índice](README.md) ·
[Contrato obligatorio: base compartida](00-base-compartida.md) ·
[Siguiente: puesto](02-puesto-de-control.md).

## Objetivo y dependencias

Crear el pueblo inicial explorable: estación reutilizada, habitantes y radio
presentan la falta de agua y el objetivo de Vera. Depende de la fase 0 aceptada,
incluidos viajes reversibles, recursos por contexto y estados de mapa persistentes.
Esta fase añade contenido a `hondonada`; no otro loop ni otra copia de campaña.

Salida de fase: empezar una partida en el pueblo, conversar, reconocer el camino
principal, viajar al puesto provisional y regresar con el mismo progreso. **Cero
enemigos y cero combates en el pueblo.** Sin misiones, recompensas, tienda ni
curación gratuita. No introducir compañeros.

## Assets disponibles y faltantes

Nombres exactos y procedencia local en [inventario del índice](README.md):
`pueblo-referencia`, `aldeano-taza`, `vera-frente` y `vera-espalda`.

El usuario eligió usar esta ilustración como escenario por capas y autorizó
expresamente escaleras transitables el 19 de octubre de 2026. Se conserva la
referencia original y se incorpora una placa editada con IA para quitar el
personaje incrustado. La placa no incorpora navegación automáticamente: se
añaden superficies transitables, conexiones de escaleras y máscaras delanteras
registradas por separado. Las capas de oclusión se preparan en memoria, no como
PNG separados. [Procedencia y límites](../../assets/provenance/hondonada-layered.md).
No hacen falta animaciones en este incremento.

Preparar los dos sprites de Vera con pies alineados y escala corporal constante;
usar render por recurso, sin el tinte de las plantillas. Reutilizar el mismo arte
del artesano para dos habitantes **con IDs distintos** y estado de diálogo
independiente. No prometer una espalda del aldeano que no fue compartida.

## Contratos y recorrido

- Mapa `hondonada`: conserva coordenadas lógicas `(col,row)` pero sustituye
  el plano uniforme por anclas/polígonos de superficie y conectividad explícita.
  Las conexiones autoradas unen caminos, terrazas y escaleras; estar cerca en
  pantalla o ser vecinos numéricos NO autoriza cruzar muros/desniveles.
  Radio y salida al puesto deben seguir alcanzables. Los NPC siguen pendientes.
- Dos NPC estáticos bloquean su casilla para Vera y pathfinding. Interacción E
  desde un vecino lógico muestra un mensaje breve; ni caminar contra ellos ni
  pulsar E inicia encuentros. Cada uno debe tener al menos un vecino accesible.
- Radio examinable mantiene la premisa de reservas agotadas. Los habitantes
  aportan contexto del suministro y de La Custodia, sin cambiar objetivos ni
  añadir obligaciones jugables. Repetir diálogo no altera inventario/vida.
- Salida señalizada al puesto: E vecina, fuera de combate y sin pasos/rutas
  pendientes, según base. El regreso usa aparición libre reservada. No se cobra
  PA al explorar; no se reinicia el estado de Vera ni del puesto.
- Las escaleras conectadas son recorridos jugables, con pasos e interpolación
  anclados al dibujo. Tejados, edificios, paredes, bordes del acantilado y agua
  no se vuelven transitables por aparecer en la imagen. No inferir conexiones
  de la pintura: consultar los datos del mapa. Las máscaras delanteras se
  intercalan con Vera según apoyo/profundidad, no como una tapa permanente.

Entradas: campaña/base y originales de referencia. Salidas: datos de mapa con
colisiones/objetos/NPC/salida, módulos acreditados, recursos estáticos de Vera y
aldeano y evidencias de recorrido. No modificar reglas de arena para esta fase.

## Incremento actual: esquema del escenario ilustrado

`data/hondonada.json` es el contrato versionado de autoría: 228 nodos, 234 conexiones
bidireccionales y 12 máscaras delanteras en este incremento. El PNG NO decide
colisiones. Cada nodo declara casilla lógica, centro en píxeles de la placa,
superficie y nivel. `edges` enumera conexiones bidireccionales permitidas; no se
añaden enlaces por cercanía en pantalla ni por casillas numéricamente contiguas.
`routes` define bandas de selección; `areas`, suelo seleccionable más amplio;
`layers`, siluetas de primer plano y profundidad. `game/hondonada.py` adapta ese
contrato a la rejilla y a la selección/presentación sin usar `Rect` en el dominio.

El nivel puede ser fraccionario en peldaños: es metadata, no física. La profundidad
se calcula con el pie proyectado y las siluetas. El porche oeste es un ramal sin
salida conectado al sendero inferior/escalera oeste; no hay un paso imaginario
por el techo hacia la plaza alta.

Las seis conexiones de escaleras autoradas son:

| ID | Recorrido |
| --- | --- |
| `escalera_anden_madera` | Acceso de madera al andén |
| `escalera_anden_piedra` | Acceso de piedra al andén |
| `escalera_oeste` | Escalinata del lateral izquierdo |
| `escalera_sur` | Escalinata entre terrazas del sur |
| `escalera_entrada` | Escalinata de entrada inferior |
| `escalera_terraza_este` | Acceso a la terraza del este |

Se recorre el grafo de suelo/escaleras; no cualquier píxel del escenario. Las
alturas son metadatos de presentación 2.5D, no una simulación 3D. La placa completa
se autoencuadra en el área del mundo conservando proporción, sin cámara libre ni
zoom. Las máscaras se extraen de esa misma placa una vez, con registro compartido.
Si se reemplaza la imagen o cambia su encuadre, hay que revisar anclas, áreas,
rutas y siluetas; escalar únicamente el PNG no conserva la navegación.
F3 alterna la superposición de rutas y nombres de escaleras para diagnóstico;
inicia apagada y no modifica la navegación ni el bitmap. Las líneas del overlay
no sustituyen la revisión visual de que el cuerpo de Vera coincide con el suelo.

## Resto de fase 1: tareas todavía pendientes

1. Escribir RED para carga de `hondonada`, ausencia de enemigos, dos NPC únicos y
   alcanzabilidad de radio, vecinos de NPC y salida con sus bloqueos reales.
2. Implementar datos navegables con geometrías provisionales; probar entrada y
   regreso desde el puesto antes de producir el arte del pueblo.
3. Añadir RED de interacción vecina, colisión de NPC y diálogo repetido sin
   recompensas; implementar mensajes e integración de E/UI.
4. Preparar estáticos de Vera y artesano, sus anclas/escala y registro de origen;
   comprobar que cambiar Vera no cambia recursos de guardias/jefe.
5. Producir e integrar módulos de estación, viviendas y plaza sobre las mismas
   colisiones. Revisar oclusión/legibilidad a resolución real, no solo el original.
6. Ejecutar runner compartido, revisar ida/vuelta manualmente y registrar qué
   arte sigue provisional. Actualizar evidencias sin declarar otras fases listas.

## Pruebas y checklist de aceptación

- [ ] Nueva partida aparece en `hondonada`, con 30 HP y un botiquín inicial.
- [ ] Dos aldeanos estáticos tienen casillas bloqueantes y vecinos accesibles;
  contacto y diálogo jamás activan arena ni consumen recursos.
- [ ] E desde lejos/en movimiento se rechaza sin mutación; mensajes de radio y
  aldeanos permiten comprender el objetivo sin sistemas de misión nuevos.
- [ ] No hay kits recogibles, enemigos, curación ni recompensas en este mapa.
- [ ] Ida/vuelta al puesto conserva HP/inventario/progreso; las apariciones están
  libres y la orden anterior no continúa al cambiar de escena.
- [ ] Se recorren las rutas previstas sin atravesar edificios ni subir decoración.
- [ ] Vera no flota ni se hunde al cambiar frente/espalda; se reconoce a escala
  de juego, y puede pasar por detrás de los elementos correspondientes.
- [ ] Derivados tienen rutas de proyecto y procedencia; no requieren Downloads.
- [ ] Runner y recorrido manual registrados por separado; no hay builds.
