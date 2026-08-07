# Materiales: qué sabe Orca y qué tenemos que aportar nosotros

> Investigado el 2026-08-07.
> Base para la recomendación de material según el uso de la pieza.

## El inventario

**4837 perfiles de filamento**, 18 tipos de material:

| Tipo | Perfiles | | Tipo | Perfiles |
|---|---|---|---|---|
| PLA | 210 | | PA | 43 |
| PETG | 128 | | PC | 39 |
| PLA-CF | 83 | | PVA | 36 |
| PA-CF | 76 | | PET | 24 |
| TPU | 68 | | PPS | 17+18 |
| ABS | 65 | | HIPS | 16 |
| ASA | 65 | | PP | 15 |
| PETG-CF | 45 | | BVOH | 11 |

## Lo que el perfil sí sabe

```
filament_type                  PETG
nozzle_temperature             255
hot_plate_temp                 80
filament_density               1.27
filament_cost                  30
filament_max_volumetric_speed  10
filament_flow_ratio            0.95
filament_soluble               0
temperature_vitrification      70      ← la joya
```

**`temperature_vitrification` es la única propiedad física real** que guardan: la
temperatura a la que la pieza empieza a ablandarse.

| Material | Se ablanda a | Densidad | Boquilla |
|---|---|---|---|
| TPU | 30 °C | 1.24 | 240 |
| **PLA** | **45 °C** | 1.24 | 220 |
| PVA | 45 °C | 1.24 | 220 |
| PETG | 70 °C | 1.27 | 255 |
| ABS | 100 °C | 1.04 | 270 |
| ASA | 100 °C | 1.04 | 260 |
| HIPS | 100 °C | 1.06 | 240 |
| PA (nylon) | 108 °C | 1.04 | 260 |
| PP | 110 °C | 0.93 | 235 |
| PC | 120 °C | 1.04 | 280 |

**Con esto solo ya se pueden dar consejos concretos.** Una pieza que va a quedar
en un auto al sol —donde el interior supera los 70 °C— hecha en PLA se deforma, y
el dato para decirlo está ahí.

> **Ojo con los valores.** Los números de Orca son **conservadores**: la
> literatura suele citar 55–60 °C para PLA y 80–85 °C para PETG, y Orca dice 45 y
> 70. Parece "cuándo empieza a ablandarse" y no la transición vítrea estricta.
> Además **varían por fabricante** — el PETG de Creality dice 80 y el genérico
> 70. Otra razón para leer el perfil cargado y no una tabla nuestra.
>
> Redactar los avisos como *"empieza a ablandarse alrededor de X"*, nunca como un
> valor exacto.

## Lo que NO sabe, y tenemos que aportar

Ninguna de estas propiedades está en los perfiles:

- **Resistencia UV / intemperie** — es la diferencia clave entre ABS y ASA
- **Resistencia mecánica y a impactos**
- **Adhesión entre capas** (cuánto aguanta la fuerza en el eje Z)
- **Higroscopía** — PA absorbe humedad y eso arruina la impresión
- **Facilidad de impresión** — PLA fácil, ABS se despega, PA es difícil

Es una tabla **chica (18 materiales) y estable**: se escribe una vez y no cambia
con las versiones de Orca. **No hace falta IA para esto.**

La IA aporta arriba: cruzar esa tabla con el uso concreto de la pieza y explicar
el porqué en lenguaje humano.

## Ejemplo de la recomendación completa

```
┌────────────────────────────────────────────────────┐
│ Vas a usar esta pieza a la intemperie.             │
│                                                     │
│ El PLA elegido empieza a ablandarse a 45 °C y no    │
│ resiste el sol: en unos meses se vuelve quebradizo. │
│                                                     │
│ Para exterior conviene ASA — aguanta hasta 100 °C   │
│ y resiste UV. El PETG es una alternativa más fácil  │
│ de imprimir, pero se degrada más rápido al sol.     │
│                                                     │
│   Filamento   Creality Generic PLA → Generic ASA    │
│   Boquilla    220 °C → 260 °C                       │
│   Cama        Al cambiar, revisar adherencia        │
│                                                     │
│        [ Aplicar ]  [ ¿Por qué? ]  [ Ignorar ]     │
└────────────────────────────────────────────────────┘
```

De ahí, **la temperatura y el ablandamiento salen del perfil**; la resistencia UV
y la dificultad de impresión salen de nuestra tabla.

## Generador de paredes: cuándo cada uno

Conocimiento de uso real, no del código — no está documentado en Orca:

| | Cuándo conviene |
|---|---|
| **Clásico** | Piezas paramétricas, tolerancias, encastres. **Ancho de extrusión constante = dimensiones predecibles.** |
| **Arachne** | Perímetros con mucho detalle y paredes curvas. **Ancho variable = sigue mejor la forma.** |

Eso convierte la elección del generador en una recomendación posible, y encaja
con la deducción del uso de la pieza (decisión 6 en
[`ASISTENTE.md`](ASISTENTE.md)): si la pieza parece un conjunto mecánico con
encastres, clásico; si es orgánica y detallada, Arachne.

Ver la advertencia sobre no asumir generador en
[`INVESTIGACION-ORIENT.md`](INVESTIGACION-ORIENT.md) sección 2.

## Cabo suelto resuelto

El primer día, el G-code de prueba salió con `filament_density: 0` y anoté que el
perfil de PLA de Creality no tenía densidad. **Era falso.**

Resolviendo la herencia, `Creality Generic PLA` tiene `filament_density: 1.24` y
`temperature_vitrification: 60`. El cero venía de **el CLI de Orca no resolviendo
la cadena de herencia** — el mismo problema que costó el rato del Paso 0.

De 4597 perfiles con tipo de material declarado, solo **110 no tienen densidad
utilizable**, y son casi todos perfiles base abstractos (`fdm_filament_common`),
no perfiles que el usuario vea.
