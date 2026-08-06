# El asistente de IA — diseño

> Decisiones tomadas el 2026-08-06. Cada una tiene su porqué: si alguna se
> revierte, que sea sabiendo qué se está descartando.

## La tesis del producto

**Orca ya hace el razonamiento. Solo que nunca lo muestra.**

Verificado en el código el 2026-08-06. Cuando apretás auto-orientar, `Orient.cpp`
puntúa cada orientación candidata por área en voladizo, casco inferior, contorno,
área de caras de ángulo bajo, volumen y relación de estabilidad. Elige la mejor,
rota el objeto… y descarta todo el razonamiento.

Lo único que `OrientJob.cpp` le muestra al usuario es una barra de progreso que
dice "Orienting" y dos mensajes de error sobre placas bloqueadas. **Cero
explicación de por qué eligió esa orientación y no otra.**

De ahí salen las dos mitades del producto:

| | |
|---|---|
| **Hacer visible lo que ya existe** | Los números que Orca calcula y descarta: por qué esta orientación, cuánto soporte ahorra, qué tan estable queda. No hay que calcular nada nuevo. |
| **Agregar lo que Orca no toca** | Recomendaciones de paredes, relleno y tipo de soporte, **en función del uso de la pieza** — que es lo único que Orca no puede saber. Acá entra la IA. |

La primera mitad es sorprendentemente barata: el dato ya está, falta la UX. La
segunda es donde está el diferencial real.

## El riesgo que define todo

Un asistente que diga *"esta pieza tiene voladizos, considerá usar soportes"* es
**peor que no tener nada**: es obvio, es genérico, y le enseña al usuario que la
función no sirve. Después no la abre más.

La diferencia entre útil y adorno es una sola pregunta:

> **¿Dice algo específico de *esta* pieza que el usuario no podía ver solo?**

Si no, mejor callarse.

Y hay que tenerlo presente: **Orca ya tiene auto-orientación, soportes
automáticos y un tooltip explicativo en cada parámetro.** Repetir eso no aporta
nada. Lo que Orca no puede hacer es conectar la geometría con **para qué es la
pieza**: un soporte de estante que va a cargar 5 kg y una figura decorativa
pueden ser la misma malla y necesitar decisiones opuestas.

Esa es toda nuestra ventaja. Se construye alrededor de ella.

---

## Decisiones

### 1. Habla solo cuando tiene algo específico

Al cargar la pieza corre el análisis geométrico en silencio. Si encontró algo
concreto y accionable, aparece **una línea**. Si la pieza está bien, **silencio
total**.

```
┌──────────────────────────────────────┐
│ Voladizo de 68° en la cara inferior. │
│ Rotando 90° en X desaparece la       │
│ necesidad de soportes.               │
│          [ Aplicar ]  [ ¿Por qué? ]  │
└──────────────────────────────────────┘
```

**Por qué:** un asistente que salta solo todo el tiempo se odia y se desactiva;
uno que espera a que lo llamen se olvida. Hablar solo cuando hay algo que decir
es lo que construye la confianza de que, cuando habla, vale la pena leerlo.

**Costo aceptado:** un usuario nuevo puede no enterarse de que existe. Se
compensa con la primera aparición, que va a ser útil.

### 2. Propone, el usuario aplica

Muestra exactamente qué cambiaría —parámetro, valor viejo, valor nuevo— y aplica
solo si el usuario lo pide. **Nunca toca un parámetro por su cuenta.**

```
┌─ Propuesta ──────────────────────┐
│ Altura de capa   0.20 → 0.12 mm  │
│ Soportes         no   → sí (árbol)│
│ Relleno          15%  → 40%      │
│                                  │
│ Motivo: detalle fino y va a       │
│ recibir carga.                    │
│   [ Aplicar los 3 ]  [ Elegir ]  │
└──────────────────────────────────┘
```

**Por qué:** en un laminador la confianza es todo. Si alguien descubre que le
cambiaron un parámetro sin avisar, no lo usa nunca más. Además, **ver el cambio
es parte de aprender**: el diff enseña más que el resultado.

### 3. El loop de fotos vive en "Mis impresiones"

Una sección propia con el historial: qué se imprimió, con qué parámetros, cómo
salió. Ahí se suben las fotos.

