# Perfiles de opinión — «como lo haría nacod3d»

> Decidido el 2026-08-07.

## La idea

Un botón que configura una sección del perfil **como la configuraría nacod3d**,
en vez de dejar los defaults de Orca.

```
[ Poner los soportes como lo haría nacod3d ]

  Ángulo umbral        30°   →  40°
  Distancia Z superior 0.2   →  0.22
  Capas de interfaz    3     →  2
  Espaciado interfaz   0.5   →  0.4
  Distancia XY         0.35  →  0.4
```

## Por qué funciona: el nombre es la mitad del valor

No se llama "configuración recomendada" ni "ajustes óptimos". Se llama **como lo
haría nacod3d**, y esa diferencia es la que sostiene toda la función.

"Recomendado" pretende objetividad, y por lo tanto **se puede desmentir**:
alguien con otra impresora prueba los valores, le sale peor, y quedamos como que
dimos un mal consejo.

**"Como lo haría nacod3d" es honesto: es una opinión con dueño.** Nadie puede
discutir que nacod3d lo hace así. Y es exactamente lo que un principiante
necesita — no quiere entender siete parámetros, quiere que alguien que sabe se
los ponga.

**Regla:** nunca renombrar esto a algo que suene objetivo. La honestidad sobre
que es una opinión es lo que lo hace defendible.

## El problema que resuelve

Los defaults de Orca para soportes:

| Parámetro | Default |
|---|---|
| Ángulo umbral | 30° |
| Distancia Z superior / inferior | 0.2 / 0.2 |
| Capas de interfaz superior / inferior | 3 / 0 |
| Espaciado de interfaz superior | 0.5 |
| Distancia XY soporte/objeto | 0.35 |

Quien imprime seguido los cambia siempre. Quien recién empieza no sabe que hay
que cambiarlos, y le salen soportes imposibles de sacar o piezas arruinadas al
despegarlos.

## Decisiones tomadas

### Varía según material y tipo de pieza

No un juego único. Los soportes en PETG se pegan mucho más que en PLA, así que la
distancia Z tiene que ser distinta; y una pieza con voladizos suaves no necesita
lo mismo que una con salientes agresivos.

```
PLA  + voladizos suaves      → ángulo 40°, Z 0.20, interfaz 2
PETG + voladizos suaves      → ángulo 40°, Z 0.25, interfaz 2
cualquiera + salientes duros → árbol, ángulo 50°, interfaz 3
```

El material sale del perfil cargado; el tipo de pieza, del análisis geométrico
que ya existe (ver [`INVESTIGACION-ORIENT.md`](INVESTIGACION-ORIENT.md)).

### Se diseña como sistema desde el inicio

Aunque al principio solo se complete la sección de soportes, el mecanismo se
piensa para varias:

```
opiniones/
  soportes.json      ← primera en completarse
  adherencia.json
  velocidades.json
  temperaturas.json
```

Así no hay que rehacerlo cuando se extienda. Cuesta más antes del primer
resultado visible, pero evita reescribir el mecanismo tres veces.

## Los valores varían por impresora — el botón no puede ser una lista fija

Medido sobre **493 perfiles "0.2 Standard"** de todos los fabricantes:

| Parámetro | Mayoría | Pero también |
|---|---|---|
| Distancia Z superior | 0.2 (294) | 0.15, 0.1, 0.18, 0.12, 0 |
| Espaciado de interfaz | 0.5 (297) | **0.2 (101)**, 0, 0.12, 1 |
| Distancia XY | 0.35 (306) | **60% (62)**, 0.5, 0.2, 0.3 |
| Capas de interfaz | 2 (364) | 3 (108) |
| Ángulo umbral | 30 (419) | 40, 35, 20 |

Hay una mayoría clara en cada uno, pero la variación es real y **buena parte es
deliberada**: una impresora rápida o de cinemática distinta necesita otros
valores, y el fabricante los puso ahí por algo.

> **Consecuencia de diseño:** la opinión **no puede ser una lista de valores
> absolutos** que pise el perfil. Tiene que expresarse como reglas relativas al
> perfil cargado — «si el espaciado de interfaz está por debajo de X, subirlo»,
> «la distancia Z, al menos Y» — o en unidades relativas a la boquilla y la
> altura de capa.
>
> Un valor absoluto de Creality aplicado a una Prusa sería exactamente el tipo
> de mal consejo que hunde la credibilidad del asistente.

Nota: los valores de la CR-10 V2 (0.15 / 0.2 / 60% / 3) están **todos en la
minoría**. No es un perfil representativo para sacar conclusiones generales.

## ~~Posible bug del upstream~~ — DESCARTADO, era mi error

