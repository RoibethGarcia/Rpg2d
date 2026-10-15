# Dominio y mundo: evidencia TDD

Fecha: 15 de octubre de 2026. Python 3.13.15; `unittest` estándar.
No se ejecutaron builds, empaquetado, `py_compile` ni `compileall`.

## Contratos implementados

- `game.world`: `Cell=(col,row)`, BFS con desempate W/D/S/A y costo uniforme,
  `GridMap` con límites/transitabilidad; `Projection` con ancla superior,
  centro lógico `col+.5,row+.5` e inversa con `floor` (incluidos negativos).
- `GameState.new()` lee `data/world.json` desde una ruta absoluta basada en el
  módulo. Cada llamada obtiene un estado mutable independiente.
- Los comandos devuelven `ActionResult(ok,message)`; su conversión booleana es
  `ok`. La UI consulta `state.message`. `update(dt)` recibe segundos.
- Una `Motion` reserva destino; la casilla lógica y el costo se confirman al
  finalizar el paso. Las reservas y actores en tránsito bloquean sin contacto.
- `preview_path` no incluye origen y puede incluir destino hostil estacionario
  en exploración. En combate se ejecuta solo el prefijo pagable y se descarta
  el resto. Escape cancela después del paso actual; WASD puede sustituir los
  pasos pendientes por una dirección después de ese paso.
- Comenzar combate cancela rutas y movimientos pendientes (las unidades quedan
  en su última casilla confirmada), pausa patrullas y requiere una nueva orden.
- IA determinista por acciones: acercamiento BFS, ataque vecino por 2 PA y fin
  cuando no puede actuar. Pasos de simulación de 0.02 s conservan la secuencia
  al fraccionar `dt`; las reglas no dependen de los FPS.
- Botiquines: SOLO turno propio en combate, 2 PA y hasta 8 HP, sin consumir nada
  si la acción es inválida. No se añadió curación gratuita en exploración.
- Interacción E: recoger una vez, abrir mantenimiento, examinar mecanismos y
  notas, activar panel desde distancia Manhattan exactamente 1 con credencial,
  únicamente en exploración y sin movimiento pendiente de Vera.

## Ciclos RED → GREEN observados

| Ciclo | Comando ejecutado | RED real | GREEN |
|---|---|---|---|
| Rejilla/proyección/BFS | `python3.13 -m unittest discover -s tests -p test_world.py -v` | 3 FAIL: transitabilidad falsa, vecinos vacíos y origen incorrecto en esqueletos importables | 3 OK |
| Exploración | `python3.13 -m unittest discover -s tests -p test_model.py -v` | 4 FAIL: comandos devolvían rechazo, ruta sin avance y contacto ausente | 5 OK |
| Combate/interacciones | mismo comando | 6 FAIL: ataques, curación, turnos, credencial y recogida aún rechazados | 12 OK |
| Contenido | `python3.13 -m unittest discover -s tests -p test_playthrough.py -v` | 2 FAIL: faltaban cuatro enemigos y la compuerta inicialmente bloqueada | 2 OK |
| Rechazo de curación en exploración | comando de modelo | 1 FAIL: devolvía éxito y consumía botiquín fuera de combate | 13 OK |
| Recorrido real | comando de recorrido | 1 FAIL: interacción bloqueada por animaciones de patrullas distantes | 3 OK |
| Transición durante snapshot de animaciones | comando de modelo | ERROR de comportamiento `KeyError: other` al cancelar las demás motions; no era importación/sintaxis | 17 OK |

El refactor dejó ayudantes compartidos para validación, ocupación y resultados;
se repitieron las pruebas correspondientes después de las correcciones.

## Recorrido completo reproducible

`test_complete_real_map_three_guards_boss_credential_and_panel` crea la partida
real, camina por sus casillas y solo invoca comandos públicos y `update`.
NO modifica vida, posiciones, inventario, enemigos, patrullas ni balance.

1. Accede al anillo del guardia 1 y lo derrota.
2. Recoge el primer botiquín y abre el acceso de mantenimiento con E.
3. Supera los guardias 2 y 3; usa un botiquín durante cada combate.
4. Recoge el segundo botiquín antes de la sala de control.
5. Derrota al jefe de 48 HP y usa el último botiquín durante ese combate.
6. Recibe la credencial, camina junto al panel y activa E: victoria.
7. Comprueba nueva partida limpia e independiente.

Estrategia de prueba: golpe potente y retirada de tres pasos; en el turno de
curación, retirada de cuatro. La maquinaria central impide atajos y permite
recorrer los anillos. Resultado comprobado: **Vera con 2 HP, cero botiquines y
los cuatro enemigos derrotados**. Demuestra viabilidad, NO balance satisfactorio
para cualquier estrategia ni una revisión de facilidad/legibilidad.

Comandos finales de dominio, sin necesitar pygame:

```sh
python3.13 -m unittest tests.test_world tests.test_model tests.test_playthrough -v
```

Resultado: 23 pruebas OK. La regresión independiente de QA añade otra prueba
lógica. Ejecutar la suite gráfica completa requiere el Python del entorno con
pygame instalado; el Python global no tiene esa dependencia.

## Pendiente de revisión humana

Profundidad visual, anclajes reales de assets, legibilidad, controles con teclado
físico y sonido real NO se certifican mediante estas pruebas de dominio.