```
┌─ Mis impresiones ───────────────┐
│ 05/08  soporte_estante   ✓ bien │
│ 04/08  engranaje_v2      ⚠ hilos│
│ 02/08  caja_bisagra      ✓ bien │
│                                 │
│ Patrón detectado:               │
│ tus piezas con PETG salen con   │
│ hilos — probá subir retracción  │
└─────────────────────────────────┘
```

**Por qué:** funciona sin impresora conectada (mucha gente lamina en la
computadora e imprime desde SD), y el historial es lo que permite detectar
**patrones propios del usuario**, que es de donde sale el aprendizaje real. Un
consejo basado en "las últimas tres veces que usaste PETG te pasó esto" vale
infinitamente más que uno genérico.

**Descartado:** ponerlo en la pestaña Dispositivo. El momento es oportuno pero
solo sirve con la impresora conectada, y se pierde el historial.

### 4. Sin API key funciona igual, con menos profundidad

| Sin key — gratis, offline, instantáneo | Con key — ~US$0,03 por consulta |
|---|---|
| Voladizos y ángulos críticos | "¿Para qué es esta pieza?" → consejo según uso |
| Espesor mínimo de pared | El porqué explicado y conversable |
| Orientaciones candidatas y volumen de soporte | Análisis de fotos del resultado |
| Centro de masa y estabilidad | Detección de patrones en el historial |

**Por qué:** el análisis geométrico es **matemática pura sobre la malla** —
instantáneo, sin costo, sin internet. Cubre buena parte del valor. Desperdiciarlo
detrás de un muro de configuración sería regalar la primera impresión del
producto.

### 5. Un proveedor afinado + adaptador compatible con OpenAI

Un proveedor principal con los prompts realmente afinados, más un adaptador que
habla el protocolo de OpenAI — con lo que el usuario puede apuntar a OpenRouter
(una key, todos los modelos), a Ollama local, o a cualquier servicio compatible.

**Por qué no multi-proveedor nativo:** los prompts se afinan por modelo. Con
tres adaptadores nativos, o afinamos tres veces o dos dan una experiencia peor —
y el usuario juzga *nuestro producto*, no al modelo. Además la calidad de
**análisis de fotos** varía mucho entre modelos, y ese es justamente el
diferencial.

**Dato importante que hay que comunicar bien:** ninguna suscripción de
consumidor (Claude Pro, ChatGPT Plus, Gemini Advanced) da acceso a la API. Son
facturaciones separadas en las tres empresas. "Conectá tu IA" **no** significa
"usá lo que ya pagás" — siempre hay que cargar crédito de API aparte. La
documentación tiene que decirlo sin vueltas, o generamos frustración.

### 6. Deduce el uso de la pieza y pide confirmación

En vez de preguntar en frío, arriesga una lectura y deja corregirla:

```
┌────────────────────────────────────┐
│ Parece una pieza técnica: tiene    │
│ agujeros pasantes y paredes de     │
│ 3mm. Recomiendo 40% de relleno.    │
│     [ Correcto ]  [ No, es otra ]  │
└────────────────────────────────────┘
```

**La deducción es geométrica, no de IA.** Agujeros pasantes, espesor de pared,
relación superficie/volumen, roscas, simetría — todo se mide localmente. Así la
lectura es gratis, instantánea y funciona sin API key, que es coherente con la
decisión 4. La IA entra **después de la confirmación**, para el consejo
profundo.

Sin esto, la app estaría gastando una consulta de IA que nadie pidió, cada vez
que se carga una pieza.

**Regla contra el riesgo de errarle:** si la geometría es ambigua, **no
arriesga** — pregunta en vez de afirmar. Un asistente que se equivoca con
seguridad pierde autoridad mucho más rápido de lo que la gana uno que acierta.
Es preferible callarse.

### 7. comoimprimo se integra más adelante

El asistente explica por su cuenta. Los enlaces al manual se suman cuando tenga
contenido cubriendo los temas que el asistente toca — enlazar a páginas que no
existen es peor que no enlazar.

**No perder de vista que esto quedó pendiente:** una vez que el asistente ya
explica bien solo, cuesta más volver a meter la integración. Conviene revisarlo
cuando comoimprimo crezca.

