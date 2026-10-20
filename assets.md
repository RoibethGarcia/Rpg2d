# Brief de assets — La última válvula

Documento para **adjuntar a ChatGPT y generar imágenes**, no para generar código.
Basado en el repositorio revisado el 19 de octubre de 2026. Es independiente del
[registro de recursos y licencias](docs/ASSETS.md): no lo reemplaza.

## 1. Cómo usarlo

1. Adjunta este documento a una conversación con generación de imágenes.
2. Copia el **prompt maestro** y añade una solicitud de la sección 6.
3. Empieza por Vera de frente. Revisa su diseño antes de pedir su espalda y el resto.
4. Adjunta después esa imagen aprobada como referencia visual en cada solicitud.
5. Pide **un recurso por imagen**, salvo que se solicite expresamente una lámina de
   referencia. Una lámina conceptual no es un spritesheet listo para el juego.

**Pedido inicial listo para copiar:**

> Usa este documento como brief. Aplica su prompt maestro y genera únicamente
> `vera_front`: una primera propuesta visual del sprite estático de Vera de frente
> en tres cuartos isométricos. No generes un escenario, una ficha con texto ni una
> hoja de animación. Conserva el fondo transparente y el cuerpo completo. La
> normalización final a 32×32 se hará después; no afirmes que el archivo ya cumple
> ese tamaño si no puedes comprobarlo.

Las especificaciones nuevas de vestuario, paleta y archivos que siguen son
**propuestas de producción**, no decisiones artísticas ya aprobadas. Generar una
imagen NO la integra automáticamente en Pygame.

## 2. Contexto que las imágenes deben respetar

**La última válvula** es un RPG táctico postapocalíptico, isométrico 2.5D. Una guerra
destruyó las ciudades y contaminó los ríos hace treinta años. Las comunidades
dependen de viejas plantas de purificación.

**Vera** es la técnica de bombas y generadores de **La Hondonada**, un asentamiento
en una estación ferroviaria abandonada. No es una supersoldado ni una elegida.
Debe recuperar el agua que **La Custodia**, grupo armado que controla la planta,
retiene para exigir recursos a las comunidades. Su herramienta de combate inicial
es una **llave de mantenimiento**; no diseñar un arsenal nuevo.

El primer mapa mide **24×16 casillas** y contiene tres sectores contiguos:

| Sector | Identidad visual | Prioridad narrativa |
| --- | --- | --- |
| Acceso industrial | Hormigón gastado, puesto de seguridad y mantenimiento | Entrada a una instalación deteriorada pero utilizable |
| Patio de distribución | Metal oxidado, conducciones y depósitos | El agua existe, pero los conductos comunitarios están cerrados |
| Sala de control | Paneles, maquinaria y superficies industriales frías | Recuperar el control del suministro |

Hay **una protagonista, tres guardias del mismo tipo y un jefe**, en combates
1 contra 1. El jefe entrega automáticamente una credencial al ser derrotado;
Vera gana al activar después el panel final. La esperanza viene de reparar y
restablecer el agua, no de eliminar toda la escasez del mundo.

**No agregar:** zombis, mutantes, magia, compañeros, armas nuevas, vehículos
jugables, cofres o mapas adicionales. La Hondonada no necesita un mapa propio
para este incremento. Los camiones y grandes decoraciones narrativas pueden
esperar: no son recursos obligatorios del mapa actual.

## 3. Dirección artística propuesta

Propuesta de continuidad con los sprites pequeños actuales: **pixel art industrial
sobrio**, siluetas claras, pocos detalles y desgaste localizado. No fotorealismo,
ilustración pintada ni estética de fantasía medieval. Se puede elegir otro estilo,
pero implicaría rehacer un conjunto coherente, no mezclar acabados al azar.

- **Vista del mundo:** isométrica de rombos **2:1**, cámara fija, sin perspectiva
  convergente. Ver caras superiores y dos laterales de los objetos volumétricos.
  No entregar personajes de plataforma vistos solo de perfil ni vista cenital.
- **Escala:** personas que caben en una casilla; maquinaria modular que no invada
  pasillos visualmente. No incluir bases grandes debajo de los personajes.
- **Luz propuesta:** luz suave desde arriba a la izquierda, común a todos los
  recursos; evitar brillos intensos y sombras largas que oculten otras casillas.
