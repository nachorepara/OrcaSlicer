# Backlog

Ideas con la investigación ya hecha, para no arrancar de cero cuando les toque.
No están priorizadas entre sí.

---

## Resumen de "todo lo distinto al estándar"

**El problema.** Cuando abrís un 3MF que armó otra persona, Orca te marca en
naranja cada valor que difiere del perfil de sistema. Está bien, pero si el otro
tocó veinte parámetros repartidos en seis pestañas, tenés que ir a cazarlos uno
por uno. No hay forma de barrer todas las diferencias de una sola vez.

**Lo que queremos.** Un botón que abra un resumen de todo lo que está distinto al
perfil predefinido, con el valor original y el actual.

```
┌─ Diferencias con «0.20mm Standard @Creality CR10V2» ─┐
│                                                       │
│  CALIDAD                                              │
│    Perímetros              2      →  3                │
│    Altura de capa          0.20   →  0.16 mm          │
│                                                       │
│  FUERZA                                               │
│    Relleno                 15%    →  40%              │
│    Patrón de relleno       rejilla → giroide          │
│                                                       │
│  VELOCIDAD                                            │
│    Perímetro externo       25     →  18 mm/s          │
│                                                       │
│  14 parámetros modificados en total                   │
│              [ Restaurar todo ]  [ Exportar lista ]   │
└───────────────────────────────────────────────────────┘
```

**Por qué es viable.** El dato ya está calculado; falta la pantalla. Es el mismo
caso que la orientación: Orca lo sabe y no lo muestra.

| Pieza que ya existe | Dónde |
|---|---|
| `config.diff(config)` — devuelve las claves que difieren | `src/libslic3r/Preset.hpp:316` |
| `get_differed_values_to_update(preset, key_values)` — devuelve clave → valor | `src/libslic3r/Preset.hpp:554` |
| `dirty_options` / `nonsys_options` — vectores de opciones modificadas | `src/slic3r/GUI/Tab.hpp:387` |
| `m_color_label_modified = "#F1754E"` — el naranja de "modificado" | `src/slic3r/GUI/GUI_App.cpp:4066` |

Ese último es lindo: **el color que Orca ya usa para "modificado" es un naranja**,
así que la función encaja natural con la marca sin forzar nada.

**Lo que hay que resolver.** Agrupar por categoría respetando el orden de las
pestañas, traducir los nombres internos de los parámetros a los rótulos que ve el
usuario (ya existe ese mapeo para dibujar la UI), y decidir si "Restaurar todo"
entra en la primera versión o es un segundo paso.

**Dónde se cruza con la IA.** Muy bien: con la lista de diferencias en la mano,
el asistente puede explicar *qué hace* cada cambio y si tienen sentido juntos —
por ejemplo, advertir que alguien subió la velocidad de perímetro externo y a la
vez bajó la altura de capa buscando calidad, y que las dos cosas se pelean. Pero
**la lista sola ya es útil sin nada de IA**, y conviene construirla primero.

---

## Aviso de detalles que se imprimen más gruesos de lo diseñado

**El problema.** Con Arachne (el generador por defecto), los detalles del modelo
más finos que `min_bead_width` **se ensanchan hasta ese valor**. Con los defaults
y boquilla de 0.4 mm, cualquier detalle entre 0.10 y 0.34 mm sale de 0.34 mm.

Un detalle de 0.15 mm sale **más del doble de grueso**. Si el diseño tenía una
tolerancia o un encastre, la pieza puede no entrar — y **no hay forma de
enterarse antes de imprimir**.

**Lo que queremos.**

```
┌──────────────────────────────────────────────────┐
│ 3 zonas de tu modelo son más finas que 0.34 mm   │
│ y se van a imprimir más gruesas de lo diseñado.  │
│                                                   │
│ La más fina mide 0.15 mm y saldrá de 0.34 mm.    │
│                                                   │
│ Propuesta:                                        │
│   Ancho mínimo de pared   85%  →  45%            │
│                                                   │
│ Si esas zonas son encastres o tolerancias,        │
│ la pieza podría no entrar como está ahora.        │
│                                                   │
│        [ Aplicar ]   [ ¿Por qué? ]   [ Ignorar ] │
└──────────────────────────────────────────────────┘
```

**El arreglo correcto** es bajar `min_bead_width`, que actúa como **piso**: si el
detalle es más grueso que ese valor, la pared toma el espesor real del detalle.
Bajarlo de 85% a 45% hace que un detalle de 0.15 mm salga de 0.18 en vez de 0.34.

**Lo que NO es el arreglo:** cambiar de generador de paredes. Arachne ya es el
default, y volver al clásico es peor — tiene ancho de extrusión constante,
mientras que Arachne es variable justamente para manejar estos casos. Lo que hay
que hacer es permitirle ir más fino.

**Sin IA y sin costo.** La detección la hace Orca durante el laminado; nosotros
leemos el resultado y lo explicamos.

**Limitación:** el aviso llega después de laminar, no al cargar la pieza, porque
la detección es por capa en 2D. Igual sirve: es antes de imprimir.

Detalle técnico completo en [`INVESTIGACION-ORIENT.md`](INVESTIGACION-ORIENT.md)
sección 2.

---

## Telemetría — DESCARTADA (2026-08-06)

**La idea era** guardar estadísticas de qué lamina la gente, para alimentar los
cursos de comoimprimo.

**Por qué se descartó.** Orca desactiva la telemetría de Bambu **a propósito, en
tres lugares distintos** de `GUI_App.cpp`, con comentarios que insisten en
"never" y "always disable it". No es un descuido: es una postura, y parte de por
qué la gente eligió Orca sobre Bambu Studio.

Nuestro código es público (AGPL) y la comunidad de impresión 3D lee estas cosas.
Agregar telemetría a un fork de Orca se descubriría en semanas, y el titular no
sería "nacod3d recopila estadísticas anónimas" sino **"un fork de Orca le puso el
tracking que Orca sacó a propósito"**. Un proyecto chico no se recupera de eso.

A eso se suma lo legal: GDPR para usuarios europeos y Ley 25.326 en Argentina
exigen consentimiento explícito y previo, política de privacidad y mecanismo de
borrado. Se puede cumplir, pero es responsabilidad y trabajo para algo que además
expone.

**Si alguna vez se retoma**, la única forma aceptable:

- Opt-in real, apagado por defecto, con la lista exacta de qué se envía
- Solo agregados anónimos: modelo de impresora, material, altura de capa
- **Nunca** nombres de archivo, geometría ni modelos
- Adopción esperable: ~5%. Es dato legítimo, no masivo.

**Alternativas más baratas para la misma pregunta**, en orden de utilidad real:

1. **Los issues y discusiones del repo.** La gente cuenta sus problemas sola y
   con más detalle del que daría cualquier telemetría. Un "no me pega el PETG en
   la cama" vale más para armar un curso que mil registros de altura de capa.
2. **La analítica de comoimprimo** — qué buscan y qué leen está más cerca de la
   pregunta real que qué laminan.
3. **Las descargas de GitHub** para volumen y crecimiento.
4. Una encuesta opcional enlazada desde el "Acerca de".

---

## Otras ideas

*(a completar)*
