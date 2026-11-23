"""Genera la imagen de una publicación de Instagram (3:4) para el AWS Student Builder Group.

Uso:
    python .claude/skills/publicaciones-aws-sbg/crear_post.py \
        --titulo "..." --fecha "..." --lugar "..."
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Falta Pillow. Instálalo con: pip install Pillow")

ANCHO = 1080
ALTO = 1440
MARGEN = 90

AZUL_OSCURO = (35, 47, 62)
NARANJA_AWS = (255, 153, 0)

CARPETA_SALIDA = Path("salida")

FUENTES_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]
FUENTES_REGULAR = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
]


def cargar_fuente(rutas, tamano):
    """Devuelve la primera fuente TTF disponible; si no hay ninguna, la fuente por defecto."""
    for ruta in rutas:
        try:
            return ImageFont.truetype(ruta, tamano)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=tamano)  # Pillow >= 10.1
    except TypeError:
        return ImageFont.load_default()


def envolver(draw, texto, fuente, ancho_max):
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = f"{actual} {palabra}".strip()
        if draw.textlength(prueba, font=fuente) <= ancho_max or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def alto_texto(draw, fuente):
    caja = draw.textbbox((0, 0), "ÁgjyÑ", font=fuente)
    return caja[3] - caja[1]


def crear_post(titulo, fecha, lugar):
    img = Image.new("RGB", (ANCHO, ALTO), AZUL_OSCURO)
    draw = ImageDraw.Draw(img)
    ancho_util = ANCHO - 2 * MARGEN

    # Encabezado
    draw.rectangle([MARGEN, MARGEN, MARGEN + 120, MARGEN + 10], fill=NARANJA_AWS)
    draw.text((MARGEN, MARGEN + 40), "AWS STUDENT BUILDER GROUP",
              font=cargar_fuente(FUENTES_BOLD, 38), fill=NARANJA_AWS)

    # Título: reduce el tamaño hasta que quepa en 5 líneas
    for tamano in range(110, 40, -6):
        f_titulo = cargar_fuente(FUENTES_BOLD, tamano)
        lineas = envolver(draw, titulo, f_titulo, ancho_util)
        if len(lineas) <= 5:
            break
    interlineado = int(alto_texto(draw, f_titulo) * 1.35)
    y = (ALTO - interlineado * len(lineas)) // 2 - 60
    for linea in lineas:
        draw.text((MARGEN, y), linea, font=f_titulo, fill=NARANJA_AWS)
        y += interlineado

    # Fecha y lugar
    f_etiqueta = cargar_fuente(FUENTES_BOLD, 28)
    f_dato = cargar_fuente(FUENTES_REGULAR, 44)
    y = ALTO - MARGEN - 260
    draw.line([(MARGEN, y), (ANCHO - MARGEN, y)], fill=NARANJA_AWS, width=3)
    y += 40
    for etiqueta, valor in (("FECHA", fecha), ("LUGAR", lugar)):
        draw.text((MARGEN, y), etiqueta, font=f_etiqueta, fill=NARANJA_AWS)
        draw.text((MARGEN, y + 36), valor, font=f_dato, fill=NARANJA_AWS)
        y += 110

    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = CARPETA_SALIDA / f"post_{marca}.png"
    img.save(ruta)
    return ruta


def main():
    parser = argparse.ArgumentParser(
        description="Genera una imagen 3:4 (1080x1440) para Instagram del AWS Student Builder Group."
    )
    parser.add_argument("--titulo", required=True, help="Título de la publicación")
    parser.add_argument("--fecha", required=True, help="Fecha del evento o publicación")
    parser.add_argument("--lugar", required=True, help="Lugar del evento")
    args = parser.parse_args()

    ruta = crear_post(args.titulo, args.fecha, args.lugar)
    print(f"Imagen generada: {ruta} ({ANCHO}x{ALTO})")


if __name__ == "__main__":
    main()
