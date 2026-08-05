#!/usr/bin/env python3
"""Cambia el acento teal de OrcaSlicer por el naranja de nacod3d.

Este script es **re-ejecutable a propósito**: cada vez que sincronicemos con el
upstream van a entrar colores teal nuevos en el código nuevo. Correrlo de nuevo
los normaliza. Por eso vive en el repo y no fue un `sed` de una sola vez.

Uso:
    python3 tools/reskin-nacod3d.py                 # prueba: dice qué haría
    python3 tools/reskin-nacod3d.py --aplicar       # escribe los cambios
    python3 tools/reskin-nacod3d.py --grupos 1,2    # solo algunos grupos

Grupos:
    1  código C++ de la interfaz      (botones, pestañas, barras)
    2  vistas web embebidas           (CSS/HTML de los diálogos)
    3  iconos de la interfaz          (SVG)
    4  diagramas de parámetros        (SVG, se ven al pasar el mouse)
    5  gráficos del AMS y spool       (SVG del panel de filamento)

En todos los casos el teal cumple la misma función: es el acento que resalta el
sujeto, sobre una estructura gris. En `ext_image_*.svg`, por ejemplo, el gris es
el cuerpo de la impresora y el teal dibuja el recorrido del filamento. Por eso
se recolorean todos: mantener el lenguaje visual es justamente lo que hace que
siga pareciendo Orca.
"""

from __future__ import annotations

import argparse
import collections
import os
import sys

# ---------------------------------------------------------------------------
# Mapa de colores.
#
# Orca usa la escala teal de Material Design. Mapeamos cada tono al naranja de
# nacod3d de luminosidad equivalente (escala orange de Tailwind, de donde sale
# nuestro #EA580C), para que los estados hover/pressed conserven la misma
# relación de contraste que tenían.
# ---------------------------------------------------------------------------
MAPA = {
    # acento principal y sus casi-duplicados (erratas del upstream)
    "009688": "EA580C",  # teal 500  -> orange 600  (el acento)
    "009687": "EA580C",
    "009789": "EA580C",
    # más claros: hover, resaltados
    "26A69A": "F97316",  # teal 400  -> orange 500
    "4DB6AC": "FB923C",  # teal 300  -> orange 400
    "52C7B8": "FB923C",
    "22BFB0": "FB923C",
    "02C7B3": "FB923C",
    "00C1AE": "FB923C",
    "00DFC4": "FDBA74",  # teal brillante -> orange 300
    "00F0D8": "FDBA74",
    "8DE5D6": "FDBA74",
    "5EEAD4": "FDBA74",
    # Cianes muy brillantes que Orca usa como acento sobre fondo oscuro:
    # el segundo valor del par de modo oscuro en btn_confirm (Button.cpp), y
    # los enlaces y el botón de descarga de la vista de inicio (home.css).
    "00FFD4": "FDBA74",
    "00FFEA": "FDBA74",
    "00FFD9": "FDBA74",
    # más oscuros: pressed, bordes
    "00897B": "C2410C",  # teal 600  -> orange 700
    "008172": "C2410C",
    "00675B": "9A3412",  # teal 800  -> orange 800
}

EXTENSIONES = (".cpp", ".hpp", ".h", ".css", ".svg", ".json", ".js", ".html", ".ini")

# Rutas que NO se tocan: paletas de datos, no colores de marca.
#
# Orca usa rampas tipo viridis y ColorBrewer para la vista térmica del G-code y
# para los colores de filamento. Recolorearlas rompería la visualización.
EXCLUIR = (
    "src/slic3r/Utils/ColorMap",
    "resources/color_map",
    "/thirdparty/",
    "/deps/",
)


def grupo_de(ruta: str) -> int:
    """Clasifica un archivo según cuánto se ve su color en el uso diario."""
    p = ruta.replace("\\", "/")
    nombre = os.path.basename(p)
    if p.startswith("src/"):
        return 1
    if "/web/" in p:
        return 2
    if nombre.startswith("ext_image"):
        return 5
    if nombre.startswith("param_"):
        return 4
    return 3


def reemplazar(texto: str) -> tuple[str, int]:
    """Aplica el mapa respetando mayúsculas/minúsculas y prefijo (# o 0x)."""
    total = 0
    for viejo, nuevo in MAPA.items():
        for v, n in ((viejo.upper(), nuevo.upper()), (viejo.lower(), nuevo.lower())):
            for prefijo in ("#", "0x", "0X"):
                objetivo = prefijo + v
                cuantos = texto.count(objetivo)
                if cuantos:
                    texto = texto.replace(objetivo, prefijo + n)
                    total += cuantos
    return texto, total


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--aplicar", action="store_true", help="escribe los cambios")
    ap.add_argument(
        "--grupos",
        default="1,2,3,4,5",
        help="grupos a procesar, separados por coma (por defecto todos)",
    )
    args = ap.parse_args()
    grupos = {int(g) for g in args.grupos.split(",") if g.strip()}

    por_grupo: collections.Counter[int] = collections.Counter()
    archivos_grupo: collections.Counter[int] = collections.Counter()
    tocados: list[tuple[str, int]] = []

    for base in ("src", "resources"):
        for dp, _, fs in os.walk(base):
            for f in fs:
                if not f.endswith(EXTENSIONES):
                    continue
                ruta = os.path.join(dp, f)
                if any(x in ruta.replace("\\", "/") for x in EXCLUIR):
                    continue
                g = grupo_de(ruta)
                if g not in grupos:
                    continue
                try:
                    with open(ruta, encoding="utf-8", errors="surrogateescape") as fh:
                        original = fh.read()
                except OSError:
                    continue
                nuevo, n = reemplazar(original)
                if n == 0:
                    continue
                por_grupo[g] += n
                archivos_grupo[g] += 1
                tocados.append((ruta, n))
                if args.aplicar:
                    with open(ruta, "w", encoding="utf-8", errors="surrogateescape") as fh:
                        fh.write(nuevo)

    etiquetas = {
        1: "código C++ de la interfaz",
        2: "vistas web embebidas",
        3: "iconos de la interfaz",
        4: "diagramas de parámetros",
        5: "gráficos del AMS y spool",
    }
    modo = "APLICADO" if args.aplicar else "PRUEBA (no se escribió nada)"
    print(f"=== re-skin nacod3d — {modo} ===\n")
    for g in sorted(por_grupo):
        print(f"  grupo {g}  {etiquetas[g]:32s} {por_grupo[g]:>6d} cambios en {archivos_grupo[g]:>4d} archivos")
    print(f"\n  TOTAL: {sum(por_grupo.values())} cambios en {len(tocados)} archivos")

    if not args.aplicar:
        print("\n  Los 10 archivos con más cambios:")
        for ruta, n in sorted(tocados, key=lambda t: -t[1])[:10]:
            print(f"    {n:4d}  {ruta}")
        print("\n  Para aplicar: python3 tools/reskin-nacod3d.py --aplicar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
