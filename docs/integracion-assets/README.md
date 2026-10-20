# Integración jugable de assets — La última válvula

## Estado y alcance de esta entrega

**Plan del 19 de octubre de 2026; fase 0 parcialmente implementada (tareas 1–2).** Estos
seis documentos permiten ejecutar las fases por separado. Después de la entrega
documental se incorporó un **reemplazo parcial independiente**: los seis PNG
estáticos de Vera, guardias y jefe ya se cargan y dibujan desde el proyecto.
Ese reemplazo no implementó campaña. El incremento posterior ya añade los tres
mapas provisionales persistentes y viajes reversibles; NPC, arena y animaciones
siguen pendientes. Los incrementos visuales posteriores integraron Hondonada,
puesto y planta sobre sus ilustraciones por capas, con caminos y escaleras
autorados. La planta ya incluye tres guardias, jefe y válvula final. La fase 0
NO está completa: arena lateral, NPC y animaciones continúan pendientes.

La historia sigue siendo restablecer el agua de La Hondonada. El cambio autorizado
es de alcance y presentación, no un requisito nuevo de la consigna ni una solución
proporcionada por el curso. Consultar [diseño vigente](../../HistoriaYMecanicas.md),
[reglas](../../Codex/rules.md), [evidencia del curso](../../Codex/references/curso-y-consigna.md),
[ejecución actual](../../README.md) y [créditos actuales](../ASSETS.md).

| Aspecto | Implementado actualmente, inspeccionado | Objetivo aprobado, pendiente |
| --- | --- | --- |
| Mundo | Tres ilustraciones con grafos autorados sobre rejilla lógica 24×16; Hondonada ↔ puesto ↔ planta, E vecino y mantenimiento para avanzar | Aceptación manual de dificultad y presentación |
| Habitantes/enemigos | Sin aldeanos; dos guardias en puesto, tres y jefe en planta | Dos aldeanos y animaciones |
| Combate | 1 contra 1 en la rejilla de exploración | 1 contra 1 en arena lateral de 12 casillas |
| Estado | Campaña con una Vera/inventario/credencial y colección de `MapState`; viajes no restauran recursos | Encuentro separado de exploración |
| Arte humano | Seis PNG exclusivos frente/espalda de Vera, guardias y jefe; sin tintes, escala proporcional y anclas por vista | NPC, animaciones y configuración adicional por contexto |
| Nuevos PNG | Seis originales estáticos copiados sin edición y cargados desde el proyecto; procedencia y hashes registrados | Ampliar módulos básicos ya integrados, aldeano, interfaz y animaciones; confirmar redistribución |

Las diferencias con los documentos de la primera iteración son intencionales.
Actualizar esos documentos **cuando se implemente** cada cambio, sin describir
funcionalidades futuras como terminadas.

## Orden, dependencias y forma de trabajar

| Fase | Documento | Dependencias | Estado de implementación |
| --- | --- | --- | --- |
| 0 | [Base compartida](00-base-compartida.md) | Código actual y este acuerdo | Parcial: tareas 1–2 automatizadas; 3–6 pendientes |
| 1 | [La Hondonada](01-la-hondonada.md) | Fase 0 aceptada | Escenario por capas y escaleras; NPC/diálogos y aceptación completa pendientes |
| 2 | [Puesto de control](02-puesto-de-control.md) | Fases 0–1 aceptadas | Ilustración, dos patrullas y combate in situ implementados; arena lateral pendiente |
| 3 | [Planta final](03-planta-final.md) | Fases 0–2 aceptadas | Ilustración, tres guardias+jefe, kits, credencial/válvula y recorrido automatizado implementados; aceptación manual pendiente |
| 4 | [Animaciones y cierre](04-animaciones-y-cierre.md) | Recorrido estático de fases 0–3 aceptado | Pendiente |

Ejecutar **0 → 1 → 2 → 3 → 4**. La fase 0 entrega los tres destinos provisionales
y la arena mínima, para que cada escenario posterior sea un incremento comprobable.
Las fases 1–3 añaden contenido y arte estático, no copias de los sistemas comunes.
La fase 4 sustituye presentaciones estáticas por animaciones, sin cambiar reglas.

Para implementar una fase, proporcionar al ejecutor este índice, la base y el
documento de esa fase. Primero inspeccionar el estado real y las evidencias de las
dependencias; después TDD estricto (RED de comportamiento → GREEN → REFACTOR),
revisión manual y actualización de evidencias. Registrar comando, resultado y
límites antes de marcar una casilla; «pendiente», «automatizado» y «manual» son
estados distintos. No cambiar las reglas comunes desde un escenario aislado.

## Inventario de originales compartidos

Ubicación de consulta: `/Users/roibethgarcia/Downloads/`. Son los nombres exactos
aportados por el usuario, **no rutas de carga del juego**. Los seis originales
estáticos ya tienen copias en `assets/images/characters/`; las tres referencias de escenario ya están copiadas en `assets/reference/scenarios/` y respaldan un atlas generado; los restantes siguen pendientes. Conservar originales y registrar los derivados al incorporarlos.
El fondo negro de la previsualización no debe convertirse automáticamente en
colorkey: validar el alfa de cada archivo y preservar detalles oscuros.

