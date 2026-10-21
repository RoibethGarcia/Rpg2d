# Ataques de Vera, guardia y jefe

Tres PNG **aportados por el usuario el 21 de octubre de 2026**. Nombres de
entrada originales, SHA-256 y rutas portables figuran en `assets/manifest.json`
(`vera_attack`, `guard_attack`, `boss_attack`). Son copias byte por byte de los
originales 2172×724, con canal alfa real (no fondo negro opaco).

- Vera: `Imagen de ChatGPT 19 oct 2026, 11_55_05.png`.
- Guardia: `Imagen de ChatGPT 19 oct 2026, 11_54_03-4.png`.
- Jefe: `Imagen de ChatGPT 19 oct 2026, 11_52_27-4.png`.

Procedencia indicada: imágenes de ChatGPT suministradas por el usuario.
Autoría y derechos de uso/redistribución **NO verificados independientemente**;
`pending_confirmation`. No se heredan CC0/CC-BY-SA de las plantillas previas.
No se generaron ni retocaron ilustraciones para esta incorporación.

## Derivación técnica reproducible

`game.animation.isolate_attack_frames` selecciona cuatro rectángulos explícitos
por hoja; NO usa celdas uniformes de 543 píxeles. Dentro de cada rectángulo, aplica
el `isolation_polygon` del manifiesto en coordenadas locales. Esto elimina partes
de otras poses que entran en su caja: especialmente botas de la pose siguiente
junto al arco del golpe de Vera y polvo del impacto del jefe. Las fronteras
siguen los huecos entre siluetas; los píxeles RGBA interiores conservan sus valores,
sin convertir negros en transparencia ni aplicar umbral global al alfa. Puede
haber residuos semitransparentes del original en esos huecos: no se promete una
limpieza artística exhaustiva.

Las anclas registran el apoyo intermedio entre las botas. Una única referencia
corporal por hoja (Vera 610 px, guardia 600 px, jefe 540 px, desde cabeza a suelas,
NO contando armas/efectos elevados) mantiene escala relativa con los estáticos.
El agachamiento propio de una pose no se estira para igualar todas las cajas.
Se escala proporcionalmente y se prepara también el reflejo horizontal y su ancla
`(ancho - ancla_x, ancla_y)` una sola vez por contexto; el punto de profundidad
sigue siendo el pie proyectado de la casilla lógica.

Duraciones editables por frame: 0.06, 0.05, 0.04 y 0.05 segundos (total **0.20 s**).
La elección conserva la cadencia enemiga existente de 0.22 s; su legibilidad debe
evaluarse con el usuario. La misma secuencia de Vera representa Llave y Potente:
no se suministraron dos ataques visuales diferenciados.

Solo ataques frontales derecha/reflejo izquierdo; no hay ciclos traseros ni de
caminar incorporados aquí. El movimiento conserva explícitamente los estáticos
frente/espalda existentes. Ningún frame aplica daño, cobra PA o termina un turno.
Al cerrar combate (incluido golpe letal), mapa, escena, terminal o reinicio se
cancelan las señales; no hay cola de efectos ni impacto tardío.
