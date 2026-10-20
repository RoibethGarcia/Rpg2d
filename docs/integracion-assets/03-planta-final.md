# Fase 3 — Planta final

**Estado: incremento ilustrado implementado el 20/10/2026; aceptación manual y
arena lateral del plan original pendientes.** [Índice](README.md) ·
[Contrato obligatorio: base compartida](00-base-compartida.md) ·
[Anterior: puesto](02-puesto-de-control.md) · [Siguiente: cierre](04-animaciones-y-cierre.md).

## Incremento implementado a pedido del usuario

La petición de hacer `planta.png` explorable reutiliza el combate **in situ** del
puesto, no implementa la arena lateral pendiente de fase 0. `data/planta.json`
declara 72 nodos y 76 aristas en la rejilla lógica 24×16, cinco escaleras y seis
capas delanteras. Los niveles visuales están conectados exclusivamente por
aristas explícitas; no se implementa física 3D ni se infieren pasos del bitmap.
Esto reemplaza para este incremento la propuesta inferior de un solo plano.

Tres guardias (`guard3/4/5`, 16 HP/3 daño), jefe (48 HP/4 daño), dos kits únicos
(`kit2/3`), distribución, registro y válvula final (`panel`) están integrados.
La entrada está dentro del portón cerrado. El exterior inferior, agua y tejados
siguen siendo decoración; no se atraviesan para entrar. Regreso al puesto desde
el vecino reservado `(9,8)`, sin restaurar vida ni recursos.

La válvula se activa desde `(21,13)`, vecino conectado de `(22,14)`, solo con la
credencial del jefe y sin combate, movimiento o ruta pendiente. Matar al jefe
vuelve a exploración. El original se conserva, la placa limpia y su prompt están
en `assets/provenance/planta-layered.md`. Prueba directa: `main.py --map planta`.

Pruebas ejecutadas y capturas: [VALIDACION](../VALIDACION.md). El recorrido
integrado ahora reproduce el presupuesto inferior de cinco guardias+jefe y acaba
con **2 HP/0 kits**, sin modificar HP, posiciones ni recursos desde el test.
No equivale a aceptación humana de dificultad, animaciones ni arena lateral.

## Objetivo y dependencias

Completar el recorrido jugable con **tres guardias y un jefe**, dos botiquines,
distribución, registro y panel final. Depende de fases 0–2 aceptadas. Reutilizar
arena, guardias, transiciones y UI; no crear otro combate ni una copia de Vera.
La credencial y la victoria pertenecen a campaña, no al renderer del mapa.

## Assets disponibles y faltantes

En el [inventario del índice](README.md): `planta-referencia`, `jefe-frente` y
`jefe-espalda`; guardias y Vera estáticos vienen de fases anteriores. Las hojas
del jefe son material futuro de fase 4, no animaciones ya cargables.

Producir suelo, maquinaria, tuberías, depósitos, control y pasarelas decorativas
como módulos con huella y pie definidos. Faltan las piezas separadas, capas de
ocultación y representación de los mecanismos/panel coherente con el estilo.
La ilustración sirve de referencia: no aporta alturas navegables ni una malla de
caminos. Mantener un plano y bloquear escaleras/plataformas decorativas.
Preparar al jefe sin deformar su arma por encajarlo en un cuadrado universal.

## Contratos y recorrido

- Mapa `planta`: 24×16 y un plano, regreso al puesto permitido. Conectar aparición,
  distribución, registro, dos kits, área del jefe y vecino accesible al panel.
- Exactamente tres guardias y un jefe con IDs únicos en campaña. Guardias usan
  16 HP/3 daño; jefe 48 HP/4 daño. No aumentar estadísticas por el tamaño visual.
  Rutas/puntos de estancia nunca ocupan apariciones reservadas.
- Los guardias pueden evitarse cuando la ruta lo permite; no condicionar la
  credencial ni el panel a derrotar a todos. Los seis encuentros de la campaña
  deben ser abordables para el recorrido automatizado de aceptación.
- Dos botiquines distintos, recogibles una vez y accesibles antes del jefe sin
  exigir su derrota. No sumar otros suministros o curas gratuitas para ajustar
  informalmente el balance.
- Distribución revela depósitos llenos y conductos comunitarios cerrados;
  registro explica el uso del protocolo por La Custodia. Interacciones vecinas,
  fuera de combate, sin daño, costes ni recompensas nuevos.
