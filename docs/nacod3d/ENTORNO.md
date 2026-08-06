# Entorno de trabajo del fork

Cómo retomar en una máquina nueva.

## Traer el repo

```bash
git clone https://github.com/nachorepara/OrcaSlicer.git orca-nacod3d
cd orca-nacod3d
git remote add upstream https://github.com/OrcaSlicer/OrcaSlicer.git
```

Son ~800 MB. El remoto `upstream` sirve para sincronizar con Orca más adelante.

## Para trabajar sin compilar

La mayor parte del trabajo hecho hasta ahora (re-skin, documentación) **no
requiere compilar nada localmente**: se edita, se pushea, y el CI compila en un
runner de Windows. Alcanza con Python 3 y git.

```bash
python3 tools/reskin-nacod3d.py            # prueba
python3 tools/reskin-nacod3d.py --aplicar  # escribe
```

## Compilar localmente (todavía no hecho)

Hace falta cuando lleguemos al panel de IA: iterar por CI cuesta **más de una
hora por vuelta**, mientras que una compilación incremental local es de
segundos.

Orca trae sus propios scripts:

| Script | Plataforma |
|---|---|
| `build_release_vs2022.bat` | Windows, Visual Studio 2022 |
| `build_linux.sh` | Linux |
| `build_release_macos.sh` | macOS |

En Windows hace falta Visual Studio 2022 con el toolchain de C++, CMake y Strawberry
Perl. La primera compilación incluye las dependencias y es larga (horas); las
siguientes son incrementales.

> Esto todavía **no se probó**. Cuando se haga, documentar acá lo que falte.

## El CI

| Workflow | Qué hace | Estado en el fork |
|---|---|---|
| `build_nacod3d.yml` | Compila **solo Windows x64** | activo — es el nuestro |
| `build_all.yml` | Siete plataformas | **desactivado**, disponible por disparo manual |

Los instaladores quedan como artefactos en la pestaña **Actions**, en la corrida
correspondiente.

Para disparar una compilación multiplataforma (release):

```bash
# hay que reactivarlo primero
ID=$(gh api repos/nachorepara/OrcaSlicer/actions/workflows \
      --jq '.workflows[] | select(.path|endswith("build_all.yml")) | .id')
gh api -X PUT "repos/nachorepara/OrcaSlicer/actions/workflows/$ID/enable"
gh workflow run build_all.yml --repo nachorepara/OrcaSlicer --ref main
```

### Tiempos medidos

| | |
|---|---|
| Dependencias, primera vez | ~3 h (después quedan cacheadas) |
| Dependencias, con caché | se saltean |
| Compilar Orca | **> 1 h, siempre** — no hay caché de compilador |

Ver la sección del cuello de botella en [`ESTADO.md`](ESTADO.md).

## Sincronizar con el upstream

Todavía no se hizo. Cuando toque:

```bash
git fetch upstream
git merge upstream/main
python3 tools/reskin-nacod3d.py --aplicar   # normaliza el teal que entró nuevo
```

Los conflictos deberían ser mínimos porque **agregamos archivos en vez de editar
los del upstream**. La excepción esperable son los archivos que el re-skin toca,
que son de ellos — ahí gana el upstream y el script vuelve a pintar.

## Cuentas y accesos

- El repo es **público** (obligado por AGPL, y además da CI ilimitado).
- `gh` tiene que estar autenticado: `gh auth status`.
- Para borrar repos hace falta el permiso extra:
  `gh auth refresh -h github.com -s delete_repo`.