- **Paleta de referencia tomada de la UI actual:** fondo `#11181D`, panel
  `#1A242A`, metal `#415155`, texto claro `#E6E5D3`, agua/turquesa `#59D1CE`,
  ámbar `#EBB059`, amenaza/coral `#DF715C`. Usar grises, óxido y tierra como base;
  los acentos ayudan a leer roles, no deben teñir todo el escenario.
- **Vera, propuesta:** ropa de trabajo remendada, herramienta reconocible y un
  pequeño acento turquesa. Evitar una silueta militar pesada.
- **Custodios, propuesta:** uniforme industrial de seguridad gastado, protecciones
  sencillas y acento coral. Un único diseño reutilizable para los tres guardias.
- **Jefe, propuesta:** misma facción, hombros más anchos e insignia geométrica
  ámbar; distinguirlo también por silueta, no solo por color o tamaño.
- Sin texto incrustado, marcas de agua, logos comerciales ni HUD dibujado en los
  sprites. Los textos y las barras siguen siendo responsabilidad del juego.

## 4. Qué existe y qué conviene generar

**P0:** primer conjunto útil. **P1:** mejora posterior. **P2:** opcional, no bloquea
la entrega visual básica. Las rutas propuestas se guardarán bajo
`assets/generated/`; esa carpeta aún no existe ni se carga automáticamente.

### Recursos ya disponibles — conservar, no volver a pedir por defecto

| Recurso real | Estado comprobado | Uso de este brief |
| --- | --- | --- |
| `assets/images/human_front.gif`, `human_rear.gif` | Plantillas humanas de intellikat, 32×32, CC0; Vera/guardias/jefe se diferencian con tinte y marcadores | Referencia de escala; sustituibles cuando haya diseños aprobados |
| `assets/images/pipes.png` | Hoja de Darkmoonfire 192×512, CC BY-SA 4.0; se usa un recorte oxidado de 32×32 | Mantener como recurso existente; no pedir el pack completo otra vez |
| `assets/sounds/{click,confirm,error,back}.ogg` | Cuatro sonidos UI de ObsydianX, CC0 | Fuera de la generación de imágenes |
| Suelos, paredes, objetos y pantallas | Dibujados con geometría y texto de Pygame | Funcionan como provisionales; el arte nuevo es una mejora, no un sistema faltante |

Los packs de suelo/paredes/objetos SBS **no están integrados**. Los originales,
licencias y modificaciones de recursos descargados están en el manifiesto y en
`docs/ASSETS.md`. La fuente de packs acordada es itch.io; este brief atiende el
pedido de generar propuestas propias, sin sustituir silenciosamente esos recursos
ni cambiar su procedencia.

### Inventario de imágenes propuestas

Dimensiones **finales tras normalización**, no garantías del generador. El prefijo
de todas las rutas de la tabla es `assets/generated/`.

| Prioridad | Archivos propuestos | Cantidad | Tamaño final | Función / relación con el estado actual |
| --- | --- | --- | --- | --- |
| P0 | `characters/vera_front.png`, `vera_rear.png` | 2 | 32×32 cada uno | Diseño propio para la plantilla de Vera; estáticos |
| P0 | `characters/custodio_front.png`, `custodio_rear.png` | 2 | 32×32 | Un guardia reutilizado por `guard1`, `guard2`, `guard3` |
| P0 | `characters/jefe_front.png`, `jefe_rear.png` | 2 | 32×32 | Identidad propia del jefe; misma escala humana |
| P0 | `tiles/floor_access.png`, `floor_distribution.png`, `floor_control.png` | 3 | 48×24 | Un suelo romboidal por sector, sin obstáculos incluidos |
| P0 | `tiles/wall_block.png` | 1 | 48×48 | Sustituto de los bloques bajos actuales; no un edificio completo |
| P0 | `props/medkit.png` | 1 | 48×64 | Reutilizado para los dos botiquines recogibles |
| P0 | `props/maintenance_closed.png`, `maintenance_open.png` | 2 | 48×64 | Un mecanismo con dos estados para el acceso de mantenimiento |
| P0 | `props/distribution.png` | 1 | 48×64 | Válvula/conducción para el objeto `distribution` |
| P0 | `props/panel_locked.png`, `panel_ready.png` | 2 | 48×64 | Panel final: sin credencial / con credencial; no estados de victoria adicionales |
| P1 | `props/radio.png`, `register.png` | 2 | 48×64 | Diferenciar visualmente los dos objetos que hoy comparten `kind: note` |
| P1 | `ui/medkit.png`, `credential.png`, `wrench.png` | 3 | 32×32 | Iconos opcionales para ítem, credencial y acción; NO pickups nuevos |
| P2 | `props/pump.png`, `tank.png` | 2 | 48×64 | Decoración industrial opcional; hay ramas de dibujo, pero no instancias en el mapa actual |
| P2 | `screens/menu.png`, `victory.png`, `defeat.png` | 3 | 1280×800 | Fondos ilustrados opcionales; las pantallas actuales ya existen |

