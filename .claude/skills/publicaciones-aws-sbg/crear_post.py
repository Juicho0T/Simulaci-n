"""Genera la imagen de una publicación de Instagram (3:4) para el AWS Student Builder Group.

Uso:
    python .claude/skills/publicaciones-aws-sbg/crear_post.py \
        --titulo "..." --fecha "..." --lugar "..." [--tipo anuncio] [--estilo orbitas] [--logo ruta.png]

Tipos:   anuncio, resultado, taller, tutorial (cambia la etiqueta y el estilo por defecto).
Estilos: orbitas, circuito, bloques, terminal (las decoraciones varían en cada ejecución).
Logo:    por defecto usa assets/logo.png junto a este script.
"""

import argparse
import math
import random
import sys
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
except ImportError:
    sys.exit("Falta Pillow. Instálalo con: pip install Pillow")

ANCHO = 1080
ALTO = 1440
ESCALA = 2  # se dibuja al doble de tamaño y se reduce al final para suavizar bordes
MARGEN = 90

# Paleta del grupo
FONDO = (21, 28, 38)           # #151C26
FONDO_PROFUNDO = (12, 16, 23)
LINEA = (42, 48, 58)           # líneas de la cuadrícula
LINEA_CLARA = (61, 68, 78)
ACENTO = (174, 92, 255)        # morado #AE5CFF
ACENTO_CLARO = (212, 170, 255)
ACENTO_MEDIO = (136, 68, 212)
ACENTO_SOMBRA = (92, 44, 150)
BLANCO = (255, 255, 255)
GRIS = (165, 175, 190)
VERDE = (110, 210, 150)

CELDA = 60  # tamaño de la cuadrícula del fondo

CARPETA_SALIDA = Path("salida")
LOGO_POR_DEFECTO = Path(__file__).resolve().parent / "assets" / "logo.png"

TIPOS = {
    "anuncio": ("PRÓXIMO EVENTO", "orbitas"),
    "resultado": ("ASÍ LO VIVIMOS", "bloques"),
    "taller": ("RESUMEN DE TALLER", "circuito"),
    "tutorial": ("TUTORIAL", "terminal"),
}
ESTILOS = ("orbitas", "circuito", "bloques", "terminal")

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
FUENTES_MONO = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
    "/System/Library/Fonts/Menlo.ttc",
    "C:/Windows/Fonts/consolab.ttf",
] + FUENTES_BOLD


# --------------------------------------------------------------------------- utilidades

def s(valor):
    """Convierte una medida del lienzo final (1080x1440) a la del lienzo de trabajo."""
    return int(round(valor * ESCALA))


def caja(cx, cy, r):
    return [s(cx - r), s(cy - r), s(cx + r), s(cy + r)]


def cargar_fuente(rutas, tamano):
    """Primera fuente TTF disponible; si no hay ninguna, la fuente por defecto de Pillow."""
    for ruta in rutas:
        try:
            return ImageFont.truetype(ruta, s(tamano))
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=s(tamano))  # Pillow >= 10.1
    except TypeError:
        return ImageFont.load_default()


def escribir(d, xy, texto, fuente, color, anchor="la"):
    """Dibuja texto; si la fuente no admite 'anchor' (fuente bitmap antigua), lo calcula a mano."""
    try:
        d.text(xy, texto, font=fuente, fill=color, anchor=anchor)
    except (ValueError, TypeError):
        x, y = xy
        izq, arr, der, aba = d.textbbox((0, 0), texto, font=fuente)
        if anchor[0] == "m":
            x -= (der - izq) / 2
        elif anchor[0] == "r":
            x -= der - izq
        if anchor[1] == "m":
            y -= (aba - arr) / 2
        d.text((x, y), texto, font=fuente, fill=color)


def ancho_texto(d, texto, fuente):
    return d.textlength(texto, font=fuente) / ESCALA


def envolver(d, texto, fuente, ancho_max):
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = f"{actual} {palabra}".strip()
        if ancho_texto(d, prueba, fuente) <= ancho_max or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def ajustar(d, texto, rutas, ancho_max, alto_max, inicio=120, minimo=40, max_lineas=5, interlineado=1.12):
    """Busca el tamaño de letra más grande con el que el texto cabe en la caja dada."""
    for tam in range(inicio, minimo - 1, -4):
        fuente = cargar_fuente(rutas, tam)
        lineas = envolver(d, texto, fuente, ancho_max)
        if len(lineas) <= max_lineas and tam * interlineado * len(lineas) <= alto_max:
            break
    return fuente, lineas, tam * interlineado


