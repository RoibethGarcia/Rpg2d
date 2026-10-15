# Contratos de subagentes

Estas carpetas describen responsabilidades para delegaciones puntuales.
**No registran ni ejecutan agentes automáticamente**, ni son nuevas skills.

Todos los roles leen `Codex/rules.md`; su contrato local solo delimita la tarea.
El coordinador entrega contexto, decisiones acordadas, evidencias y archivos que
puede modificar. Nunca delegar una decisión del usuario como si estuviera aprobada.

| Rol | Responsabilidad | Cuándo usarlo |
| --- | --- | --- |
| [planificacion](planificacion/AGENTS.md) | Alcance, diseño y trazabilidad | Antes de un incremento o ante una ambigüedad |
| [gameplay](gameplay/AGENTS.md) | Dominio, combate y turnos | Al implementar reglas acordadas |
| [mundo-isometrico](mundo-isometrico/AGENTS.md) | Rejilla, proyección y representación | Al implementar mapa y selección |
| [qa](qa/AGENTS.md) | Pruebas y revisión independiente | Al definir aceptación y verificar incrementos |

## Protocolo de coordinación

1. Definir objetivo, alcance, entradas, criterios de aceptación y archivos propios.
2. Inyectar las reglas compactas relevantes y el contexto previo verificado.
3. No asignar el mismo archivo simultáneamente a varios agentes.
4. Acordar interfaces compartidas antes de que dos roles las implementen.
5. Si surge una duda que requiere al usuario, comunicarla al coordinador y detener
   el trabajo que dependa de ella; no elegir respuestas por cuenta propia.
6. Entregar: estado, resumen, archivos, decisiones, validaciones reales, riesgos
   y próximo paso. Distinguir recomendaciones de trabajo implementado.
7. Guardar hallazgos y decisiones importantes en Engram antes de retornar.

El coordinador integra y verifica. QA no puede certificar sus propias suposiciones
como requisitos ni declarar ejecutada una prueba solo por inspeccionar el código.
No todos los roles necesitan activarse para cada cambio.
