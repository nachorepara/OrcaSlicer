#!/usr/bin/env python3
"""Recolorea el acento teal dentro de imágenes PNG.

El script principal (`reskin-nacod3d.py`) sólo toca archivos de texto: código,
CSS y SVG. Algunos logos son PNG, que es binario, y quedaban con el teal
original — el más visible es el del asistente de bienvenida.

Uso:
    python3 tools/reskin-png.py                # prueba
    python3 tools/reskin-png.py --aplicar
"""
from __future__ import annotations

import argparse
import glob
import struct
import sys
import zlib

# Mismo criterio que el script de texto: mapear por luminosidad equivalente.
MAPA = {
    (0, 150, 136): (234, 88, 12),
    (0, 151, 137): (234, 88, 12),
    (0, 150, 135): (234, 88, 12),
    (38, 166, 154): (249, 115, 22),
    (0, 137, 123): (194, 65, 12),
    (0, 103, 91): (154, 52, 18),
}
# Tolerancia baja a propósito. Con 60 el escaneo tocaba un millón de píxeles en
# 75 imágenes, muchas de ellas fotos de piezas y renders de impresoras donde el
# verdoso es contenido real, no marca. Con 25 se captura el 97% del logo y los
# falsos positivos desaparecen.
TOLERANCIA = 25

# Sólo imágenes de marca. El resto de resources/images son fotos de calibración,
# miniaturas de impresoras y diagramas: ahí un tono verdoso es contenido, no
# acento, y recolorearlo sería mentir sobre lo que muestran.
ARCHIVOS = (
    "resources/web/image/logo.png",
    "resources/images/OrcaSlicer.png",
    "resources/images/OrcaSlicer_192px.png",
    "resources/images/OrcaSlicer_128px.png",
    "resources/images/OrcaSlicer_64.png",
    "resources/images/OrcaSlicer_154.png",
    "resources/images/OrcaSlicerTitle.png",
    "resources/images/OrcaSlicer_154_title.png",
)


def _cerca(px, ref):
    return sum((a - b) ** 2 for a, b in zip(px, ref)) ** 0.5 <= TOLERANCIA


def _sin_filtros(raw: bytes, w: int, h: int, ch: int) -> bytearray:
    """Deshace los filtros por línea del PNG."""
    out = bytearray()
    stride = w * ch
    prev = bytearray(stride)
    i = 0
    for _ in range(h):
        f = raw[i]; i += 1
        line = bytearray(raw[i:i + stride]); i += stride
        for x in range(stride):
            a = line[x - ch] if x >= ch else 0
            b = prev[x]
            c = prev[x - ch] if x >= ch else 0
            if f == 1:   line[x] = (line[x] + a) & 0xFF
            elif f == 2: line[x] = (line[x] + b) & 0xFF
            elif f == 3: line[x] = (line[x] + (a + b) // 2) & 0xFF
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 0xFF
        out += line
        prev = line
    return out


def procesar(path: str, aplicar: bool) -> int:
    d = open(path, "rb").read()
    if d[:8] != b"\x89PNG\r\n\x1a\n":
        return 0
    w, h = struct.unpack(">II", d[16:24])
    bd, ct = d[24], d[25]
    if bd != 8 or ct not in (2, 6):     # sólo RGB/RGBA de 8 bits
        return 0
    ch = 3 if ct == 2 else 4

    idat = b""; otros = []
    i = 8
    while i < len(d):
        ln = struct.unpack(">I", d[i:i + 4])[0]
        tag = d[i + 4:i + 8]
        if tag == b"IDAT":
            idat += d[i + 8:i + 8 + ln]
        elif tag not in (b"IEND",):
            otros.append((tag, d[i + 8:i + 8 + ln]))
        i += 12 + ln

    px = _sin_filtros(zlib.decompress(idat), w, h, ch)

    cambios = 0
    for o in range(0, len(px), ch):
        actual = (px[o], px[o + 1], px[o + 2])
        for viejo, nuevo in MAPA.items():
            if _cerca(actual, viejo):
                # Conservar la diferencia de luminosidad del píxel respecto del
                # color base, para no aplanar los bordes suavizados.
                delta = [actual[k] - viejo[k] for k in range(3)]
                for k in range(3):
                    px[o + k] = max(0, min(255, nuevo[k] + delta[k]))
                cambios += 1
                break

    if cambios and aplicar:
        crudo = bytearray()
        stride = w * ch
        for y in range(h):
            crudo += b"\x00" + px[y * stride:(y + 1) * stride]

        def chunk(tag, data):
            c = tag + data
            return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

        salida = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", d[16:29])
        for tag, data in otros:
            if tag != b"IHDR":
                salida += chunk(tag, data)
        salida += chunk(b"IDAT", zlib.compress(bytes(crudo), 9)) + chunk(b"IEND", b"")
        open(path, "wb").write(salida)
    return cambios


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--aplicar", action="store_true")
    args = ap.parse_args()

    total = 0; tocados = []
    for f in ARCHIVOS:
        if True:
            try:
                n = procesar(f, args.aplicar)
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"  (omitido {f}: {e})")
                continue
            if n:
                total += n; tocados.append((f, n))

    modo = "APLICADO" if args.aplicar else "PRUEBA (no se escribió nada)"
    print(f"=== re-skin de PNG — {modo} ===\n")
    for f, n in sorted(tocados, key=lambda t: -t[1]):
        print(f"  {n:>7,} píxeles  {f}")
    print(f"\n  TOTAL: {total:,} píxeles en {len(tocados)} imágenes")
    if not args.aplicar and tocados:
        print("\n  Para aplicar: python3 tools/reskin-png.py --aplicar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