# --------------------------------------------------------------------------- fondo

def fondo():
    img = Image.new("RGB", (s(ANCHO), s(ALTO)))  # RGB: así ImageDraw mezcla colores con transparencia
    d = ImageDraw.Draw(img)
    alto = s(ALTO)
    for y in range(alto):
        t = y / alto
        color = tuple(int(a + (b - a) * t) for a, b in zip(FONDO, FONDO_PROFUNDO))
        d.line([(0, y), (s(ANCHO), y)], fill=color)
    return img


def brillo(img, cx, cy, radio, intensidad):
    mascara = Image.new("L", img.size, 0)
    ImageDraw.Draw(mascara).ellipse(caja(cx, cy, radio), fill=intensidad)
    mascara = mascara.filter(ImageFilter.GaussianBlur(s(radio * 0.45)))
    img.paste(Image.new("RGB", img.size, ACENTO), (0, 0), mascara)


def cuadricula(d, rnd):
    """Cuadrícula de líneas con algunas celdas encendidas en morado."""
    columnas, filas = ANCHO // CELDA + 1, ALTO // CELDA + 1
    celdas = rnd.sample([(c, f) for c in range(columnas) for f in range(filas)], 7)
    for c, f in celdas:
        alfa = rnd.choice((28, 40, 55, 75))
        d.rectangle([s(c * CELDA), s(f * CELDA), s((c + 1) * CELDA), s((f + 1) * CELDA)], fill=ACENTO + (alfa,))
    for x in range(0, ANCHO + 1, CELDA):
        d.line([(s(x), 0), (s(x), s(ALTO))], fill=LINEA + (200,), width=s(1))
    for y in range(0, ALTO + 1, CELDA):
        d.line([(0, s(y)), (s(ANCHO), s(y))], fill=LINEA + (200,), width=s(1))


# --------------------------------------------------------------------------- decoraciones

def deco_orbitas(d, rnd):
    cx, cy = ANCHO - 80, 300
    for i, r in enumerate((100, 165, 235, 305)):
        d.ellipse(caja(cx, cy, r), outline=ACENTO + (170 - i * 30,), width=s(3))
        angulo = rnd.uniform(math.pi * 0.55, math.pi * 1.45)
        px, py = cx + r * math.cos(angulo), cy + r * math.sin(angulo)
        d.ellipse(caja(px, py, rnd.choice((7, 10, 13))), fill=ACENTO_CLARO + (235,))
    d.ellipse(caja(cx, cy, 56), fill=ACENTO)
    d.ellipse(caja(cx - 18, cy - 18, 16), fill=ACENTO_CLARO + (200,))


def deco_circuito(d, rnd):
    for _ in range(8):
        x, y = ANCHO + 20, rnd.randint(190, 410)
        puntos_linea = [(x, y)]
        for _ in range(rnd.randint(2, 3)):
            x -= rnd.randint(70, 160)
            puntos_linea.append((x, y))
            y = min(420, max(180, y + rnd.choice((-1, 1)) * rnd.randint(30, 90)))
            puntos_linea.append((x, y))
        alfa = rnd.randint(120, 230)
        d.line([(s(a), s(b)) for a, b in puntos_linea], fill=ACENTO + (alfa,), width=s(4), joint="curve")
        fx, fy = puntos_linea[-1]
        d.ellipse(caja(fx, fy, 10), fill=FONDO_PROFUNDO, outline=ACENTO + (alfa,), width=s(4))
    chip = [s(ANCHO - 250), s(250), s(ANCHO - 130), s(370)]
    d.rounded_rectangle(chip, radius=s(14), fill=ACENTO)
    d.rounded_rectangle([chip[0] + s(22), chip[1] + s(22), chip[2] - s(22), chip[3] - s(22)],
                        radius=s(8), outline=FONDO_PROFUNDO, width=s(4))


