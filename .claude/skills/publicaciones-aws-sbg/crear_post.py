"""Genera la imagen de una publicación de Instagram para el AWS Student Builder Group.

Uso:
    python .claude/skills/publicaciones-aws-sbg/crear_post.py \
        --titulo "..." --fecha "..." --lugar "..." [--tipo "..."] [--salida salida]
"""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Falta Pillow. Instálalo con: pip install Pillow")

ANCHO, ALTO = 1080, 1440
MARGEN = 90

FONDO_ARRIBA = (35, 47, 62)    # azul marino
FONDO_ABAJO = (15, 22, 32)
NARANJA = (255, 153, 0)
BLANCO = (255, 255, 255)
GRIS = (200, 208, 218)

FUENTES_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]
FUENTES_REGULAR = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
]


def fuente(rutas, tamano):
    for ruta in rutas:
        if Path(ruta).exists():
            return ImageFont.truetype(ruta, tamano)
    return ImageFont.load_default(size=tamano)


def envolver(draw, texto, font, ancho_max):
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = f"{actual} {palabra}".strip()
        if draw.textlength(prueba, font=font) <= ancho_max:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def slug(texto):
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-") or "post"


def crear_post(titulo, fecha, lugar, tipo, carpeta):
    img = Image.new("RGB", (ANCHO, ALTO))
    draw = ImageDraw.Draw(img)

    # Fondo degradado vertical
    for y in range(ALTO):
        t = y / ALTO
        color = tuple(int(a + (b - a) * t) for a, b in zip(FONDO_ARRIBA, FONDO_ABAJO))
        draw.line([(0, y), (ANCHO, y)], fill=color)

    ancho_util = ANCHO - 2 * MARGEN

    # Encabezado
    draw.rectangle([MARGEN, MARGEN, MARGEN + 120, MARGEN + 10], fill=NARANJA)
    draw.text((MARGEN, MARGEN + 40), "AWS STUDENT BUILDER GROUP",
              font=fuente(FUENTES_BOLD, 38), fill=BLANCO)
    if tipo:
        draw.text((MARGEN, MARGEN + 100), tipo.upper(),
                  font=fuente(FUENTES_REGULAR, 32), fill=NARANJA)

    # Título: reduce el tamaño hasta que quepa en 5 líneas
    for tamano in range(110, 40, -6):
        f_titulo = fuente(FUENTES_BOLD, tamano)
        lineas = envolver(draw, titulo, f_titulo, ancho_util)
        if len(lineas) <= 5:
            break
    alto_linea = int(tamano * 1.2)
    y = (ALTO - alto_linea * len(lineas)) // 2 - 60
    for linea in lineas:
        draw.text((MARGEN, y), linea, font=f_titulo, fill=BLANCO)
        y += alto_linea

    # Fecha y lugar
    f_dato = fuente(FUENTES_REGULAR, 44)
    f_etq = fuente(FUENTES_BOLD, 28)
    y = ALTO - MARGEN - 260
    draw.line([(MARGEN, y), (ANCHO - MARGEN, y)], fill=NARANJA, width=3)
    y += 40
    for etiqueta, valor in (("FECHA", fecha), ("LUGAR", lugar)):
        draw.text((MARGEN, y), etiqueta, font=f_etq, fill=NARANJA)
        draw.text((MARGEN, y + 36), valor, font=f_dato, fill=GRIS)
        y += 110

    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{slug(titulo)}.png"
    img.save(ruta)
    return ruta


def main():
    p = argparse.ArgumentParser(description="Genera una imagen de 1080x1440 para Instagram.")
    p.add_argument("--titulo", required=True)
    p.add_argument("--fecha", required=True)
    p.add_argument("--lugar", required=True)
    p.add_argument("--tipo", default="", help="Ej.: Anuncio de evento, Tutorial")
    p.add_argument("--salida", default="salida", help="Carpeta de salida (por defecto: salida)")
    a = p.parse_args()

    ruta = crear_post(a.titulo, a.fecha, a.lugar, a.tipo, a.salida)
    print(f"Imagen generada: {ruta} ({ANCHO}x{ALTO})")


if __name__ == "__main__":
    main()