**P0 son 16 imágenes estáticas**, no 16 tipos de enemigo ni animaciones. Los
objetos actuales tienen siete instancias: radio, mantenimiento, botiquín 1,
distribución, botiquín 2, registro y panel. No hace falta una imagen por instancia.
Reutilizar diseños reduce trabajo y mantiene consistencia.

## 5. Contrato técnico: realidad frente a propuesta

### Renderer actual, verificado en código

- La ventana mide **1280×800**. La zona lógica de interacción del mundo es
  `(24,96,968,528)`; el resto contiene UI. Un fondo de pantalla no es un tile.
- `WorldRenderer` instancia `Projection(48,24, origin=(400,110))`. El rombo mide
  **48×24**; la proyección devuelve su **vértice superior**, y el pie de actores
  y objetos se sitúa en el **centro del rombo**, 12 píxeles por debajo.
- Importante: `Projection` tiene valores por defecto 64×32 y `docs/ASSETS.md`
  menciona suelo 64×32, pero **la escena actual usa explícitamente 48×24**.
  No ampliar el mapa basándose en esos valores de referencia.
- Humanos originales: **32×32**, ancla local **(16,31)**; el renderer los amplía
  a **64×64** y fija el pie en **(32,62)**. Todos los roles comparten las mismas
  dos imágenes y reciben un tinte multiplicativo por código.
- Solo se seleccionan vistas **`front` y `rear`**; el renderer actual NO aplica
  espejo horizontal ni reproduce ciclos de caminar/atacar. El desplazamiento
  suave interpola la posición de la imagen estática. No confundirlo con animación
  de frames ni prometer cuatro u ocho direcciones ya soportadas.
- El recorte de tubería usado pasa de **32×32 a 48×48**. Suelos, paredes y otros
  props no tienen hoy una carga de PNG propia. Las capas se ordenan por el pie.

### Objetivos de exportación propuestos

| Familia | Transparencia | Ancla / encaje final propuesto |
| --- | --- | --- |
| Personajes 32×32 | PNG RGBA, alfa real | Pie `(16,31)` idéntico entre vistas; cuerpo completo sin recortes, sin sombra horneada: el juego ya dibuja sombra e indicadores |
| Suelos 48×24 | Transparente fuera del rombo; interior opaco | Vértice superior `(24,0)`; extremos del contorno geométrico en `(0,12)`, `(48,12)`, `(24,24)`; bordes sin bandas de fondo |
| Bloque bajo 48×48 | PNG RGBA | Centro de apoyo `(24,36)`; base romboidal 48×24 y unos 15 px de altura visible; integrar con ajuste explícito, no con el ancla de personajes |
| Props 48×64 | PNG RGBA | Apoyo de la base `(24,60)`; dibujo contenido en su propia casilla, margen transparente superior cuando sobre; objetos pequeños NO se agrandan para llenar todo el lienzo |
| Iconos 32×32 | PNG RGBA | Símbolo centrado, margen de 2 px; sin perspectiva isométrica obligatoria por ser UI |
| Fondos 1280×800 | Opacos | Composición de pantalla, no recurso de rejilla; texto y botones se superponen en Pygame |

Las coordenadas extremas del rombo describen su geometría de encaje, no índices
de píxel válidos fuera del lienzo. Comprobar la rasterización y las juntas al
montar tiles vecinos; evitar líneas dobles y huecos de un píxel.