def cubo(d, cx, cy, a, solido):
    k = 0.866 * a
    arriba = [(cx, cy - a), (cx + k, cy - a / 2), (cx, cy), (cx - k, cy - a / 2)]
    izquierda = [(cx - k, cy - a / 2), (cx, cy), (cx, cy + a), (cx - k, cy + a / 2)]
    derecha = [(cx, cy), (cx + k, cy - a / 2), (cx + k, cy + a / 2), (cx, cy + a)]
    for cara, color in ((arriba, ACENTO_CLARO), (izquierda, ACENTO), (derecha, ACENTO_SOMBRA)):
        puntos_cara = [(s(x), s(y)) for x, y in cara]
        if solido:
            d.polygon(puntos_cara, fill=color)
        else:
            d.polygon(puntos_cara, fill=FONDO + (170,), outline=ACENTO + (210,), width=s(3))


def deco_bloques(d, rnd):
    a, cx, cy = 62, ANCHO - 170, 270
    bloques = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0), (2, 0, 0), (0, 2, 0), (0, 0, 1), (1, 0, 1)]
    rnd.shuffle(bloques)
    elegidos = sorted(bloques[: rnd.randint(5, 8)], key=lambda b: (b[2], b[0] + b[1]))
    for i, j, k in elegidos:
        x = cx + (i - j) * 0.866 * a
        y = cy + (i + j) * 0.5 * a - k * a
        cubo(d, x, y, a, solido=rnd.random() > 0.3)
    for _ in range(3):
        cubo(d, rnd.randint(600, 740), rnd.randint(310, 400), rnd.randint(16, 26), solido=False)


DECORACIONES = {"orbitas": deco_orbitas, "circuito": deco_circuito, "bloques": deco_bloques}


# --------------------------------------------------------------------------- bloques de contenido

def pegar_logo(img, ruta_logo, x, y, lado):
    """Pega el logo (con su transparencia) centrado en un cuadro de 'lado' px. False si no se pudo cargar."""
    try:
        logo = Image.open(ruta_logo).convert("RGBA")
    except (OSError, ValueError):
        return False
    logo = ImageOps.contain(logo, (s(lado), s(lado)), method=getattr(Image, "Resampling", Image).LANCZOS)
    px = s(x) + (s(lado) - logo.size[0]) // 2
    py = s(y) + (s(lado) - logo.size[1]) // 2
    img.paste(logo.convert("RGB"), (px, py), logo.getchannel("A"))
    return True


def marca_sin_logo(d, x, y, lado):
    """Hexágono con </> para cuando no hay logo disponible."""
    cx, cy, r = x + lado / 2, y + lado / 2, lado / 2
    hexagono = [(s(cx + r * math.cos(math.pi / 6 + n * math.pi / 3)),
                 s(cy + r * math.sin(math.pi / 6 + n * math.pi / 3))) for n in range(6)]
    d.polygon(hexagono, fill=ACENTO)
    escribir(d, (s(cx), s(cy)), "</>", cargar_fuente(FUENTES_MONO, int(lado * 0.3)), FONDO_PROFUNDO, "mm")


def encabezado(img, d, etiqueta, ruta_logo):
    lx, ly, lado = MARGEN, 72, 122
    if not (ruta_logo and pegar_logo(img, ruta_logo, lx, ly, lado)):
        marca_sin_logo(d, lx, ly, lado)
    tx = lx + lado + 30
    escribir(d, (s(tx), s(ly + 34)), "AWS STUDENT BUILDER GROUP", cargar_fuente(FUENTES_BOLD, 30), BLANCO, "lm")

    fuente = cargar_fuente(FUENTES_BOLD, 24)
    y, alto, relleno = ly + 72, 50, 24
    ancho = ancho_texto(d, etiqueta, fuente) + 2 * relleno
    d.rounded_rectangle([s(tx), s(y), s(tx + ancho), s(y + alto)], radius=s(alto / 2), fill=ACENTO)
    escribir(d, (s(tx + relleno), s(y + alto / 2)), etiqueta, fuente, FONDO_PROFUNDO, "lm")


