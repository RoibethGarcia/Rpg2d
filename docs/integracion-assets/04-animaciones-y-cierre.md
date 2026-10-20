# Fase 4 — Animaciones y cierre

**Estado: pendiente de implementación.** [Índice](README.md) ·
[Contrato obligatorio: base compartida](00-base-compartida.md) ·
[Anterior: planta](03-planta-final.md).

## Objetivo y dependencias

Añadir caminar y ataques a la campaña estática completa, conservando las reglas,
el progreso y el recorrido de aceptación. Depende de fases 0–3 aceptadas y de los
recursos por personaje/contexto de la base. Primero cerrar juego estático, después
animarlo: la presentación no debe convertirse en una segunda simulación.

## Assets disponibles y faltantes

En el [inventario del índice](README.md) están las seis hojas: caminar/atacar de
Vera, guardia y jefe, además de sus estáticos frente/espalda. La hoja original de
Vera de caminar y ataque mide 2172×724; usar los originales, no las imágenes
redimensionadas de la conversación. No deducir una grilla uniforme de cuatro
celdas: cortes cada 543 px pueden atravesar figuras. Registrar rectángulos
explícitos medidos para cada pose, incluyendo arma y efecto cuando corresponda.

Faltan recortes validados, limpieza de residuos de alfa/halos, registro homogéneo
de pies y tiempos de reproducción comprobados. No se aportaron ciclos traseros
completos válidos: **conservar la espalda estática** en exploración donde falten.
No inventar caminar trasero espejando una cara frontal. El aldeano permanece
estático; no crear una animación artificial por oscilación si no fue solicitada.

## Contratos de animación y recursos

- Cada frame define rectángulo dentro de la hoja, ancla de pie y duración en
  segundos; escala corporal consistente entre reposo, caminar y ataque. Validar
  límites y evitar recortes de armas/efectos o contaminación por la pose contigua.
- Separar fuente/derivado: conservar original, registrar recortes, limpieza,
  escalado y reflejo; documentar origen/licencia sin heredar la de plantillas.
- El movimiento visual sigue el progreso del paso lógico; no cobra PA ni modifica
  casillas desde callbacks de frames. La animación usa `dt` en segundos y no FPS.
- El ataque reproduce una secuencia **una sola vez** y vuelve a reposo. El comando
  lógico válido aplica daño/coste exactamente una vez; los frames solo representan
  ese resultado. No aplicar de nuevo al llegar al «frame de impacto».
- Mientras se presenta la acción, no aceptar una repetición accidental mantenida
  que ejecute otro comando; las acciones siguientes necesitan una nueva orden
  válida. Terminar una animación no cambia turno ni concede PA.
- En arena orientar participantes hacia su oponente; reflejar horizontalmente el
  recurso cuando corresponda y transformar también ancla/offset. La lógica mantiene
  sus índices tácticos; reflejar un sprite no invierte comandos ni posiciones.
- Cambiar mapa/escena, cerrar encuentro, victoria, derrota y nueva partida cancelan
  animaciones/eventos pendientes. Nunca dejar daño diferido después de un reset.
- No cargar/copiar/reescalar todas las hojas por frame; preparar y cachear recursos
  al cargarlos. Errores obligatorios visibles, sin excepciones amplias silenciosas.

Entradas: recorrido estático y originales de hojas. Salidas: derivados/metadatos,
presentación animada, evidencias y documentación final actualizada. No ampliar a
varios enemigos, alturas jugables, grupo, defensa, huida ni guardado en disco.

## Tareas ordenadas — TDD futuro

1. Registrar las hojas originales y medir todos los rectángulos; crear tests RED
   de límites, alfa, duración positiva y anclas. Preparar derivados sin asumir
   cuatro celdas iguales ni quitar colores negros del personaje.
2. Probar selección de reposo/caminar y fallback explícito de espalda; integrar
   caminar de Vera, después guardias y jefe, sobre pasos ya comprobados.
3. RED de ataque one-shot, avance con distintos `dt` y ausencia de daño/coste
   duplicados; añadir feedback de ataques sin cambiar reglas de la arena.
4. Probar reflejo/ancla y cancelación de estados al cambiar contexto; integrar
   orientaciones y revisar pies/armas/efectos a escala world y arena.
5. Reejecutar regresiones completas, incluido recorrido de cinco guardias y jefe.
   Revisar manualmente los tres mapas, clics, sonido, legibilidad y profundidad.
6. Actualizar diseño, README, créditos/manifiesto e informe de validación reales
   para tres mapas/arena; conservar diferencia entre pruebas, inspección y revisión
   manual. Actualizar este índice con evidencias de fases aceptadas.
7. Preparar guion de video de 15–40 segundos conforme a la consigna cuando el
   recorrido funcione; grabar/publicar solo con autorización correspondiente.

## Pruebas y checklist de aceptación

- [ ] Todos los frames están dentro de su original y no cortan cuerpos/armas;
  transparencia sin rectángulos de fondo ni restos de otras poses.
- [ ] Pies y escala corporal estables entre estados/orientaciones y ambos contextos;
  el reflejo no desplaza visualmente a la unidad fuera de su casilla.
- [ ] Espalda estática explícita donde no exista ciclo; no se afirma cobertura de
  direcciones/acciones que no tenga material válido.
- [ ] Ataque se reproduce una vez; un comando causa un único daño/coste, incluso
  con `dt` grande o varios frames; no depende del framerate.
- [ ] Animación de caminar no adelanta lógica ni cobra dos veces el paso.
- [ ] Ninguna ruta, ataque o efecto sobrevive a transiciones, terminales o reinicio.
- [ ] HP, PA y botiquines del recorrido completo coinciden con sus comandos,
  no con callbacks visuales; los tests estáticos siguen siendo aplicables.
- [ ] Recursos cargados desde proyecto, con procedencia, cambios y derechos
  registrados; sin atribuir a los nuevos PNG las licencias de otros packs.
- [ ] Revisión manual y pruebas documentadas por separado, sin builds; sonido
  real no se declara probado mediante SDL dummy.
- [ ] Diseño/créditos/instrucciones reflejan solo lo implementado. No se declara
  permiso docente ni publicación del repositorio por haber completado el arte.
