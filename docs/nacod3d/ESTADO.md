# nacod3d Slicer — estado del fork

> Última actualización: 2026-08-06
>
> Este documento y todo lo que está bajo `docs/nacod3d/` es **nuestro**, no del
> upstream. Para el entorno de desarrollo, ver [`ENTORNO.md`](ENTORNO.md).

## Qué es

Un fork de **OrcaSlicer** con la marca de nacod3d y, encima, una capa de IA que
le enseña al usuario a imprimir mejor: recomendaciones de orientación, soportes,
altura de capa y material según la geometría de la pieza y el uso que va a
tener; y después de imprimir, subir fotos del resultado para proponer ajustes.

**La base es Orca y tiene que seguir siéndolo.** Misma interfaz, misma UX, mismo
soporte de impresoras. Lo único que cambia es el acento de color, el nombre, y
lo que agregamos arriba.

## Estado

| | |
|---|---|
| El fork compila sin modificar | ✅ 29 jobs verdes, instaladores generados |
| CI recortado a Windows x64 | ✅ `build_nacod3d.yml` |
| Re-skin a naranja | ✅ aplicado y revisado en pantalla |
| Renombre del producto | ✅ `nacod3d Slicer`, con atribución en el Acerca de |
| Análisis geométrico | ⬜ |
| Panel de IA | ⬜ |

---

## Por qué forkeamos en vez de construir de cero

Primero se intentó una app nueva y liviana (Tauri + three.js) que llamara a Orca
en modo headless por detrás. Se descartó: **la interfaz tiene que ser Orca**, y
reconstruirla es un proyecto de años — son 430.000 líneas de C++ solo en la GUI,
con cientos de paneles, el árbol de parámetros, la previsualización del G-code y
los asistentes de calibración.

El intento vive en `nachorepara/nacod3d-slicer` y quedó archivado. Lo único que
sobrevive de ahí es la lógica de diagnóstico de malla, que se porta a C++ (ver
tarea pendiente más abajo).

## Licencia — leer antes de tocar nada

OrcaSlicer es **AGPL-3.0**. Al modificarlo, **todo lo que agreguemos encima es
obra derivada y queda bajo AGPL**, incluida la capa de IA.

En concreto:

- Se puede vender, cobrar suscripción, todo eso es legal.
- **Hay que publicar el código fuente.** Por eso el repo es público.
- Cualquiera puede tomarlo, sacarle la marca y redistribuirlo. El diferencial
  pasa a ser la ejecución, la marca y la comunidad, no el código.
- Efecto secundario bueno: al ser público, el CI tiene minutos ilimitados.

**La atribución a OrcaSlicer es obligatoria y además corresponde.** Cuando se
haga el renombre, la pantalla de "Acerca de" tiene que decir claramente que esto
es un derivado de OrcaSlicer, con enlace al proyecto original.

---

## Cómo está organizado nuestro trabajo

**Regla:** agregamos archivos, no editamos los del upstream, siempre que se
pueda. Así sincronizar con Orca no genera conflictos.

| Archivo nuestro | Para qué |
|---|---|
| `.github/workflows/build_nacod3d.yml` | Compila solo Windows x64 |
| `tools/reskin-nacod3d.py` | Aplica el naranja de la marca |
| `docs/nacod3d/` | Esta documentación |

`build_all.yml` del upstream queda **intacto pero desactivado** en el fork
(vía API, no editando el archivo). Sigue disponible por disparo manual para
releases multiplataforma.

### El re-skin

`tools/reskin-nacod3d.py` cambia el acento teal de Orca (`#009688` y familia)
por el naranja de nacod3d (`#EA580C`, el mismo que usan `nacod3d-web` y
`comoimprimo`).

```bash
python3 tools/reskin-nacod3d.py            # prueba: dice qué haría
python3 tools/reskin-nacod3d.py --aplicar  # escribe
```

**Es re-ejecutable a propósito.** Cada sincronización con el upstream trae teal
nuevo en código nuevo; correrlo otra vez lo normaliza. Por eso vive en el repo
y no fue un `sed` de una sola vez.

Dos decisiones que conviene no revertir sin pensarlo:

- **Mapea por luminosidad equivalente, no reemplazo plano.** Orca usa la escala
  teal de Material Design: un tono para el acento, más claros para hover, más
  oscuros para pressed. Cada uno va al naranja de luminosidad pareja. Un
  reemplazo plano dejaría todos los botones del mismo color y se perdería la
  sensación de que responden al mouse.
- **Busca el color en dos formas: hexadecimal y decimal.** Orca escribe algunos
  colores como `wxColour(0, 150, 136)`, que es exactamente `#009688`. La primera
  versión del script solo miraba hexadecimal y dejó pasar 79 apariciones — entre
  ellas el fondo de la pestaña activa, el elemento más visible de la interfaz.
  Si aparece otro verde suelto, revisar primero si está escrito en decimal.
