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

## 2. Paredes demasiado finas — Orca lo sabe y no avisa

**`detect_thin_wall`** (`PrintConfig.cpp:7253`) es una **opción de configuración**,
no un análisis que se le muestre al usuario.

**Arachne** (`src/libslic3r/Arachne/WallToolPaths.hpp:136`) tiene
`min_feature_size`, documentado como:

> *"The minimum size of the features that can be widened by the widening beading
> meta-strategy. **Features thinner than that will not be printed**"*

Verificado: **no hay ningún aviso al usuario** cuando eso pasa. Orca descarta en
silencio los detalles más finos que la boquilla, y uno se entera cuando la pieza
sale sin ellos.

**Oportunidad clara**: avisar antes de imprimir qué partes del modelo no van a
salir. Es información que Orca ya tiene.

**Limitación**: la detección ocurre **durante el laminado**, por capa en 2D, no
sobre la malla cruda. Así que el aviso llega después de laminar, no al cargar la
pieza. Igual sirve — es antes de imprimir, que es lo que importa.

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
