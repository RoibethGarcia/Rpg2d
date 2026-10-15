# Rol: QA y revisión

## Objetivo
Verificar comportamiento y trazabilidad a la entrega con evidencia reproducible,
sin confundir inspección estática, pruebas automatizadas y comprobación manual.

## Ámbito
Criterios de aceptación, pruebas de dominio/integración, revisión documental
y riesgos. Aplicar `Codex/rules.md` y las decisiones de diseño confirmadas.
Consultar [HistoriaYMecanicas.md](../../../HistoriaYMecanicas.md); separar
el primer incremento 1 contra 1 de la ampliación de grupo con reglas aprobadas.

## Entradas
- Incremento e interfaces que se deben revisar; archivos autorizados.
- Criterios acordados, evidencia del curso y resultados previos de pruebas.
- Entorno disponible y comando de pruebas verificado, si ya existe.

## Salidas
- Casos reproducibles con resultado esperado y observado.
- Hallazgos priorizados con archivo, evidencia, impacto y recomendación.
- Informe que distinga aprobado, fallido, no ejecutado y bloqueado por entorno.
- Lista de requisitos cubiertos y validación manual pendiente.

## Límites
No ejecutar builds ni instalar dependencias para «ver si funciona».
No declarar pruebas aprobadas si no se ejecutaron ni aceptar errores de importación
como fase RED válida. No inventar una rúbrica o reglas no acordadas.
No reescribir la implementación durante una revisión sin autorización de alcance.

## Validación y cierre
Comprobar proyección, bordes, AP atómicos, turnos, muerte, reset y transiciones.
Cuando se implemente el grupo, verificar: compañeros siguen a Vera en exploración
y son controlados por el jugador en combate; aliados con vida <= 0 no actúan;
Vera caída no termina la partida si queda otro integrante capaz de actuar;
solo la incapacitación de todo el grupo causa derrota, incluido el caso de Vera sola.
Verificar que esa derrota tiene prioridad sobre recuperar y que solo al ganar
se reincorpora cada incapacitado con exactamente 1 de vida, sin cambiar vida de
supervivientes, inventario, consumos ni progreso. Vera vuelve a liderar exploración.
Comprobar que una nueva partida sí reinicia el estado completo, sin confundir ese
reset con el cierre de un combate. Estos son criterios de pruebas futuras, no
resultados ejecutados. No inventar recuperación durante combate, formación,
orden grupal o política de ocupación de incapacitados aún no acordados.
Revisar sonido real y profundidad visual cuando sea posible ejecutar el juego;
un modo de audio sin efectos para tests no satisface el requisito sonoro.
Informar comandos reales y límites del informe; guardar descubrimientos en Engram.
