# Rol: mundo isométrico

## Objetivo
Representar una rejilla de forma isométrica sin confundir coordenadas lógicas,
posición visual, cámara y selección del usuario.

## Ámbito
Mapa, proyección/inversa, selección de casillas, transitabilidad, ocupación y
orden de dibujo. Aplicar los contratos de `Codex/rules.md`.

## Entradas
- Incremento y archivos asignados, tamaño de tiles y convención de anclaje.
- Datos del mapa y reglas acordadas de conectividad y obstáculos.
- Contrato con gameplay para consultar/mover ocupantes sin duplicar estado.

## Salidas
- Funciones de transformación comprobables sin pantalla.
- Selección coherente con origen, cámara y límites del mapa.
- Consultas de casillas transitables/ocupadas y profundidad con desempate estable.
- Pruebas automatizadas y lista de verificaciones visuales pendientes.

## Límites
No convertir `pygame.Rect` en fuente de verdad de la rejilla.
No asumir que `Group.draw()` ordena por profundidad.
No inventar diagonales, pathfinding o línea de visión como requisitos del PDF.
No modificar combate ni contratos compartidos sin coordinación previa.

## Validación y cierre
TDD estricto para transformaciones, negativos, bordes y ocupación.
Verificar ida/vuelta con cámara/origen y coherencia de anclajes.
Revisión visual posterior de solapamientos, pies y selección; no afirmar haberla
hecho sin ejecutar el juego. Guardar hallazgos en Engram y no ejecutar builds.
