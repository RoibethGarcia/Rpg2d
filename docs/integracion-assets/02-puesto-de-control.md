# Fase 2 — Puesto de control

**Estado: implementación PARCIAL del plan; exploración y combate in situ funcionales.**
[Índice](README.md) · [Base compartida](00-base-compartida.md) ·
[Hondonada](01-la-hondonada.md) · [Planta](03-planta-final.md).

## Incremento implementado

La imagen elegida `assets/reference/scenarios/puesto.png` tiene un derivado limpio
`assets/images/environments/puesto-clean.png` (1448×1086). Se retiraron los soldados
pintados: los dos guardias visibles son unidades reales, con HP, ocupación y
patrullas; no hay detección por focos. Procedencia y redistribución pendiente en
[ASSETS](../ASSETS.md). No se presenta el bitmap como tilemap automático.

`data/puesto.json` declara 42 nodos dentro del contrato lógico 24×16, 46 aristas,
bandas seleccionables y cuatro máscaras delanteras. El acceso inferior asciende
por los tramos reales de escalera; la carretera ofrece dos corredores conectados
que rodean el camión. El grafo excluye tejados, roca, depósitos, vías superiores,
agua y el resto del decorado. No todo el suelo dibujado es explorable.

Se reutilizan `AuthoredLayout`/`AuthoredProjection` y `LayeredEnvironmentArt` de
Hondonada: carga y preparación de capas una vez, profundidad por pie, interpolación
de centros visuales, selección solo sobre rutas, sin inferir conexiones por
cercanía de píxeles. El alcance uno del combate consulta la arista real, no la
resta de IDs de nodos. Los costes y daño existentes NO cambian.

## Probar

```sh
.venv/bin/python -B main.py --map puesto
```

Inicia una campaña fresca con Vera a 30 HP, un botiquín y guardias a 16 HP.
El arranque normal sigue en menú y «Comenzar»/«Nueva partida» vuelve a Hondonada.
También se puede viajar desde la salida sur de Hondonada, con E desde su vecino.

1. Desde la entrada inferior, subir por la escalera al botiquín al lado del
   aterrizaje de carretera; E lo recoge una sola vez, sin curación automática.
2. Observar los dos corredores y las patrullas. Clic sobre un guardia se aproxima
   e inicia contacto lógico, no un ataque gratuito. WASD usa vecinos autorados;
   F3 muestra rutas diagnósticas, apagadas por defecto.
3. En combate, usar llave/potente/botiquín y Espacio para ceder turno. La ruta
   distingue pasos disponibles y resto ámbar; las acciones inválidas no gastan PA.
4. Mantenimiento está junto al portón noreste. E desde su nodo o vecino abre
   permanentemente el paso a planta; el marcador de salida exige E desde vecino.
   No requiere eliminar guardias ni conseguir credencial. El corredor alternativo
   permite llegar a suministros/mantenimiento sin matar obligatoriamente.

## Contratos persistentes

- `guard1` y `guard2` están en puesto; `guard3` y `boss` en planta: no se añadió
  dificultad ni se duplicaron enemigos. Sus rutas excluyen las apariciones.
- Solo patrulla el mapa activo. Ante ocupación/reserva esperan. Contacto desde
  Vera o desde una patrulla inicia un único duelo contra esa unidad real.
- El resto del mundo se congela durante el duelo. Al ganar persiste HP cero del
  rival; viajar no revive enemigos ni restaura vida, AP, inventario o consumibles.
- `kit1` se recoge una vez y no reaparece al volver; `maintenance` mantiene abierta
  la salida. El retorno a Hondonada nunca exige combatir.
- El motor conserva su único loop, escenas `Scene` y actores `GameObject`.

## Evidencia y límites

Pruebas en `tests/test_puesto.py`, `tests/test_startup.py` y regresiones de campaña:
centros seleccionables, aristas sin cruce de máscaras, escalera real sin atajo por
pared, rutas a objetivos evitando ocupación de guardias, patrullas/contactos de
ambos rivales, persistencia, interpolación y oclusión del camión. El playthrough de
comandos públicos gana campaña completa con 2 HP y cero botiquines sin adulterar
recursos; el fixture legacy también sigue pasando. Comandos y resultado global en
[VALIDACION](../VALIDACION.md).

Se inspeccionaron capturas SDL dummy de rutas, peldaños, actores y ocultación;
esto NO certifica sonido real, legibilidad nativa ni una partida manual completa.
La arena lateral de 12 posiciones del plan sigue **PENDIENTE**: el código previo
no tenía `EncounterState` ni arena funcional, por lo que este incremento conserva
el combate in situ, su UI real y sus reglas. También quedan pendientes animaciones,
exploración de vías superiores/decorado y permisos de redistribución. No se declara
completada la fase 2 ni las dependencias completas de la fase 0.