- Al derrotar al jefe conceder automáticamente **una** credencial a campaña.
  Derrota y credencial persisten al volver a puesto/pueblo y regresar.
- Vencer al jefe devuelve a exploración, **no** produce victoria de campaña.
  Solo E desde un vecino del panel, fuera de combate/sin movimiento pendiente y
  con credencial, activa el suministro. Rechazos no mutan recursos/progreso.
  Usar el desenlace acordado; después bloquear gameplay y permitir volver al menú.

Entradas: campaña, recursos y presentación de fases anteriores. Salidas: planta,
seis encuentros totales posibles, credencial/panel y recorrido completo probado.
Sin guardado en disco, compañeros, huida ni nuevos finales.

## Tareas ordenadas — TDD futuro

1. RED de datos y conectividad: tres guardias+jefe, dos kits distintos, mecanismos,
   panel y rutas accesibles. Implementar primero geometrías provisionales.
2. Probar ida/vuelta, recogida única y congelación de patrullas; integrar distribución
   y registro sin duplicar la interacción compartida.
3. RED de recompensa única del jefe y victoria condicionada por vecino/credencial;
   integrar retorno al mapa, panel y terminales de aplicación.
4. Preparar estáticos del jefe y módulos de planta con registro de derivados;
   revisar arma, escala relativa, oclusión y lectura del panel.
5. Añadir recorrido completo automatizado por comandos públicos (ver abajo), sin
   mutar HP, teletransportar unidades ni conceder recursos desde el test.
6. Ejecutar regresiones y jugar el recorrido manualmente. Registrar dificultad,
   legibilidad y desvíos; no alterar números sin actualizar contratos/pruebas.

## Prueba de balance y recorrido completo

Presupuesto aprobado: 30 HP, un kit inicial + uno en puesto + dos en planta,
cinco guardias y un jefe. La simulación matemática previa es **evidencia aislada,
no validación integrada**. Estrategia candidata para reproducir en la línea 0…11:

| Tramo | Secuencia candidata | Resultado matemático de referencia |
| --- | --- | --- |
| Cada guardia | Turnos 1–2: potente y retirada de tres pasos hacia la izquierda; turno 3: básica para rematar | Tras guardias 1…5: Vera 24, 26, 28, 30, 30 HP |
| Curación de guardias | En el tercer turno de guardias 2…5, usar un kit **antes** de la básica final; ya deben haberse recogido los necesarios | Cuatro kits usados; no puede curar tras salir de combate |
| Jefe, entrando con 30 HP | T1: potente + retirada de tres; T2–T4: dos potentes por turno, el último mata | Vera después de cada tramo: 26, 14, 2, 2 HP; cero kits |

El test integrado debe recorrer las salidas, recoger los tres kits a tiempo,
resolver contacto, actuar/terminar turnos y esperar actualizaciones a través de
las interfaces públicas. Puede usar rutas calculadas con datos del mapa, no
asignaciones directas a posición/HP/credencial. Debe verificar el retorno después
de cada combate y pulsar interacción ante el panel. Si no reproduce la referencia,
investigar orden de IA, alcances, rutas o consumo; no falsificar el resultado ni
dar la campaña por equilibrada. Incluso si coincide, 2 HP demuestra posibilidad,
**no comodidad ni validación con jugadores**.

## Pruebas y checklist de aceptación

- [ ] Planta tiene tres guardias+jefe, dos kits únicos y mecanismos alcanzables.
- [ ] Kits se obtienen antes del jefe y su recogida respeta el presupuesto total
  de suministros: un inicial más tres recogidos únicos en toda la campaña.
- [ ] Victoria de cada encuentro conserva consumos/HP; el jefe concede credencial
  una vez y no reaparece al viajar.
- [ ] Sin credencial, en arena, lejos del panel o en movimiento no hay victoria.
- [ ] Jefe derrotado por sí solo no gana; E vecina con credencial activa desenlace.
- [ ] Victoria/derrota bloquean gameplay y permiten menú; nueva partida limpia
  los tres mapas, credencial, recogidos y todos los estados temporales.
- [ ] Recorrido automatizado vence a cinco guardias y jefe mediante comandos reales,
  recoge suministros y activa panel; registrar HP/kits finales reales.
- [ ] Revisión humana de dificultad y presentación separada de la simulación y de
  dummy; assets acreditados, runner documentado y ningún build.
