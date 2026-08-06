# Dónde retomar

> Actualizado: 2026-08-06, antes de un viaje.
>
> Para el contexto completo: [`ESTADO.md`](ESTADO.md) ·
> [`ASISTENTE.md`](ASISTENTE.md) · [`MONETIZACION.md`](MONETIZACION.md) ·
> [`BACKLOG.md`](BACKLOG.md) · [`ENTORNO.md`](ENTORNO.md)

## Lo primero al volver

```bash
cd ~/orca-nacod3d
./build_linux.sh -d -j6      # retoma la compilación de dependencias
```

**Es resumible**: lo que ya se compiló no se rehace. Cuando termine:

```bash
./build_linux.sh -s -j6      # compila la app
```

Y para verla andando (usa WSLg, no hace falta configurar nada):

```bash
./build/src/orca-slicer
```

## Estado de las dos compilaciones

| | Estado al pausar |
|---|---|
| **Dependencias locales** (WSL) | ~665 MB compilados, 27 dependencias iniciadas, 96 marcas de completado. **Se interrumpe al apagar y se retoma sola.** |
| **CI de Windows** | Tercer intento en cola. Corre en los servidores de GitHub: **no se ve afectado por apagar la máquina.** |

Ver el resultado del CI:

```bash
gh run view 31124626416 --repo nachorepara/OrcaSlicer --json conclusion --jq .conclusion
```

Si salió verde, el instalador está en la pestaña **Actions** del repo, artefacto
`OrcaSlicer_Windows_..._x64_portable`.

### Si el CI volvió a fallar

Ya falló dos veces con *"The hosted runner lost communication with the server"* —
**es infraestructura de GitHub, no nuestro código**: compilar Orca exprime los
runners gratuitos de Windows hasta tumbarlos. La prueba es que una compilación
anterior con el mismo peso salió verde.

No relanzarlo indefinidamente. El build local es justamente la salida.

## Qué falta verificar en pantalla

Cuando haya un binario, mirar:

- [ ] **La pestaña activa en naranja.** Era teal escrito en decimal
      (`wxColour(0, 150, 136)`) y se corrigió; es lo más visible de la interfaz.
- [ ] **Dice "nacod3d Slicer"** en la ventana, y arranca con configuración limpia
      sin tocar la instalación de Orca 2.4.2 existente.
- [ ] **La atribución en el Acerca de**, sumada a la cadena que Orca ya mantiene.
- [ ] **La vista térmica del G-code con sus colores originales.** Si ahí salió
      naranja, tocamos una paleta de datos que no correspondía.

## Lo próximo a construir

En orden, y con la investigación ya hecha:

**1. Mostrar el razonamiento de la orientación.** Es la tesis del producto:
Orca calcula voladizo, casco inferior, estabilidad y contorno para cada
orientación candidata, elige la mejor y **descarta el razonamiento**. Nosotros lo
mostramos. No hay que calcular nada nuevo — está todo en
`src/libslic3r/Orient.cpp`.

**No necesita IA ni cuesta un centavo.** Es la primera función útil del asistente
y sirve como prueba de la UX antes de sumar la capa que depende de un tercero.

**2. Verificar qué falta del análisis geométrico.** Casi todo ya existe
(`TriangleMeshStats`, `Orient.cpp`). Falta confirmar si Orca calcula el espesor
mínimo de pared contra el ancho de línea, y las señales para deducir el uso de la
pieza: agujeros pasantes, roscas, relación superficie/volumen.

**3. Recién después, el panel de IA.** Con las 9 decisiones de diseño ya tomadas
en [`ASISTENTE.md`](ASISTENTE.md).

## Recordatorios

- **`ccache`**: quedó pendiente instalarlo (`sudo apt install -y ccache`).
  Acelera bastante las recompilaciones.
- **El fork viejo** `nachorepara/BambuStudio` sigue existiendo sin uso. Para
  borrarlo: `gh auth refresh -h github.com -s delete_repo` y después
  `gh repo delete nachorepara/BambuStudio --yes`.
- **El repo Tauri** `nachorepara/nacod3d-slicer` quedó archivado. Solo conserva
  valor documental.
- **Paciencia con los disparos de CI**: GitHub puede tardar ~6 minutos en
  registrar un push. Disparar a mano en el medio crea una corrida duplicada que
  después se cancela sola.