| ID de referencia | Archivo original | Uso previsto | Fase |
| --- | --- | --- | --- |
| vera-frente | `Mecánica superviviente con llave inglesa.png` | Vera estática, frente | 1 |
| vera-espalda | `Imagen de ChatGPT 19 oct 2026, 11_54_50.png` | Vera estática, espalda | 1 |
| vera-caminar | `Imagen de ChatGPT 19 oct 2026, 11_54_59.png` | Hoja de caminar | 4 |
| vera-atacar | `Imagen de ChatGPT 19 oct 2026, 11_55_05.png` | Hoja de ataque | 4 |
| aldeano-taza | `Artesano del Yermo con Taza.png` | Dos NPC estáticos reutilizados | 1 |
| combate-referencia | `Batalla pixel art en la fábrica industrial.png` | Dirección artística de fondo e interfaz | 2 |
| jefe-frente | `Imagen de ChatGPT 19 oct 2026, 11_52_25-1.png` | Jefe estático, frente | 3 |
| jefe-espalda | `Imagen de ChatGPT 19 oct 2026, 11_52_26-2.png` | Jefe estático, espalda | 3 |
| jefe-caminar | `Imagen de ChatGPT 19 oct 2026, 11_52_26-3.png` | Hoja de caminar | 4 |
| jefe-atacar | `Imagen de ChatGPT 19 oct 2026, 11_52_27-4.png` | Hoja de ataque | 4 |
| guardia-frente | `Imagen de ChatGPT 19 oct 2026, 11_54_02-1.png` | Guardia estático, frente | 2–3 |
| guardia-espalda | `Imagen de ChatGPT 19 oct 2026, 11_54_02-2.png` | Guardia estático, espalda | 2–3 |
| guardia-caminar | `Imagen de ChatGPT 19 oct 2026, 11_54_03-3.png` | Hoja de caminar | 4 |
| guardia-atacar | `Imagen de ChatGPT 19 oct 2026, 11_54_03-4.png` | Hoja de ataque | 4 |
| pueblo-referencia | `Imagen de ChatGPT 19 oct 2026, 11_54_08.png` | Referencia exacta de placa limpia, capas y escaleras transitables | 1 |
| puesto-referencia | `Imagen de ChatGPT 19 oct 2026, 11_54_23.png` | Control y patrullas | 2 |
| planta-referencia | `Imagen de ChatGPT 19 oct 2026, 11_54_30.png` | Instalación y control final | 3 |

**Integración visual básica disponible:** atlas con 16 módulos, suelos/muros por mapa y decoración sobre huellas bloqueadas; recorte, escala y profundidad por pie. No completa las fases ni layouts finales.

**Faltan piezas de producción:** ampliar edificios y props para reconstruir los layouts finales; fondo limpio de arena; marcos, iconos y retratos de UI; ciclos
traseros válidos. Las ilustraciones de escenario son referencias para reconstruir
módulos, no tilemaps ni fondos listos con colisiones. Sus personajes dibujados no
pueden permanecer como supuestos actores del juego. El mockup con varios rivales
no aprueba combate grupal, defensa, huida ni nuevas estadísticas.

## Validación del incremento y límites

Runner ejecutado durante el primer incremento de campaña, desde la raíz que
contiene el [README](../../README.md); resultados en [VALIDACION](../VALIDACION.md):

```sh
PYTHONDONTWRITEBYTECODE=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python -m unittest discover -s tests -v
```

No ejecutar builds, empaquetado, `py_compile` ni `compileall`. No instalar
dependencias automáticamente. Dummy comprueba integración técnica, no sonido real,
legibilidad, profundidad ni calidad del arte. Cada fase requiere revisión manual
cuando exista su implementación. El incremento actual tiene pruebas automatizadas de dominio/UI dummy y recorrido
completo del contenido provisional; no se realizó partida manual ni revisión sonora.

Balance de partida objetivo: Vera 30 HP, un botiquín inicial y tres recogibles
(uno en puesto, dos en planta; ninguno en pueblo). Existe una simulación matemática
aislada de cinco guardias y jefe que termina con 2 HP y cero botiquines. **No es
una partida de esta campaña ni una prueba integrada**: reproducirla mediante los
comandos públicos en fase 3, y revisar después la experiencia humana.

La procedencia de los PNG nuevos debe registrarse sin inventar CC0 ni heredar
licencias de los packs existentes. No publicar por completar estas fases: sigue
pendiente confirmar permiso de redistribución del motor docente y autorización
expresa para publicar, según [MOTOR](../MOTOR.md).

### Incremento visual de escenarios (19 de octubre de 2026)

Atlas real integrado en Hondonada, puesto y planta, sin pegar ilustraciones completas.
Se conserva la navegación anterior: no se implementaron NPC, arena, nuevos guardias,
animaciones ni desniveles. Por tanto las fases 0–4 **no se marcan completas**.
Procedencia, prompt, referencias y límites en [ASSETS](../ASSETS.md).

### Cambio autorizado: Hondonada por capas y escaleras

La petición posterior del usuario sustituye el límite de un plano y escaleras
decorativas **solo para Hondonada**. Se conserva el original; `hondonada_plate`
registra una placa limpia editada con IA, fondo negro opaco explícito, prompt
y SHA-256. La navegación no depende de píxeles ni de un colorkey global: usa
superficies y conexiones de escaleras autoradas. Las máscaras de primer plano
se preparan en memoria a partir de la misma placa. Véase el
[contrato actualizado](01-la-hondonada.md). Esto NO completa aldeanos, diálogos,
arena, animaciones ni las demás tareas pendientes de fases 0–4.