**No se exige que ChatGPT entregue esos tamaños exactos a la primera.** Puede
producir una imagen mayor. Solicitar bordes limpios y margen suficiente, conservar
el original y después recortar, eliminar fondo si falta alfa real, reducir con
vecino más cercano y colocar sobre el lienzo final. Revisar y retocar a mano:
una imagen grande de apariencia pixelada no se convierte automáticamente en buen
pixel art 32×32. No deformar ancho y alto de manera independiente.

## 6. Prompts copiables

Usa **maestro + solicitud concreta** en cada generación. Adjunta la referencia
visual aprobada si ya existe; mantén el mismo encuadre, luz y escala entre recursos.

### Prompt maestro

```text
Genera un recurso visual para «La última válvula», RPG táctico postapocalíptico
isométrico 2.5D. Vera, técnica de La Hondonada, busca restablecer el agua de una
planta industrial controlada por La Custodia. Mundo deteriorado pero funcional,
escasez y reparación con una nota de esperanza. Sin zombis ni fantasía.

Propuesta estética: pixel art industrial sobrio, siluetas simples y legibles a
escala pequeña, metal gastado y óxido localizado, grises/tierra con acentos
turquesa para agua/Vera, coral para amenaza y ámbar para mecanismos/autoridad.
En recursos del mundo usa vista isométrica 2:1, sin puntos de fuga, luz superior
izquierda y coherencia con la referencia aprobada. En iconos usa composición UI.

Entrega solo el recurso solicitado, completo y aislado. Para sprites, tiles e
iconos usa fondo realmente transparente: no dibujes un tablero de ajedrez ni un
fondo blanco. Sin texto, etiquetas, marcos, logos, marcas de agua ni interfaz.
No incluir suelo o escenario bajo personajes/props. No recortar herramientas ni
extremidades. No entregar una vista lateral de plataformas. Si la resolución
solicitada no está disponible, conserva el recurso a mayor tamaño y deja margen
para su normalización manual; no afirmes dimensiones o alfa no comprobados.
```

### A. Personajes — una vista por solicitud

```text
Recurso: vera_front. Un único sprite estático de cuerpo completo de Vera, técnica
de mantenimiento, vista frontal en tres cuartos isométricos, con la cara visible
y orientada hacia abajo-derecha de la pantalla. Ropa de trabajo gastada y remendada,
silueta práctica y un acento turquesa. Llave de mantenimiento compacta y legible,
sin arma de fuego añadida. Pose neutral de pie, no atacar ni caminar. Fondo
transparente y sin sombra. Debe poder simplificarse a 32×32 con el pie en (16,31).
No generar más vistas en la misma imagen.
```

Para `vera_rear`, adjunta la vista aprobada y sustituye la solicitud por:

```text
Genera vera_rear: el MISMO personaje, vestuario, herramienta, proporciones y luz
de la referencia, pero de espaldas en tres cuartos isométricos, orientada hacia
arriba-izquierda. Misma pose neutral, escala y punto de apoyo. No es otro diseño.
Una imagen aislada transparente, sin sombra; destino final 32×32, pie (16,31).
```

Repite el par sustituyendo el personaje y el nombre de archivo:

- **`custodio_front` / `custodio_rear`:** guardia humano de seguridad industrial,
  protecciones modestas, acento coral y uniforme gastado; sin nuevos tipos de arma.
  Un solo diseño para los tres custodios del mapa.
- **`jefe_front` / `jefe_rear`:** jefe de esa misma facción; hombros más anchos e
  insignia geométrica ámbar, silueta distinta dentro del mismo tamaño, no gigante.

### B. Suelos y bloque bajo

```text
Genera floor_access: UN solo tile modular de suelo de hormigón industrial gastado,
rombo isométrico 2:1. El rombo ocupa todo su rectángulo útil, sin grosor de bloque,
sin pedestal, sin pared, sin objetos, sin personajes y sin perspectiva convergente.
Destino final 48×24; exterior transparente, interior opaco. Grietas pequeñas y
textura discreta sin detalles que exijan continuación en el tile vecino. Bordes
limpios para repetir en una rejilla sin huecos; nada de sombras que salgan del tile.
```

Variantes, **en solicitudes separadas**: `floor_distribution`, suelo industrial
gris verdoso del patio; `floor_control`, suelo industrial gris azulado de control.
Conservar idéntico rombo, escala, luz y densidad de textura.

