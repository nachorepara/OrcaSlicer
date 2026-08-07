# Cómo sacar el razonamiento que Orca esconde

> Investigado el 2026-08-07 leyendo el código, sin compilar nada.
> Es el plan de implementación de la primera función del asistente.

## Resumen

| Pregunta | Respuesta |
|---|---|
| ¿Orca calcula el razonamiento de la orientación? | **Sí, completo**, y lo descarta al terminar |
| ¿Se puede sacar? | Sí, tocando ~20 líneas de `Orient.hpp` y `Orient.cpp` |
| ¿Detecta paredes demasiado finas? | **Sí, y las descarta en silencio sin avisar** |
| ¿Sirve para deducir el uso de la pieza? | Parcialmente — ver la tabla al final |

---

## 1. El razonamiento de la orientación

### Dónde está el dato

`src/libslic3r/Orient.cpp`, dentro de `AutoOrienter::process()`:

```cpp
struct CostItems {              // namespace orientation, solo en el .cpp
    float overhang;             // área en voladizo
    float bottom;               // área de contacto con la cama
    float bottom_hull;          // casco convexo del apoyo
    float contour;              // longitud del contorno
    float area_laf;             // área de caras de ángulo bajo
    float area_projected;       // perfil proyectado en 2D
    float volume, area_total;
    float radius;               // radio de la caja envolvente
    float height_to_bottom_hull_ratio;   // estabilidad (menor = mejor)
    float unprintability;       // el puntaje final
    ...
    static std::string field_names();   // ya sabe imprimirse solo
    std::string field_values();
};
```

`results_vector` guarda **todas** las orientaciones candidatas con su `CostItems`,
ordenadas por `unprintability`. En la línea 184 hay hasta un `std::cout` que
vuelca la mejor. Después `process()` devuelve solamente `Vec3d` con la
orientación elegida, y **todo lo demás se pierde**.

### Cómo decide — la fórmula (línea 472, `target_function`)

```
costo =  RELATIVE_F · (voladizo·TAR_C + TAR_D + TAR_LAF·area_laf)
        ──────────────────────────────────────────────────────────
        (TAR_D + CONTOUR_F·contorno + BOTTOM_F·bottom
                + BOTTOM_HULL_F·bottom_hull + TAR_PROJ_AREA·area_proyectada)

costo += 100   si  bottom < BOTTOM_MIN
```

**Arriba lo malo, abajo lo bueno.** Menor costo, mejor orientación.

Ese `+100` es un **veto duro**: si el contacto con la cama queda por debajo del
mínimo, la orientación se descarta aunque sea perfecta en todo lo demás. Eso nos
permite explicar rechazos, no solo preferencias:

> *"La alternativa tenía menos voladizo, pero se descartó porque el contacto con
> la cama quedaba por debajo del mínimo y la pieza se despegaría."*

Los pesos están en `OrientParamsArea` (`Orient.hpp`): `TAR_A = 0.015`,
`TAR_B = 0.177`, `RELATIVE_F = 20`, etc.

### Qué hay que cambiar

Es un cambio chico pero **toca archivos del upstream**, así que va a generar
conflictos al sincronizar. Inevitable para esta función.

1. **Mover `CostItems` a `Orient.hpp`** (o una versión pública reducida). Hoy
   vive solo en el `.cpp`.
2. **Agregar un campo a `OrientMesh`**, que ya es la estructura de entrada/salida
   de `orient()` y por lo tanto llega sola al llamador:
   ```cpp
   // nacod3d: por qué se eligió esta orientación
   std::vector<std::pair<Vec3f, orientation::CostItems>> candidatas;
   ```
3. **Poblarlo en `process()`** antes del `return`, con las mejores N candidatas.

`OrientMesh` ya tiene un `std::function<void(const OrientMesh&)> setter`, así que
el patrón de devolver cosas al llamador ya existe.

### Qué se puede mostrar

Todo esto sale del dato ya calculado, **sin IA y sin costo**:

```
Orientación elegida: rotada 90° en X

  Voladizo          12.4 cm²  →   0.8 cm²     -94%
  Contacto cama      8.1 cm²  →  31.5 cm²     +289%
  Estabilidad        0.91     →   0.62        mejor
  Contorno          expuesto  →  apoyado

  Se eligió esta porque elimina casi todo el voladizo
  sin perder estabilidad.

  ▸ Ver las otras 3 orientaciones evaluadas
```

---

## 2. Detalles finos — dos cosas pasan, y ninguna se avisa

> **Corregido el 2026-08-07.** La primera versión de este documento decía que
> `detect_thin_wall` descartaba paredes finas. **Es falso**: es un mecanismo de
> rescate, y ni siquiera aplica al generador que viene por defecto.

### Cuál generador de paredes se usa realmente — cuidado acá

**El default del código no es el default efectivo.** `PrintConfig.cpp` define
Arachne, pero **los perfiles lo pisan**, y la mayoría elige clásico:

| Fabricante | classic | arachne |
|---|---|---|
| **Creality** | **135** | 4 |
| Anycubic | 71 | 0 |
| Sovol | 20 | 0 |
| Artillery | 3 | 14 |
| Prusa | 0 | 3 |
| Voron | — | — (cae en Arachne por código) |

