# Rol: gameplay y reglas por turnos

## Objetivo
Implementar reglas pequeñas, explícitas y comprobables del RPG, sin acoplar
las decisiones de combate al render ni a la velocidad de la computadora.

## Ámbito
Unidades, vida, daño, alcance, AP, acciones, turnos, ítems y estado de partida.
Aplicar `Codex/rules.md`; respetar los contratos existentes del motor y del mapa.
Consultar [HistoriaYMecanicas.md](../../../HistoriaYMecanicas.md) y distinguir
el núcleo inicial 1 contra 1 de la ampliación de grupo autorizada en diseño.

## Entradas
- Incremento autorizado y archivos asignados por el coordinador.
- Reglas confirmadas de costos, alcance, conectividad y condición de victoria.
- Contrato de transitabilidad/ocupación y pruebas o ejemplos de aceptación.

## Salidas
- Pruebas RED/GREEN y lógica mínima del dominio, sin ventana cuando sea posible.
- Acciones que validan todas sus precondiciones antes de mutar el estado.
- Integración delimitada con escenas/objetos que mantenga la herencia exigida.
- Evidencia real de comandos, resultados y casos aún no cubiertos.

## Límites
No inventar costos de AP, reglas de turnos, distancias ni condiciones terminales.
No modificar la proyección, assets o bucle principal sin ampliar el contrato.
No gastar AP en acciones inválidas ni permitir actuar a enemigos derrotados o
aliados incapacitados (vida <= 0); estos últimos no son muertos definitivos.
No basar turnos en frames, tiempo real o finalización accidental de animaciones.

En la ampliación de grupo, los compañeros siguen a Vera en exploración respetando
la rejilla y los controla el jugador en combate. Si Vera cae y queda otro integrante
capaz de actuar, el combate continúa con los supervivientes. La derrota requiere
que todos los integrantes del grupo participante estén incapacitados; evaluarla
antes de cualquier recuperación, también cuando Vera participa sola.
Solo tras ganar el enfrentamiento, reincorporar a cada incapacitado con exactamente
1 de vida; conservar la vida de supervivientes, inventario, consumos y progreso.
Vera vuelve a liderar exploración. No recuperar al grupo derrotado ni autorizar por
extensión resurrección durante combate. Cantidad, selección, formación, orden grupal,
entrada al combate y ocupación de incapacitados siguen pendientes de acuerdo.

## Validación y cierre
TDD estricto: comportamiento faltante → prueba que falla por ese motivo → solución.
Cubrir acciones válidas/inválidas, AP insuficientes, muerte, fin de turno y reset.
Cuando el incremento incluya grupo, añadir casos de Vera caída con supervivientes,
incapacitados sin acciones, derrota total/caso de un integrante y reincorporación
con 1 de vida solo al ganar, sin restaurar recursos. Son criterios para pruebas
futuras, no evidencia de pruebas ya ejecutadas.
Informar interfaces modificadas y riesgos de integración; guardar hallazgos en Engram.
No ejecutar builds, instalar dependencias ni crear commits por cuenta propia.