```text
Genera wall_block: UN bloque bajo industrial de hormigón y metal oxidado, vista
isométrica 2:1, tres caras visibles, sin suelo alrededor ni escenario. Su huella
debe encajar en un rombo 48×24; es un obstáculo bajo de unos 15 px de altura a
escala final, no una pared alta que tape unidades. Destino final 48×48, apoyo de
la base en (24,36), fondo transparente. Mantén la luz y materiales de los suelos.
```

### C. Objetos — usa esta plantilla y elige una fila

```text
Genera [ARCHIVO]: [DESCRIPCIÓN]. Un único objeto industrial aislado, vista
isométrica 2:1, luz y estilo de la referencia aprobada. Sin suelo, peana, texto,
personajes ni sombra exterior. Destino final PNG RGBA 48×64, apoyo (24,60).
La escala la determina el objeto respecto a una persona, no llenar todo el lienzo.
Mantener base compacta dentro de una casilla de suelo 48×24.
```

| Archivo | Descripción para sustituir |
| --- | --- |
| `medkit` | Pequeño maletín de primeros auxilios gastado, color claro y cierre legible; aproximadamente 20 px de ancho al tamaño final |
| `maintenance_closed` | Mecanismo compacto de acceso con volante de válvula y conducción corta; señal ámbar de cerrado |
| `maintenance_open` | El MISMO mecanismo aprobado, misma base, encuadre y ancla; volante cambiado de posición y señal turquesa de abierto |
| `distribution` | Conducción comunitaria con válvula cerrada, oxidada y mantenida; un mecanismo legible, no un depósito gigantesco |
| `panel_locked` | Panel compacto de control, pantalla ámbar sin letras, botones simples; unos 26 px de ancho y 36 de alto en tamaño final |
| `panel_ready` | El MISMO panel aprobado, misma carcasa, encuadre y ancla; pantalla turquesa preparada para activar con credencial |
| `radio` (P1) | Radio portátil industrial vieja con antena corta, claramente distinta de un documento |
| `register` (P1) | Carpeta o registro de distribución deteriorado, hojas sin texto legible; pequeño respecto al panel |

Los pares de estado deben partir de la imagen anterior como referencia; NO
rediseñar la carcasa. Si conservas las tuberías existentes, no es necesario generar
otra hoja: el nuevo mecanismo puede combinarse en integración sin alterar el original.

### D. UI y pantallas — solo después del conjunto jugable

```text
Genera un único icono UI de [botiquín / credencial industrial / llave de
mantenimiento], coherente con la paleta aprobada. Símbolo simple reconocible en
32×32, centrado con margen de 2 px y fondo transparente, sin letras, números,
marco de botón ni fondo de escenario. No es un objeto recogible adicional.
```

```text
Genera una ilustración de fondo para el menú de La última válvula: planta de
distribución de agua postapocalíptica, tuberías y metal gastado, atmósfera sobria
con esperanza, coherente con los materiales aprobados. Composición de pantalla
1280×800, opaca, sin texto, título, botones ni HUD. Mantén el centro de la imagen
oscuro y poco detallado para superponer título en y=325 y botones en y=412–536.
Esto es una ilustración de menú, NO un tile ni una captura ficticia del juego.
```

Para victoria: maquinaria funcionando y acento turquesa, sin sugerir que el mundo
ya está reparado. Para derrota: planta silenciosa con acento coral, sin violencia
gráfica. En ambas dejar libre la franja central de títulos y botones entre
`y=330` y `y=590`. Son fondos opcionales, no escenas/cinemáticas nuevas.

## 7. Orden de trabajo y alternativas

1. **Vera frontal:** validar estilo y legibilidad en pequeño antes de producir todo.
2. **Vera trasera, custodio y jefe:** reutilizar referencias, escala y luz.
3. **Tres suelos y bloque:** montar una muestra con tiles vecinos para revisar juntas.
4. **Botiquín, mantenimiento, distribución y panel:** revisar estados lado a lado.
5. **Radio/registro e iconos:** solo si el núcleo ya se reconoce con claridad.
6. **Fondos, maquinaria extra y animaciones:** opcionales, después de integrar.

