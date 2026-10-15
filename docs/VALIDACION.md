# Validación — primera iteración

Fecha: **15 de octubre de 2026**. Resultado automatizado final de esta revisión: **70 pruebas correctas, salida 0**. No equivale a certificar todos los entregables ni a afirmar que una persona completó la partida.

## Pruebas ejecutadas

Desde la raíz del proyecto, con el intérprete del entorno que contiene Pygame:

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m unittest discover -s tests -v
```

Ejecución final: `Ran 70 tests in 1.019s`, `OK`, exit 0. Usar un Python global sin Pygame no es este comando; un fallo de importación por intérprete equivocado no constituye RED válido ni éxito.

| Área | Archivo de pruebas | Cantidad | Evidencia |
|---|---|---:|---|
| Motor | `test_engine.py` | 11 | Segundos, sobrante de animación, API sonora, botones, QUIT y limpieza ante excepción; recursos relativos al JSON. |
| Mundo | `test_world.py` | 3 | Límites, obstáculos, proyección/inversa, negativos, cámara y BFS estable. |
| Modelo | `test_model.py` | 17 | Reservas, contacto, PA, alcance, curación, turnos, derrota, credencial, interacción y patrullas. |
| Contenido y partida completa | `test_playthrough.py` | 3 | Balance y datos independientes; patrullas válidas; partida real con mapa y recursos aprobados. |
| QA independiente de dominio | `test_regressions.py` | 12 | Contacto a mitad del tick, bloqueo/reserva, atomicidad, terminales, reset anidado, tiempos y selección desplazada. |
| UI | `test_ui.py` | 11 | Herencia, menú, nueva partida, clic UI aislado, transiciones, carga única, audio/canal e interpolación sin mover casilla lógica. |
| Integración independiente | `test_integration.py` | 9 | Otro directorio, import sin efectos, equivalencia clic/WASD, botones y turnos, derrota, panel/victoria y reinicio. |
| Recursos | `test_assets.py` | 4 | Manifiesto, procedencia, hashes, licencias, dimensiones, transparencia, frames y decodificación OGG. |
| **Total** | | **70** | Sin builds ni compilación de validación. |

La integración UI de victoria usa una **fixture de jefe** para aislar transiciones; no debe confundirse con recorrer todo el mapa mediante la UI. El recorrido completo usa comandos públicos del dominio, sin teletransportar, alterar vida, inventario ni balance: vence a los tres guardias y al jefe de **48 de vida**, obtiene credencial y activa panel. Termina con **2 de vida y 0 botiquines**. Prueba existencia de una estrategia con maniobra, no dificultad adecuada para principiantes.

## Hallazgo independiente y corrección RED → GREEN

**Impacto alto, corregido:** contacto con enemigo al completar un paso podía cerrar la aplicación con `KeyError: 'patrol'`.

- Repro: Vera `(2,2)` ordena ruta hasta el guardia quieto `(5,2)`. Otra patrulla parte de `(7,5)` hacia `(7,4)` con pausa de 0.14 s. Dos llamadas públicas `state.update(.14)` sincronizan el segundo paso de Vera con el de la patrulla.
- **RED real:** `test_contact_mid_tick_cancels_other_motion_without_stale_commit_or_crash` falló en `game/model.py`, `_tick`, al ejecutar `del self.motions[uid]`. No fue error de importación, dependencia ni sintaxis.
- Causa: el contacto cancela todos los movimientos, pero `_tick` continuaba consumiendo una instantánea anterior del diccionario; podía confirmar posición y cobrar PA de un paso ya cancelado antes de borrar una clave inexistente.
- Corrección realizada por el propietario de dominio: comprobar identidad del movimiento todavía activo antes de avanzar tiempo, confirmar posición o cobrar costo. La revisión QA no editó archivos de implementación ajenos.
- **GREEN:** la regresión conserva Vera `(4,2)`, rival `(5,2)`, patrulla `(7,5)`, vida intacta, 6 PA, sin rutas ni movimientos pendientes; suite independiente y suite completa aprobadas.

Otros 11 casos independientes ampliaron cobertura del comportamiento existente; no se presentan como nuevas correcciones inventadas. Durante la integración también se avisó una referencia temporal a `state` en el render del menú; el propietario la corrigió antes de la suite final y los tests de dibujo del menú pasan.

## Inspección estática y arranque real

- Leídos mundo, modelo, carga de contenido, datos y pruebas; contrastados con los valores y contratos aprobados. Actualizados diseño, instalación, controles, estado por fases y procedencias sin modificar los acuerdos futuros de grupo.
- `bash -n scripts/grabar_video.sh`: salida 0. Consultada la ayuda local de `/usr/sbin/screencapture`: confirma `-v`, `-V<seconds>` e `-i`. **No se ejecutó captura de pantalla/video** en esta revisión; solo se preparó el script opt-in.
- El propietario del motor realizó un **smoke GUI nativo autorizado**, sin SDL dummy: driver `cocoa`, mixer `(44100,-16,2)`, nueva partida y llamada al sonido de confirmación, cierre QUIT tras 2.2 s; exit 0. Captura exclusiva de la superficie del juego en `artifacts/smoke-real.png`, no del escritorio.
- El coordinador inspeccionó capturas de menú, partida, combate y smoke real. Comprobó legibilidad general de esas capturas; no es una prueba exhaustiva de profundidad o interacción.
- Capturas de victoria/derrota generadas como fixtures de render no prueban que una persona haya ganado/perdido manualmente una partida completa.

## No ejecutado / pendiente

- **Partida manual completa** con teclado/ratón, calidad de maniobra, accesibilidad, profundidad en todos los solapamientos y ajuste de dificultad.
- **Percepción sonora real:** cargar mixer y llamar a reproducción no demuestra que una persona oyera ni evaluara el resultado. SDL dummy solo comprueba contratos/decodificación.
- **Video de 15–40 segundos:** todavía no existe `artifacts/demo.mov`. Script de 25 s y guion preparados; seleccionar únicamente ventana del juego requiere usuario y permisos de macOS. No instala encoder, no usa micrófono ni publica archivos.
- Permiso de **redistribución del motor docente**, no declarado en notebook; publicar repositorio requiere además autorización expresa. GitLab, commit y publicación no realizados.
- Tests en Windows/Linux y otros tamaños de pantalla no ejecutados. No afirmar compatibilidad validada fuera del entorno macOS ARM64/Python 3.13 comprobado.
- Arte final de personajes/maquinaria y packs SBS pendientes; geometría provisional explícita y archivos reales acreditados en [ASSETS](ASSETS.md).

No se ejecutaron builds, `py_compile`, `compileall`, empaquetado ni compilación de dependencias. Compañeros y combate múltiple no forman parte de la aceptación inicial.