> **Verificado en pantalla el 2026-08-07: NO hay bug.** El perfil dice `"60%"` y
> la interfaz muestra **0.35** — el valor heredado del padre. Orca descarta el
> valor inválido y usa la herencia. Mi lectura del `iss >> value` no reflejaba
> lo que pasa en la carga real de perfiles.
>
> **Lo único real, y es menor:** quien escribió esos 373 perfiles quiso poner un
> porcentaje y Orca lo ignora en silencio. La intención del fabricante se pierde,
> pero el resultado es el valor heredado, que es sensato. Nada roto.
>
> **Lección:** tres veces en esta sesión saqué una conclusión leyendo código y
> las tres veces la realidad la desmintió. El código dice qué es posible; los
> perfiles y la pantalla dicen qué pasa. **Verificar en la app antes de afirmar.**

<details>
<summary>El razonamiento equivocado, conservado como advertencia</summary>

`support_object_xy_distance` está declarado como **`coFloat`** — un número en
milímetros, con máximo 10:

```cpp
this->add("support_object_xy_distance", coFloat);
((ConfigOptionFloat, support_object_xy_distance))
def->sidetext = L("mm");   def->max = 10;
```

Pero **373 perfiles de 14 fabricantes** le ponen un porcentaje (`"60%"`),
incluidos Prusa, Creality, Anycubic, Qidi y Ratrig — y el de la CR-10 V2.

Y `ConfigOptionFloat::deserialize` (`Config.hpp:825`) hace:

```cpp
std::istringstream iss(str);
iss >> this->value;    // lee 60, se detiene en el '%'
return !iss.fail();    // no falla: leyó un número
```

Con lo cual `"60%"` quedaría en **60 mm** de separación, que es absurdo. El tipo
es `coFloat` desde el import original de BambuStudio: nunca cambió.

**No está confirmado.** No encontré acotado al máximo al cargar, pero tampoco
descarto que haya manejo en otro lado — a 373 perfiles de escala, un bug así
debería haber saltado antes.

**Verificado: la interfaz muestra 0.35, no 60.** Hipótesis descartada.

</details>

## Lo que hace falta y no puedo inventar

**Los valores tienen que salir de la experiencia de Nacho.** Ese es todo el
punto de la función: sin sus números es un botón vacío. El mecanismo se puede
construir antes, pero no sirve de nada hasta que estén cargados.

Hay que definir, por combinación de material y tipo de pieza:

- Ángulo umbral (o si conviene el modo por solapamiento, ver abajo)
- Distancia Z superior e inferior
- Capas y espaciado de interfaz
- Distancia XY soporte/objeto
- Tipo (normal o árbol) y estilo
- Patrón de base

## Cuidados

**Mostrar siempre qué cambió.** Si aplica valores que en la impresora de otro
salen mal, el botón daña la confianza en vez de construirla. Va con el diff a la
vista, como la decisión 2 de [`ASISTENTE.md`](ASISTENTE.md).

**Es reversible.** Tiene que poder deshacerse en un clic.

**No pisar lo que el usuario ya tocó a mano** sin avisar. Si alguien ya ajustó la
distancia Z, decírselo antes de cambiarla.

## Conexión con comoimprimo

*"¿Por qué nacod3d lo hace así?"* → el artículo correspondiente. Es la forma más
natural de conectar los dos proyectos, y llega cuando el manual tenga contenido
(decisión 7 de [`ASISTENTE.md`](ASISTENTE.md)).

---

## Apéndice: cómo decide Orca dónde poner soporte

Investigado el 2026-08-07. Es **bastante más rico que un simple umbral de
ángulo**, al contrario de lo que suele suponerse.

`detect_overhangs()` (`src/libslic3r/Support/SupportMaterial.cpp:1370`) combina:

| Criterio | Qué hace |
|---|---|
| `threshold_angle` | El ángulo. Default **30°** |
| `threshold_overlap` | **Si el ángulo es 0**, usa solapamiento en vez de ángulo. Default 50% |
| `bridge_no_support` | Los puentes no llevan soporte |
| `buildplate_only` | Solo lo que se apoya en la cama |
| `sharp_tails` | Tratamiento especial para colas finas |
| enforcers | Lo pintado a mano ignora todo lo demás |

El núcleo de la decisión:

```cpp
lower_layer_offset =
    has_enforcer      ? 0                                  // pintado: soporta todo
  : threshold_rad > 0 ? layer_height / tan(ángulo)         // por ÁNGULO
                      : fw - threshold_overlap;            // por SOLAPAMIENTO
```

**El modo por solapamiento es el más interesante** y casi nadie lo usa: en vez de
preguntar "¿qué inclinación tiene esta cara?", pregunta **"¿cuánto de esta línea
de extrusión tiene material debajo donde apoyarse?"**. Es un modelo físico más
directo, y se activa poniendo el ángulo umbral en 0.

> Puede ser una recomendación interesante en sí misma, y encaja con la queja de
> que el automático "pone soportes de más en todos lados": quizás el problema no
> es el valor del ángulo sino usar ángulo en vez de solapamiento.
> **Hay que probarlo antes de recomendarlo.**

Nota: con soportes de árbol, un ángulo de 0 no usa solapamiento — cae a un valor
por defecto de 30.