**Alternativa de menor costo:** conservar humanos y tuberías actuales y mejorar
solo suelos y objetos. Ahorra producción, pero Vera y La Custodia siguen siendo
plantillas. **Alternativa de identidad propia:** producir el P0 completo; requiere
más revisión y adaptar el renderer para imágenes por rol y props. Este documento
no elige ni implementa automáticamente una sustitución.

**Animaciones fuera del P0:** empezar con imágenes estáticas. Si luego se aprueba
caminar, proponer primero un ciclo corto de cuatro frames por vista y personaje,
en archivos individuales, con silueta/escala/ancla constantes. Validar los frames
y ensamblar la hoja después, con rectángulos exactos. El motor tiene soporte de
spritesheets, pero el renderer de este juego no conecta esos ciclos hoy. No pedir
una hoja de ataques/daños/muerte sin acordar antes su uso e integración.

## 8. Checklist antes de incorporar archivos

### Revisión de imagen y normalización manual pendiente

- [ ] El diseño respeta Vera, La Custodia y la planta; no añade otra mecánica.
- [ ] Cada recurso se reconoce a su **tamaño final**, no solo ampliado.
- [ ] Vistas front/rear del mismo personaje mantienen ropa, herramienta y proporciones.
- [ ] Tiles y props comparten isometría 2:1, iluminación y escala; no son laterales.
- [ ] PNG de mundo/UI tiene alfa real, sin tablero dibujado, halos ni fondo blanco.
- [ ] Dimensiones, recorte, márgenes y ancla se midieron tras exportar; no basta el prompt.
- [ ] Pies estables; personajes sin sombras duplicadas; estados del mismo objeto no saltan.
- [ ] Suelos repetidos encajan sin costuras; obstáculos no ocultan objetivos o rutas.
- [ ] Iconos y botones no dependen solo del color; jefe distinto también por silueta.
- [ ] Fondos dejan leer los textos existentes y no llevan botones pintados.

### Integración posterior — NO realizada por crear este documento

- [ ] Guardar originales y exportaciones normalizadas por separado; usar nombres
  propuestos en minúsculas, sin espacios. No sobrescribir los packs originales.
- [ ] Registrar herramienta/modelo si se conoce, fecha, prompt, referencias usadas,
  autoría/procedencia declarada, cambios y condiciones de uso verificadas.
  **No atribuir CC0 ni otra licencia a un resultado generado por defecto.**
- [ ] Si se edita arte derivado de las tuberías existentes, conservar los avisos y
  condiciones documentadas para ese recurso; no tratarlo como un original sin referencias.
- [ ] Revisar `assets/manifest.json` y `docs/ASSETS.md` al integrar. Las pruebas
  actuales admiten licencias CC0/BY-SA y exigen hashes/procedencia; no falsear esos
  campos para hacer entrar recursos generados. Su contrato requiere revisión expresa.
- [ ] Adaptar carga y dibujo en una tarea de código separada: imágenes por rol,
  eliminación/revisión del tinte sobre arte coloreado, props por ID/estado,
  anclas y escalas. El cargador no descubre `assets/generated/` automáticamente;
  añadir archivos o entradas al manifiesto no sustituye el dibujo geométrico.
- [ ] Conservar lógica, ocupación y transitabilidad del mapa. La imagen no decide
  colisiones ni convierte credencial/llave en recogibles.
- [ ] Revisar manualmente en el juego solapamientos, profundidad, UI y estados.
  Ejecutar las pruebas que correspondan cuando se modifique código, **sin builds**.

**Audio:** ya existen los cuatro sonidos de UI. No pedirlos a un generador de
imágenes. Música, ambientes y sonidos nuevos serían otra tarea y no forman parte
de este inventario mínimo.

## 9. Fuentes locales para actualizar el brief

- [Historia y mecánicas](HistoriaYMecanicas.md): narrativa y alcance acordados.
- [README](README.md): estado de la primera iteración y controles.
- [Mundo](data/world.json): unidades, objetos y sectores reales.
- [Renderer](game/render.py) y [proyección](game/world.py): tamaños, anclas y capas.
- [Carga del juego](game/app.py): carga efectiva del manifiesto.
- [Manifiesto](assets/manifest.json), [procedencia](docs/ASSETS.md) y
  [pruebas de recursos](tests/test_assets.py): contratos existentes de archivos.
