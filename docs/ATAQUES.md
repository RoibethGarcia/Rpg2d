# Primer incremento de animaciones de ataque — 21/10/2026

## Alcance real

Vera, guardias y jefe animan sus ataques en el combate **1 contra 1 in situ**
existente. Se incorporaron los tres PNG originales aportados, no imágenes nuevas.
Llave y Potente comparten la secuencia de Vera: solo se aportó una. No hay arena,
ciclos de caminar ni ataques traseros. Frente/espalda estáticos siguen siendo el
fallback explícito del movimiento. Esto NO completa la fase 4 ni valida las
fases anteriores del plan por escenarios.

## Contrato

- `GameState.attack` y `_enemy_action` validan/aplican reglas existentes y registran
  `AttackAction` inmutable: atacante, casilla objetivo e instante. `last_attacks`
  contiene solo el último hecho por actor, no una cola de comandos pendientes.
- El reloj `elapsed` incluye el residuo del tick de 0.02 s. Los comandos del jugador
  usan su instante continuo; la IA usa el instante del subpaso, no el residuo que
  durante un `dt` grande puede contener tiempo futuro.
- `AttackClip` consulta edad y duraciones sin callbacks. Preparación 0.06 s,
  golpe 0.05 s, impacto 0.04 s y recuperación 0.05 s: **0.20 s** en metadatos.
  Una consulta pasada esa duración devuelve reposo, nunca reinicia la secuencia.
  Con un `dt` grande pueden omitirse frames ya vencidos: NO se encolan ataques
  viejos ni se reproduce daño tardío. Consultar o dibujar no cambia el dominio.
- Se conserva la cadencia IA de **0.22 s**, sus PA y su daño. El turno cambia al
  agotarse PA aunque el clip siga representando la acción. El compromiso es una
  animación breve; ampliar duración exigiría evaluar solapamientos/ritmo con el
  usuario, no ralentizar reglas en un callback visual.
- La escena rechaza nuevas órdenes tácticas durante el feedback; no se aceptan
  repeticiones accidentales. Requiere una nueva orden después de volver a reposo.
  Menú, cierre global, diagnóstico y captura de UI conservan sus rutas normales.
- Cierre de combate, mapa/contexto, escena, terminal, nueva partida y QUIT limpian
  señales. Un **golpe letal cierra inmediatamente el combate y cancela su clip**;
  no se promete animar letales completos en este incremento.
- Se recortan rects medidos con polígonos de aislamiento, se escala por cuerpo y
  se precachean ambas orientaciones por contexto. La orientación depende de la
  posición **proyectada** del rival, no del orden o resta de IDs lógicos del grafo.
  Reflejar transforma también el ancla. El pie proyectado conserva profundidad.

[Procedencia, máscaras, escalas y derechos pendientes](../assets/provenance/combat-attacks.md).
No se hacen lecturas, máscaras ni reescalados de hojas durante la reproducción.

## Validación ejecutada

Runner real: Python 3.13.15 del `.venv`, Pygame 2.6.1. No hubo builds,
compilación explícita, instalaciones ni commits.

RED de comportamiento observado, antes de cada implementación:

1. `tests.test_attack_animation`: 2 fallos, faltaban hojas registradas y señal de
   acción válida; luego GREEN de 2.
2. Mismo módulo: 1 fallo entre 3, el ataque seguía mostrando idle; luego GREEN de 3.
3. Mismo módulo: 3 fallos entre 6, repetición UI, menú sin cleanup y timestamp del
   jugador anclado al tick anterior; luego GREEN de 6.
4. Caso dirigido `...test_tactical_input_is_blocked_not_menu_or_global_quit`:
   1 fallo por señal superviviente al QUIT, luego GREEN de 1.
5. `...AttackWorldContextTests`: 1 fallo entre 3, edad -1e-16 ocultaba primer frame;
   luego GREEN del módulo completo.

```sh
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m unittest tests.test_attack_animation -q
```

**24 pruebas, 6.741 s, OK** (salida 0). Cubren metadatos/alfa/negros, rechazo,
ambos ataques de Vera, guardia/jefe, one-shot, límites exactos, `dt` cero/grande/
fraccionado, PA y HP únicos, orientación/ancla, escalas en mapas autorados,
fallback trasero, caché sin I/O, contexto/reset/mapa/menú/terminal/QUIT y letales.
La suite global previa a la ampliación pasó **183 pruebas, 31.066 s, OK**;
la verificación global FINAL independiente pasó **201 pruebas, 35.620 s, OK**,
con el comando completo y evidencias en `VALIDACION.md`.

## Inspección visual y límites

Capturas SDL dummy inspeccionadas; NO equivalen a partida manual nativa ni
sonido audible. La secuencia completa, ritmo, legibilidad, profundidad en todos
los rincones y comodidad de input necesitan evaluación humana.

- [12 poses sobre checker](../artifacts/attacks/poses.png): inspección de armas,
  efectos, anclas y ausencia de contaminación visible por figuras vecinas.
- [Reposo, cuatro frames y reflejos, a escala real por mapa/rol](../artifacts/attacks/qa-native-scale-poses.png).
- [Vera ataca en puesto](../artifacts/attacks/qa-scene-puesto.png) ·
  [guardia en puesto](../artifacts/attacks/qa-enemy-puesto.png).
- [Vera ataca en planta](../artifacts/attacks/qa-scene-planta.png) ·
  [jefe en planta](../artifacts/attacks/qa-enemy-planta.png).

Las capturas `qa-*` son del agente de QA independiente, con fixtures que sitúan
Vera en un vecino real del enemigo: **no son un playthrough por comandos**.
Los artefactos locales están ignorados por Git. No se afirma distribución
pública autorizada de los PNG suministrados.