Total: **316 perfiles eligen clásico contra 60 que eligen Arachne.**

Y hay excepciones dentro de un mismo fabricante. `0.20mm Standard @Creality
CR10V2` **no define `wall_generator` en ningún eslabón de su cadena**, así que
cae en Arachne — mientras que otros 135 perfiles Creality sí ponen clásico.
Ese mismo perfil activa `detect_thin_wall`, que en Arachne no hace nada.
Parece una inconsistencia de los perfiles del upstream, no algo intencional.

> **Implicación de diseño, importante:** el asistente **no puede asumir un
> generador**. Tiene que leer la configuración efectiva del perfil cargado,
> resolviendo la cadena de herencia y los cambios manuales del usuario. Un aviso
> que asuma Arachne sería incorrecto para la mayoría de los perfiles; uno que
> asuma clásico sería incorrecto para los demás.

### Qué hace realmente `detect_thin_wall`

Es una opción del **generador clásico solamente** — vive dentro de
`PerimeterGenerator::process_classic()` (`PerimeterGenerator.cpp:1424`) y no
aplica a Arachne.

Cuando aplica, es un **rescate**: calcula el eje medial de la zona fina y la
imprime con una sola línea. Su tooltip lo dice: *"detecta paredes finas que no
pueden contener dos líneas y usa una sola línea para imprimirlas"*.

Y aun con la opción apagada, el generador clásico tiene otro rescate: para
"islas angostas" usa un **ancho de extrusión menor** en vez de descartarlas.

O sea: **el generador clásico no descarta nada.**

### Lo que sí pasa, con Arachne

Dos umbrales, ambos como porcentaje del diámetro de boquilla:

| Parámetro | Default | En boquilla 0.4 |
|---|---|---|
| `min_feature_size` | 25% | 0.10 mm |
| `min_bead_width` | 85% | 0.34 mm |

El tooltip de `min_feature_size` es literal:

> *"Los detalles del modelo más finos que este valor **no se imprimirán**,
> mientras que los más gruesos **se ensancharán** al ancho mínimo de pared."*

Con boquilla de 0.4 mm y configuración por defecto:

| Espesor del detalle | Qué le pasa |
|---|---|
| menos de 0.10 mm | **No se imprime. Desaparece.** |
| 0.10 – 0.34 mm | **Se ensancha a 0.34 mm.** La geometría cambia. |
| más de 0.34 mm | Se imprime como fue diseñado |

**Verificado: ninguno de los dos casos se le informa al usuario.**

### La oportunidad — y el segundo caso es el bueno

Que un detalle de 0.05 mm desaparezca suele ser irrelevante: a esa escala casi
siempre es un artefacto del modelado.

**El caso interesante es el ensanchado.** Un detalle de 0.15 mm sale de 0.34 —
más del doble de grueso. Si el diseño tenía una tolerancia o un encastre, la
pieza puede no entrar, y **no hay ninguna forma de enterarse antes de imprimir**.

Un aviso del tipo *"3 zonas de tu modelo se van a imprimir más gruesas de lo
diseñado"* sería información que ningún laminador da hoy.

**Limitación**: la detección ocurre **durante el laminado**, por capa en 2D, no
sobre la malla cruda. El aviso llega después de laminar, no al cargar la pieza.
Igual sirve: es antes de imprimir, que es lo que importa.

---

## 3. Señales para deducir el uso de la pieza (decisión 6)

| Señal | ¿Ya existe? | Dónde |
|---|---|---|
| Volumen | ✅ | `TriangleMesh::volume()`, `its_volume()` |
| Superficie total | ✅ | `CostItems::area_total` |
| Relación superficie/volumen | ✅ derivable | de las dos anteriores |
| **Cantidad de partes sueltas** | ✅ | `TriangleMeshStats::number_of_parts` |
| Caja envolvente y radio | ✅ | `CostItems::radius` |
| Área de caras de ángulo bajo | ✅ | `CostItems::area_laf` |
| Agujeros pasantes | ❌ | habría que escribirlo |
| Roscas | ❌ | difícil, probablemente no valga la pena |

`number_of_parts` es una señal interesante que no habíamos considerado: un objeto
con varias piezas sueltas sugiere un conjunto mecánico o un modelo para armar.

**Conclusión para la decisión 6:** hay suficiente para arriesgar una lectura sin
escribir código nuevo — relación superficie/volumen, cantidad de partes, área de
caras de ángulo bajo y proporciones de la caja envolvente. Los agujeros pasantes
son la señal más valiosa que falta; se puede evaluar después si el resto no
alcanza.

---

## El patrón, otra vez

Van cuatro casos donde **Orca calcula algo y no lo muestra**:

| | Lo calcula | No lo muestra |
|---|---|---|
| Orientación | voladizo, estabilidad, contacto, y **por qué descartó cada alternativa** | nada, solo rota el objeto |
| Paredes finas | qué detalles no se van a imprimir | nada, los descarta en silencio |
| Diferencias de perfil | las claves que difieren | las marca una por una, sin resumen |
| Integridad de malla | agujeros, normales invertidas, partes sueltas | casi nada |

Es la identidad del fork: **el laminador que te cuenta lo que está pensando.**