def titulo_poster(d, texto, y0=440, y1=1040):
    ancho = ANCHO - 2 * MARGEN
    fuente, lineas, inter = ajustar(d, texto, FUENTES_BOLD, ancho - 30, y1 - y0)
    y = y0 + (y1 - y0 - inter * len(lineas)) / 2
    for n, linea in enumerate(lineas):
        ultima = n == len(lineas) - 1
        if ultima and len(lineas) > 1:
            # Efecto marcador: la última línea va sobre una franja de color.
            izq, arr, der, aba = d.textbbox((s(MARGEN + 14), s(y)), linea, font=fuente)
            d.rounded_rectangle([izq - s(14), arr - s(10), der + s(14), aba + s(14)], radius=s(10), fill=ACENTO)
            escribir(d, (s(MARGEN + 14), s(y)), linea, fuente, FONDO_PROFUNDO)
        else:
            escribir(d, (s(MARGEN), s(y)), linea, fuente, BLANCO)
        y += inter
    if len(lineas) == 1:
        d.rounded_rectangle([s(MARGEN), s(y + 16), s(MARGEN + 160), s(y + 30)], radius=s(7), fill=ACENTO)


def titulo_terminal(d, texto, y0=320, y1=1030):
    x0, x1 = MARGEN, ANCHO - MARGEN - 16
    d.rounded_rectangle([s(x0 + 16), s(y0 + 16), s(x1 + 16), s(y1 + 16)], radius=s(22), fill=ACENTO)
    d.rounded_rectangle([s(x0), s(y0), s(x1), s(y1)], radius=s(22), fill=FONDO_PROFUNDO, outline=LINEA_CLARA, width=s(2))
    barra = (36, 44, 56)
    d.rounded_rectangle([s(x0), s(y0), s(x1), s(y0 + 58)], radius=s(22), fill=barra)
    d.rectangle([s(x0), s(y0 + 30), s(x1), s(y0 + 58)], fill=barra)
    for n, color in enumerate((ACENTO, ACENTO_CLARO, GRIS)):
        d.ellipse(caja(x0 + 36 + n * 30, y0 + 29, 9), fill=color)
    escribir(d, (s((x0 + x1) / 2), s(y0 + 29)), "sbg@cloud: ~", cargar_fuente(FUENTES_MONO, 20), GRIS, "mm")

    mono = cargar_fuente(FUENTES_MONO, 26)
    escribir(d, (s(x0 + 40), s(y0 + 100)), "$ sbg crear --post", mono, ACENTO)

    fuente, lineas, inter = ajustar(d, texto, FUENTES_MONO, x1 - x0 - 140, y1 - y0 - 260,
                                    inicio=96, minimo=36, max_lineas=6, interlineado=1.2)
    y = y0 + 170
    for linea in lineas:
        escribir(d, (s(x0 + 40), s(y)), linea, fuente, BLANCO)
        y += inter
    cx = x0 + 40 + ancho_texto(d, lineas[-1] + " ", fuente)
    d.rectangle([s(cx), s(y - inter + 8), s(cx + inter * 0.45), s(y - inter * 0.18)], fill=ACENTO)
    escribir(d, (s(x0 + 40), s(y1 - 60)), "[ok] listo para compartir", cargar_fuente(FUENTES_MONO, 22), VERDE)


def icono_calendario(d, cx, cy):
    d.rounded_rectangle([s(cx - 22), s(cy - 16), s(cx + 22), s(cy + 24)], radius=s(5), outline=FONDO_PROFUNDO, width=s(4))
    d.rectangle([s(cx - 22), s(cy - 16), s(cx + 22), s(cy - 4)], fill=FONDO_PROFUNDO)
    for dx in (-11, 11):
        d.rounded_rectangle([s(cx + dx - 3), s(cy - 25), s(cx + dx + 3), s(cy - 10)], radius=s(3), fill=FONDO_PROFUNDO)
    for dx in (-10, 0, 10):
        d.rectangle([s(cx + dx - 3), s(cy + 6), s(cx + dx + 3), s(cy + 12)], fill=FONDO_PROFUNDO)


def icono_ubicacion(d, cx, cy):
    d.ellipse(caja(cx, cy - 8, 18), fill=FONDO_PROFUNDO)
    d.polygon([(s(cx - 15), s(cy + 2)), (s(cx + 15), s(cy + 2)), (s(cx), s(cy + 28))], fill=FONDO_PROFUNDO)
    d.ellipse(caja(cx, cy - 8, 7), fill=ACENTO)