- **Excluye las paletas de datos.** Las rampas tipo viridis y ColorBrewer de la
  vista térmica del G-code, los colores de filamento, la paleta del selector de
  colores y los colores de terminal de xterm.js **no son colores de marca**.
  Recolorearlas rompería la visualización o mentiría sobre el color real de un
  filamento.

---

## El cuello de botella: una hora por compilación

Medido: las dependencias (Boost, CGAL, OCCT, wxWidgets) tardan ~3 h la primera
vez y después quedan cacheadas correctamente. Pero **compilar Orca en sí lleva
más de una hora, y no hay caché de compilador** — ni `ccache` ni `sccache`, ni
en el workflow ni en los scripts de build. Cada corrida rehace las 430.000
líneas aunque hayas cambiado un solo color.

Para el re-skin da igual: es una pasada. **Para escribir el panel de IA en C++
es insostenible.** Dos caminos, a decidir cuando lleguemos ahí:

1. **Agregar `sccache` al workflow.** Funciona con MSVC y cachea objetos entre
   corridas. Un cambio chico pasaría de una hora a minutos. Archivo nuestro, sin
   tocar los del upstream.
2. **Compilar localmente.** La primera vez es larga, pero después las
   compilaciones incrementales son de segundos porque el compilador solo rehace
   lo que cambió. Requiere instalar el toolchain de C++ (Visual Studio en
   Windows, o las dependencias en WSL).

La opción 2 es claramente mejor para iterar; la 1 es menos setup.

---

## Dónde retomar

### 1. Mirar el re-skin con los ojos

**Esto no se puede verificar por CI.** Que compile no prueba que se vea bien.

Bajar el instalador de la última corrida verde en la pestaña **Actions** del
repo (`OrcaSlicer_Windows_..._x64` o la versión portable), instalarlo, y
revisar:

- Botones normales, de confirmar y de alerta, en **modo claro y oscuro**
- La barra superior y las pestañas
- El panel del AMS con una impresora conectada (el recorrido del filamento
  tiene que verse naranja)
- Los diagramas que aparecen al pasar el mouse por un parámetro
- **Que la vista térmica del G-code siga con sus colores originales** — si ahí
  salió naranja, algo se tocó de más

Si aparece algún verde suelto: agregarlo al mapa de `tools/reskin-nacod3d.py`
y volver a correr el script.

### 2. Renombrar el producto

Nombre visible, iconos y splash a "nacod3d Slicer". **Con la atribución a
OrcaSlicer en el Acerca de** (ver sección de licencia).

Ojo con el alcance: hay strings de "Orca" en localización, nombres de archivo de
configuración y rutas de datos del usuario. Cambiar la ruta de datos rompería
los perfiles de quien ya tenga Orca instalado — conviene decidirlo a conciencia.

### 3. Portar el análisis geométrico

En el repo archivado `nachorepara/nacod3d-slicer`, el archivo
`src/viewer/malla.ts` tiene la lógica ya pensada y escrita:

- Soldado de vértices con tolerancia de 1 µm — un STL repite cada vértice sin
  decir cuáles son el mismo punto, y sin soldar no se puede saber qué aristas
  comparten dos triángulos ni, por lo tanto, detectar agujeros
- Aristas abiertas (agujeros), aristas con 3+ caras, triángulos degenerados
- Normales invertidas por volumen con signo negativo
- Y los avisos redactados en términos de **qué le va a pasar a la impresión**,
  no en jerga

Es la base de las recomendaciones de IA. Orca ya tiene reparación de mallas
propia, así que **primero hay que ver qué de esto ya existe** en `libslic3r`
antes de portar nada.

### 4. Panel de IA

Decidir dónde vive dentro de la UI de Orca sin alterar lo existente. Recién
después de que el resto esté sólido.

---

## Contexto de mercado

Las piezas sueltas existen: diagnóstico por foto ([PrintFix](https://printfix.io/),
[Nozzle Doctor](https://www.nozzledoctor.com/)), detección de fallas por cámara
([Obico](https://www.obico.io/), [SimplyPrint](https://simplyprint.io/features/ai-detection)),
recomendadores web de settings, MCP servers para controlar Orca.

**Ninguna vive dentro del laminador y ninguna cierra el círculo.** El
diferencial no es una feature: es la integración y el loop de aprendizaje. En
español no hay nada.

### Costos de la capa de IA

Medido con precios de agosto 2026: **~US$0,03–0,04 por consulta** (recomendación
de pieza o análisis de fotos). US$5 de crédito ≈ 150 análisis.

Modelo pensado: **BYOK** — el usuario pone su propia API key y le paga directo
a Anthropic; costo cero para nosotros. Más adelante, una suscripción para quien
no quiera configurar nada.

Una suscripción **no** se puede usar en lugar de la API: son productos con
facturación separada y no hay puente entre ellos.

## Proyectos relacionados (separados)

- **`we-comoimprimo`** — manual público de impresión 3D. Fuente natural de
  contenido educativo para la capa de IA, pero es otro proyecto.
- **`cotizador3d`** — va en paralelo, sin dependencia.
- **`nacod3d-slicer`** — el intento con Tauri, archivado.
