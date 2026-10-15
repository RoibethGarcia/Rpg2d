# Implementación por fases — La última válvula

Estado comprobado el **15 de octubre de 2026**. Distinguir núcleo implementado de entrega audiovisual/publicación: disponer de código y pruebas no certifica esos entregables.

## Estado por fases

| Fase | Implementado y verificable | Pendiente o límite |
|---|---|---|
| 1. Base y motor del curso | Fuente original clase 8 recuperada; adaptación explícita de `dt` a segundos; `Scene`, `GameObject`, `GameLoop`, botones y gestor de recursos; `.venv` Python 3.13 + Pygame 2.6.1; menú y salida. | El notebook no declara licencia: confirmar redistribución antes de publicar. |
| 2. Mundo isométrico | Rejilla, obstáculos, ocupación, proyección/inversa 2:1, selección `floor`, suelo y profundidad por pie/capa/desempate estable. Humanos y tuberías reales acreditados; maquinaria provisional. | Packs SBS no integrados por HTTP 429; composición y legibilidad requieren inspección manual. |
| 3. Exploración | WASD/clic comparten reglas; BFS de cuatro vecinos; reservas y confirmación al completar; cancelación y bloqueos sin recálculo; patrullas; contacto sin ataque gratuito y pausa de otras patrullas. | Revisión humana de controles y claridad del contacto pendiente. |
| 4. Combate | 6 PA, alternancia explícita, acciones atómicas, alcance vecino, ataques, curación limitada solo en combate, IA determinista, HUD de vida/PA/turno/costos/rechazos. | Dificultad y feedback deben probarse con jugadores. El combate no finaliza solo por llegar a 0 PA. |
| 5. Primera iteración | Mapa 24×16, tres guardias y jefe de 48; tres sectores; dos suministros recogibles; mantenimiento, mecanismos y notas; credencial automática, E adyacente al panel; victoria/derrota, menú y nueva partida. Recorrido completo automatizado sin teletransportes ni alterar balance. | Video todavía NO capturado; revisión manual visual/sonora/jugable pendiente; publicación NO autorizada ni realizada. |

## Arquitectura y contratos

- **Motor reutilizable:** `Scene.handle_events/update(dt)/draw`, `GameObject`, `GameLoop` y utilidades de recursos; origen, celdas y adaptaciones en [MOTOR](MOTOR.md). `LastValveGame` hereda de `GameLoop`, las escenas de `Scene` y `WorldActor` de `GameObject`.
- **Dominio:** `GameState`, `Unit`, `Motion`, `ActionResult(ok,message)` y `GridMap`. No importan Pygame ni dependen de `Rect`. Coordenada lógica única `(col,row)`; proyección/inversa fuera de las reglas. Un `GameState.new()` carga datos independientes.
- **Presentación:** escenas menú/partida/victoria/derrota, render y HUD. La UI captura sus clics antes del mapa; solo transmite comandos. Un único bucle principal convierte `Clock.tick()/1000`; ninguna escena crea otro.
- **Datos y recursos:** mapa en `data/world.json`; manifiesto con paths relativos a raíz, dimensiones/anclas, procedencia, licencias y hashes. Carga una vez, no por frame. Canal reservado de sonidos UI evita superponer efectos. No se ocultan errores de carga; modo sin audio es explícito para pruebas.
- **Tiempo:** pasos de 0.14 s, decisiones enemigas separadas por 0.22 s; simulación en ticks de 0.02 s que conserva sobrante. PA/vida se modifican por acciones y pasos confirmados, no por número de frames. Render actual con tiles 48×24, humanos escalados a 64×64 y apoyo ajustado.

## Reglas resueltas

Vera 30 de vida; guardias 16; jefe **48**. Daños 4/7 de Vera y 3/4 rivales. Cada turno 6 PA; paso 1, básico 2, potente 3, botiquín 2, ataque enemigo 2. Uno inicial y dos botiquines recogibles, curan hasta 8 sin exceder máximo. Sin curación en exploración ni consumo con vida completa.

La orden de movimiento reserva destino y confirma posición/costo al completar cada paso. WASD/Escape cancelan lo pendiente después del paso actual; WASD prepara la nueva dirección. Un nuevo obstáculo detiene sin buscar ruta alternativa. Clic demasiado lejano ejecuta solo el presupuesto disponible y descarta el resto. Cero PA no cede el turno automáticamente.

Solo el rival contactado combate; ambos conservan casillas, otras patrullas paran y se exige nueva orden de Vera. Rival quieto es contacto; reserva o rival en tránsito son bloqueos. Enemigo derrotado no actúa ni ocupa; se vuelve a exploración sin restaurar vida o inventario. La credencial no es todavía victoria: hay que activar con E el panel desde una casilla vecina fuera de combate.

## Evidencia y entrega

- **70 pruebas aprobadas** en la ejecución completa registrada en [VALIDACION](VALIDACION.md), incluyendo una partida real que acaba con 2 de vida y sin botiquines. Esta estrategia combina potente y retirada; no demuestra balance cómodo.
- QA independiente encontró y reprodujo un fallo al cancelar movimientos al contactar en medio de un tick: corrección del propietario y regresión RED→GREEN documentadas en VALIDACION.
- Arte y SFX reales seleccionados en [ASSETS](ASSETS.md). No presentar geometría propia como packs SBS ni sprites de plantilla como diseños finales.
- Arranque GUI real autorizado comprobado en macOS con driver Cocoa, mixer iniciado y cierre QUIT. El coordinador inspeccionó capturas de menú/partida/combate y arranque real; eso no certifica percepción sonora ni partida manual completa.
- Script nativo macOS opt-in de captura preparado; sintaxis validada, captura no ejecutada. El video de 15–40 s y sonido real siguen pendientes.
- No se ejecutaron builds, `py_compile`, `compileall`, empaquetado, commits ni publicación. Compañeros, combates múltiples, armas y cofres adicionales quedan fuera de esta iteración; reglas futuras conservadas en [Historia y mecánicas](../HistoriaYMecanicas.md).
