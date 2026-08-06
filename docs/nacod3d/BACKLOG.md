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