### 8. Un solo aviso de privacidad, antes de la primera foto

Las fotos van a un tercero: el proveedor de IA. Antes de la primera subida
—y solo esa vez— se explica sin vueltas:

```
┌─ Antes de tu primera foto ───────────┐
│ Para analizar la impresión, la foto  │
│ se envía a <proveedor>, que la       │
│ procesa y devuelve el diagnóstico.   │
│                                      │
│ No la guardamos en ningún servidor   │
│ nuestro: el historial queda en tu    │
│ computadora.                         │
│    [ Entendido ]   [ Mejor no ]      │
└──────────────────────────────────────┘
```

**Por qué una sola vez:** avisar en cada subida se vuelve ruido — a la tercera
vez nadie lo lee, y termina siendo transparencia decorativa que además mete
fricción en el flujo más importante del producto. Dejarlo solo en la
documentación es peor: mucha gente sube una foto sin haber leído nada, y
enterarse después se siente como un engaño.

La afirmación de que no guardamos nada en servidores nuestros **tiene que
seguir siendo cierta**. Si algún día aparece un backend que toque las fotos,
este texto cambia primero.

### 9. Responde en el idioma de la interfaz

Si Orca está en español responde en español; en inglés, inglés. Se le indica al
modelo y listo, sin trabajo extra.

**Por qué no fijarlo en español:** el asistente es justamente la parte que nos
diferencia, y atarlo a un idioma la vuelve inservible fuera de LATAM. Orca está
traducido a decenas de idiomas y su comunidad es global; no hay razón para
cerrarnos ahí.

---

## El análisis geométrico: casi todo ya existe en Orca

**Revisado el 2026-08-06.** La conclusión importante: no hay que escribirlo, hay
que **exponer lo que Orca ya calcula**.

### Integridad de la malla — `TriangleMeshStats` (`src/libslic3r/TriangleMesh.hpp`)

```cpp
open_edges          // agujeros en la superficie
degenerate_facets   // triángulos sin área
facets_reversed     // normales invertidas
backwards_edges
edges_fixed, facets_removed
manifold()          // ¿es un sólido cerrado?
```

Es exactamente lo que hacía falta, probado durante años sobre millones de
piezas.

### Orientaciones — `Orient.cpp` / `Orient.hpp` (`src/libslic3r/`)

Puntúa **cada orientación candidata** con:

| Campo | Qué es |
|---|---|
| `overhang` | área en voladizo |
| `bottom`, `bottom_hull` | área de contacto con la cama |
| `contour` | longitud del contorno |
| `area_laf` | área de caras de ángulo bajo |
| `area_projected` | perfil proyectado en 2D |
| `volume`, `area_total` | volumen y superficie total |
| `height_to_bottom_hull_ratio` | **estabilidad** (más bajo = mejor) |

`OrientMesh` además ya lleva `overhang_angle` configurable por objeto.

### Lo que sí puede faltar — verificar antes de escribir

- **Espesor mínimo de pared** comparado contra el ancho de línea configurado.
- **Señales para deducir el uso** (decisión 6): agujeros pasantes, roscas,
  relación superficie/volumen, simetría.

Solo si no existen se escriben, y siguiendo el estilo de `libslic3r`.

### Referencia descartada

Hay una implementación propia en el repo archivado
`nachorepara/nacod3d-slicer`, en `src/viewer/malla.ts`. **Quedó obsoleta**: Orca
lo hace mejor. Se conserva únicamente por un detalle que documenta bien —
que hay que soldar vértices con tolerancia antes de poder detectar agujeros,
porque un STL repite cada vértice sin decir cuáles son el mismo punto.

## Cómo se redactan los avisos

En términos de **qué le va a pasar a la impresión**, nunca en jerga:

> ✗ "Malla no manifold: 47 aristas abiertas"
>
> ✓ "La malla tiene 47 aristas sueltas: es una superficie con agujeros, no un
> sólido cerrado. El laminado puede salir con capas incompletas."

---

## Pendiente de decidir

- **Qué se guarda del historial y dónde.** Local, y con qué formato.
- **Privacidad de las fotos.** Van a un tercero (el proveedor de IA): hay que
  decirlo claramente antes de la primera subida.