def tarjeta(d, y, etiqueta, valor, icono):
    x0, x1, alto = MARGEN, ANCHO - MARGEN, 120
    d.rounded_rectangle([s(x0), s(y), s(x1), s(y + alto)], radius=s(24),
                        fill=FONDO + (215,), outline=ACENTO + (110,), width=s(2))
    d.rounded_rectangle([s(x0 + 20), s(y + 20), s(x0 + 100), s(y + 100)], radius=s(18), fill=ACENTO)
    icono(d, x0 + 60, y + 60)
    tx = x0 + 128
    escribir(d, (s(tx), s(y + 28)), etiqueta, cargar_fuente(FUENTES_BOLD, 21), ACENTO_CLARO)
    for tam in range(40, 21, -2):
        fuente = cargar_fuente(FUENTES_REGULAR, tam)
        if ancho_texto(d, valor, fuente) <= x1 - tx - 24:
            break
    escribir(d, (s(tx), s(y + 58)), valor, fuente, BLANCO)


def pie(d):
    fuente = cargar_fuente(FUENTES_REGULAR, 21)
    escribir(d, (s(MARGEN), s(1394)), "#AWSCommunity", fuente, GRIS, "lm")
    escribir(d, (s(ANCHO - MARGEN), s(1394)), "#StudentBuilderGroup", fuente, GRIS, "rm")
    d.rounded_rectangle([s(ANCHO / 2 - 40), s(1390), s(ANCHO / 2 + 40), s(1398)], radius=s(4), fill=ACENTO)


# --------------------------------------------------------------------------- principal

def crear_post(titulo, fecha, lugar, tipo="anuncio", estilo=None, ruta_logo=LOGO_POR_DEFECTO):
    etiqueta, estilo_por_defecto = TIPOS[tipo]
    estilo = estilo or estilo_por_defecto
    rnd = random.Random()

    img = fondo()
    brillo(img, ANCHO - 60, 160, 400, 60)
    brillo(img, 40, ALTO - 300, 260, 28)
    d = ImageDraw.Draw(img, "RGBA")
    cuadricula(d, rnd)
    if estilo in DECORACIONES:
        DECORACIONES[estilo](d, rnd)

    encabezado(img, d, etiqueta, ruta_logo)
    if estilo == "terminal":
        titulo_terminal(d, titulo)
    else:
        titulo_poster(d, titulo)
    tarjeta(d, 1080, "FECHA", fecha, icono_calendario)
    tarjeta(d, 1220, "LUGAR", lugar, icono_ubicacion)
    pie(d)

    lanczos = getattr(Image, "Resampling", Image).LANCZOS
    final = img.resize((ANCHO, ALTO), lanczos)

    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = CARPETA_SALIDA / f"post_{marca}.png"
    n = 2
    while ruta.exists():
        ruta = CARPETA_SALIDA / f"post_{marca}_{n}.png"
        n += 1
    final.save(ruta)
    return ruta


def main():
    parser = argparse.ArgumentParser(
        description="Genera una imagen 3:4 (1080x1440) para Instagram del AWS Student Builder Group."
    )
    parser.add_argument("--titulo", required=True, help="Título de la publicación")
    parser.add_argument("--fecha", required=True, help="Fecha del evento o publicación")
    parser.add_argument("--lugar", required=True, help="Lugar del evento")
    parser.add_argument("--tipo", choices=TIPOS, default="anuncio",
                        help="Tipo de publicación (define la etiqueta y el estilo por defecto)")
    parser.add_argument("--estilo", choices=ESTILOS, help="Estilo visual; si se omite, se usa el del tipo")
    parser.add_argument("--logo", type=Path, default=LOGO_POR_DEFECTO,
                        help="Imagen del logo (por defecto, assets/logo.png junto al script)")
    args = parser.parse_args()

    if not args.logo.exists():
        print(f"Aviso: no se encontró el logo en {args.logo}; se usará una marca genérica.", file=sys.stderr)
    ruta = crear_post(args.titulo, args.fecha, args.lugar, args.tipo, args.estilo, args.logo)
    print(f"Imagen generada: {ruta} ({ANCHO}x{ALTO})")


if __name__ == "__main__":
    main()
