# Monetización

> Decidido el 2026-08-06.

## La decisión: BYOK + donaciones. Sin backend.

El usuario pone su propia API key y le paga directo al proveedor. **Costo cero
para nosotros.** Más un botón de donación (Cafecito, GitHub Sponsors) para quien
quiera reconocer el trabajo.

Nada más por ahora: sin cuentas, sin cobros, sin servidor, sin soporte de
facturación.

## Por qué así

**No hay costo que recuperar.** Con BYOK el usuario paga su propio consumo. La
pregunta de "cómo monetizo" solo aparece si algún día ofrecemos una versión donde
nosotros ponemos la key.

**Todavía no sabemos si la gente va a usar la IA.** Construir infraestructura de
cobro antes de saberlo es trabajo que puede terminar en la basura.

**La fricción de BYOK es la medición.** Si mucha gente pregunta "¿no hay una
forma más fácil?", esa es la señal de que vale la pena el tier administrado. Si
nadie pregunta, nos ahorramos meses.

## El límite que impone el AGPL

**Cualquier candado dentro del programa se puede quitar.** El código es público y
modificable: alguien compila una versión sin la verificación y la reparte.

Lo único que se puede cobrar de verdad es **el acceso a un servidor propio**. Si
la IA pasa por nuestro backend con nuestra key, ahí sí se controla quién entra.
Es el único modelo que el AGPL no puede vulnerar.

## Si algún día hay tier administrado: packs de crédito, no suscripción

Un laminador se usa a ráfagas — tres semanas seguidas y después nada por dos
meses. Pagar todos los meses por algo que se usa así se siente mal y la gente
cancela.

Los packs de crédito encajan con **cómo se usa la herramienta y con cómo es el
costo real**: nosotros pagamos por consulta, el usuario paga por consulta. Sin
compromiso mensual y psicológicamente mucho más fácil de aceptar.

## Riesgo conocido de BYOK

En impresión 3D la gente usa **IA de consumidor en el navegador, no APIs**. Pedir
que creen cuenta en una consola de desarrollador y carguen una tarjeta es una
barrera alta para ese público. Es posible que el porcentaje que configure la key
sea muy bajo.

**Eso no invalida el plan, lo pone a prueba.** Si nadie configura la key, la
conclusión no es "hagamos un backend": es que quizás **el valor del laminador no
está en la IA sino en mostrar lo que Orca esconde** — que no cuesta un centavo y
funciona para todos. Ver la tesis del producto en [`ASISTENTE.md`](ASISTENTE.md).

## El ángulo estratégico

nacod3d es un negocio de impresión 3D, y comoimprimo va a ser una plataforma de
cursos. Cada persona que instala un laminador que dice "nacod3d Slicer" en la
barra de título aprende que la marca existe, y lo abre varias veces por semana
durante años.

**Es probable que el laminador valga más como difusión que como producto.** Un
cliente que llega por haber conocido el laminador vale bastante más que unos
dólares de crédito.

Si esa lectura es correcta, la prioridad no es monetizarlo: es que sea **bueno y
que se note de quién es**.

**Condición para enlazar a comoimprimo:** que tenga contenido. Hoy está muy
verde; mandar gente ahí antes de tiempo juega en contra de la primera impresión.
Ver decisión 7 en [`ASISTENTE.md`](ASISTENTE.md).
