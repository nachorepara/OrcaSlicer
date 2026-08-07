# Dónde retomar

> Actualizado: 2026-08-07.
>
> Índice de todos los documentos en [`ESTADO.md`](ESTADO.md).

## Estado de las compilaciones

| | Estado |
|---|---|
| **Dependencias locales** (WSL) | ✅ **Terminadas.** 18 h 24 min, 218 componentes, 6 GB en `deps/build` |
| **App local** (WSL) | 🔨 Compilando. ~483 objetos al momento de escribir |
| **CI de Windows** | ✅ El `.exe` compila. El test que fallaba ya está arreglado (commit `c1b561fdda`), falta una corrida que lo confirme |

### Retomar la compilación local

```bash
cd ~/orca-nacod3d
./build_linux.sh -s -j6        # es incremental: no rehace lo ya compilado
./build/src/orca-slicer        # abre por WSLg, sin configurar nada
```

**`-j6` y no `-j12` a propósito:** con 12 procesos en paralelo la compilación se
come los 15 GB de RAM y muere. Es lo mismo que le pasó dos veces al runner de
GitHub (*"the hosted runner lost communication with the server"*).

### Disparar el CI

```bash
gh workflow run build_nacod3d.yml --repo nachorepara/OrcaSlicer --ref main
```

**Paciencia:** GitHub puede tardar ~6 minutos en registrar un push. Disparar a
mano en el medio crea una corrida duplicada que después se cancela sola.

---

## Lo primero al volver: abrir la app y verificar

Nada de esto se puede comprobar por CI.

- [ ] **La pestaña activa en naranja.** Era teal escrito en decimal
      (`wxColour(0, 150, 136)`), que el script no veía. Es lo más visible.
- [ ] **Dice "nacod3d Slicer"** y arranca con configuración limpia, sin tocar una
      instalación de Orca existente.
- [ ] **La atribución en el Acerca de**, sumada a la cadena que Orca mantiene.
- [ ] **La vista térmica del G-code con sus colores originales.** Si ahí salió
      naranja, tocamos una paleta de datos que no correspondía.
- [ ] **Probar el modo solapamiento**: poner el ángulo umbral de soporte en 0 y
      laminar una pieza real. Puede ser la respuesta a que el automático ponga
      soportes de más. Ver [`PERFILES-DE-OPINION.md`](PERFILES-DE-OPINION.md).

---

## Lo próximo a construir

En orden, y con la investigación hecha. **Ninguna de las tres primeras necesita
IA** — son gratis, funcionan sin internet y sirven para todos.

### 1. Mostrar el razonamiento de la orientación

La tesis del producto. Orca puntúa cada orientación candidata y **descarta el
razonamiento**. Plan de implementación completo en
[`INVESTIGACION-ORIENT.md`](INVESTIGACION-ORIENT.md) sección 1: mover
`CostItems` al `.hpp`, agregar un campo a `OrientMesh` y poblarlo antes del
`return`. Son ~20 líneas y tocan archivos del upstream.

### 2. Aviso de detalles que se imprimen más gruesos de lo diseñado

Con Arachne, un detalle de 0.15 mm sale de 0.34 — más del doble. Si había una
tolerancia o un encastre, la pieza puede no entrar y no hay forma de saberlo
antes de imprimir. Ver [`BACKLOG.md`](BACKLOG.md).

**Ojo:** hay que leer el generador de paredes efectivo del perfil cargado. La
mayoría usa clásico, no Arachne.

### 3. Resumen de «todo lo distinto al estándar»

Para cuando abrís un 3MF ajeno. Todas las piezas ya existen en Orca; falta la
pantalla. Ver [`BACKLOG.md`](BACKLOG.md).

### 4. El botón «como lo haría nacod3d»

Diseño en [`PERFILES-DE-OPINION.md`](PERFILES-DE-OPINION.md). **Bloqueado
esperando los valores de Nacho** — el mecanismo se puede construir antes, pero
sin sus números es un botón vacío.

### 5. El panel de IA

Con las 9 decisiones ya tomadas en [`ASISTENTE.md`](ASISTENTE.md).

---

## La lección más importante de la sesión

**Tres veces saqué una conclusión leyendo el código y las tres veces la realidad
la desmintió:**

| Afirmé leyendo código | La realidad |
|---|---|
| Arachne es el generador por defecto | 316 perfiles usan clásico; el default del código no es el efectivo |
| Los soportes usan Z=0.2, espaciado=0.5, XY=0.35 mm | El perfil de la CR-10 V2 usa 0.15, 0.2 y otra cosa |
| El `"60%"` se parsea como 60 mm | Se descarta y hereda 0.35 — verificado en pantalla |

**El código dice qué es posible; los perfiles y la pantalla dicen qué pasa.**

Cuando se afirme "Orca hace X", que vaya con verificación en la aplicación o con
la aclaración explícita de que es una inferencia sin confirmar. Las tres veces la
corrección vino de Nacho contrastando con años de uso real.

---

## Cabos sueltos

- **`ccache`** quedó sin instalar (`sudo apt install -y ccache`). Aceleraría las
  recompilaciones.
- **El fork viejo** `nachorepara/BambuStudio` sigue existiendo sin uso. Para
  borrarlo: `gh auth refresh -h github.com -s delete_repo` y después
  `gh repo delete nachorepara/BambuStudio --yes`.
- **El repo Tauri** `nachorepara/nacod3d-slicer` quedó archivado. Solo conserva
  valor documental; su `malla.ts` está superado por lo que Orca ya trae.
- **`per_user_temp_dir`** hardcodea la carpeta temporal `orcaslicer_<usuario>`,
  así que nuestro fork la comparte con una instalación real de Orca. Riesgo bajo,
  pero es el primer lugar donde mirar si aparece algo raro con las dos abiertas.
- **El arreglo del test** de auditoría de plugins es genérico y **le serviría al
  upstream**: se les puede ofrecer como PR.
