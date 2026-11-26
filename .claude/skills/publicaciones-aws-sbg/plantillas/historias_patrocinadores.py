"""Historias 9:16 (1080x1920) de agradecimiento a cada patrocinador del Hackathon 24H ITD 2026.

Uso: python historias_patrocinadores.py <carpeta_imagenes> <carpeta_salida>
"""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
import _comun  # noqa: E402  (fuentes y logos portables)
from _comun import LOGO_ACISTI, PATRO  # noqa: E402


import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

S = 2
W, H = 1080, 1920
M = 90
ZONA_SEGURA = (250, 1670)   # Instagram tapa ~250 px arriba y abajo

FONDO1, FONDO2 = (24, 19, 44), (4, 28, 56)
ACENTO1, ACENTO2 = (174, 92, 255), (0, 190, 226)
CLARO1, CLARO2 = (198, 152, 255), (134, 220, 238)
BLANCO = (240, 242, 247)
SUAVE = (186, 194, 210)

SERIF_B = "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf"
SERIF_BI = "/usr/share/fonts/truetype/crosextra/Caladea-BoldItalic.ttf"
INTER = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
INTER_M = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
INTER_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
LOGO_SBG = _comun.LOGO_SBG

PATROCINADORES = [
    ("dicom.png", "DICOM.MX", "dicom"),
    ("pacs.png", "PACS Computación", "pacs"),
    ("print_company.png", "Print Company", "print_company"),
    ("csni.png", "CSNI", "csni"),
    ("caja_hipodromo.png", "Caja Hipódromo", "caja_hipodromo"),
    ("republica_coffee.png", "República Coffee Roasters", "republica_coffee"),
    ("cosmo_carrier.png", "Cosmo Carrier", "cosmo_carrier"),
    ("xixim.webp", "XIXIM", "xixim"),
    ("cesa.webp", "CESA", "cesa"),
    ("sistemas_computacion.webp", "Departamento de Sistemas y Computación", "sistemas_computacion"),
]
FOTO_CIRCULAR = {"sistemas_computacion.webp"}   # fotos redondas (no logos): se muestran como círculo con halo, sin tarjeta
SOLO_ICONO = {"csni.png"}   # logos sin nombre escrito: se agrega el nombre debajo del ícono

_cache = {}


def s(v):
    return int(round(v * S))


def F(ruta, tam):
    if (ruta, tam) not in _cache:
        _cache[(ruta, tam)] = ImageFont.truetype(ruta, s(tam))
    return _cache[(ruta, tam)]


def mezcla(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def suave(t):
    t = min(1, max(0, t))
    return t * t * (3 - 2 * t)


def fondo():
    col = Image.new("RGB", (1, H))
    for y in range(H):
        col.putpixel((0, y), mezcla(FONDO1, FONDO2, suave((y - 500) / 1000)))
    img = col.resize((s(W), s(H)), Image.Resampling.NEAREST)
    k = 8
    for cx, cy, r, color, a in [(980, 260, 520, ACENTO1, 0.40), (80, 1050, 480, ACENTO1, 0.18),
                                (1000, 1500, 520, ACENTO2, 0.32), (120, 1850, 460, ACENTO2, 0.30)]:
        m = Image.new("L", (W // k, H // k), 0)
        ImageDraw.Draw(m).ellipse([(cx - r) / k, (cy - r) / k, (cx + r) / k, (cy + r) / k], fill=int(255 * a))
        m = m.filter(ImageFilter.GaussianBlur(r / k * 0.55)).resize(img.size, Image.Resampling.BILINEAR)
        img.paste(Image.new("RGB", img.size, color), (0, 0), m)
    d = ImageDraw.Draw(img, "RGBA")
    for x in range(0, W + 1, 60):
        for y in range(0, H, 60):
            c = mezcla(ACENTO1, ACENTO2, suave((y - 500) / 1000))
            d.line([(s(x), s(y)), (s(x), s(y + 60))], fill=c + (30,), width=s(1))
    for y in range(0, H + 1, 60):
        c = mezcla(ACENTO1, ACENTO2, suave((y - 500) / 1000))
        d.line([(0, s(y)), (s(W), s(y))], fill=c + (30,), width=s(1))
    return img


def insignia(img, cx, cy, r, ruta, pad):
    d = ImageDraw.Draw(img)
    d.ellipse([s(cx - r), s(cy - r), s(cx + r), s(cy + r)], fill=(255, 255, 255))
    logo = Image.open(ruta).convert("RGBA")
    lado = s(2 * r * (1 - 2 * pad))
    logo = ImageOps.contain(logo, (lado, lado), Image.Resampling.LANCZOS)
    img.paste(logo.convert("RGB"), (s(cx) - logo.width // 2, s(cy) - logo.height // 2), logo.getchannel("A"))


def envolver(d, texto, f, max_w):
    lineas, act = [], ""
    for p in texto.split():
        prueba = f"{act} {p}".strip()
        if d.textlength(prueba, font=f) / S <= max_w or not act:
            act = prueba
        else:
            lineas.append(act)
            act = p
    if act:
        lineas.append(act)
    return lineas


def limpiar(logo, archivo):
    """Corrige defectos de algunos archivos: recorte sobrante y fondos casi blancos."""
    if archivo == "republica_coffee.png":
        logo = logo.crop((30, 0, logo.width, logo.height))   # franja de otra imagen a la izquierda
    if archivo in ("csni.png", "republica_coffee.png"):
        px = logo.load()
        for y in range(logo.height):
            for x in range(logo.width):
                r, g, b, a = px[x, y]
                claro = min(r, g, b) >= 222
                # En CSNI el fondo es un degradado gris-azulado: todo lo claro y poco saturado pasa a blanco.
                if archivo == "csni.png" and min(r, g, b) > 140 and max(r, g, b) - min(r, g, b) < 45:
                    claro = True
                if claro:
                    px[x, y] = (255, 255, 255, a)
    return logo


def historia(carpeta, archivo, nombre):
    img = fondo()
    d = ImageDraw.Draw(img, "RGBA")
    cajas = []

    def t(x, y, texto, f, color, anchor="la"):
        d.text((s(x), s(y)), texto, font=f, fill=color, anchor=anchor)
        b = d.textbbox((s(x), s(y)), texto, font=f, anchor=anchor)
        cajas.append((texto, b[0] / S, b[1] / S, b[2] / S, b[3] / S))

    # Collab arriba (dentro de la zona segura)
    r = 34
    fx = F(INTER_B, 30)
    ancho_x = d.textlength("×", font=fx) / S
    total = 2 * r + 16 + ancho_x + 16 + 2 * r
    x0 = (W - total) / 2
    insignia(img, x0 + r, 300, r, LOGO_SBG, 0.17)
    t(x0 + 2 * r + 16, 300, "×", fx, CLARO1, "lm")
    insignia(img, x0 + 2 * r + 32 + ancho_x + r, 300, r, LOGO_ACISTI, 0.0)
    t(W / 2, 372, "AWS STUDENT BUILDER GROUP × ACISTI", F(INTER_B, 20), BLANCO, "mm")
    d.line([(s(M + 60), s(410)), (s(W - M - 60), s(410))], fill=CLARO1, width=s(2))
    d.line([(s(M + 60), s(417)), (s(W - M - 60), s(417))], fill=ACENTO1, width=s(1))

    # Título
    t(W / 2, 470, "HACKATHON 24H · ITD 2026", F(INTER_B, 22), CLARO1, "mt")
    t(W / 2, 520, "Patrocinador", F(SERIF_B, 112), BLANCO, "mt")
    t(W / 2, 636, "oficial", F(SERIF_BI, 112), ACENTO1, "mt")

    if archivo in FOTO_CIRCULAR:
        return historia_circular(img, d, cajas, t, carpeta, archivo, nombre)

    # Tarjeta del logo con borde luminoso
    cw, ch = 760, 520
    cx0, cy0 = (W - cw) / 2, 820
    pad = 70
    m = Image.new("L", (s(cw + 2 * pad), s(ch + 2 * pad)), 0)
    ImageDraw.Draw(m).rounded_rectangle([s(pad), s(pad), s(pad + cw), s(pad + ch)], radius=s(32), outline=230, width=s(8))
    m = m.filter(ImageFilter.GaussianBlur(s(22)))
    grad = Image.new("RGB", m.size)
    gd = ImageDraw.Draw(grad)
    for x in range(m.width):
        gd.line([(x, 0), (x, m.height)], fill=mezcla(ACENTO1, ACENTO2, x / m.width))
    img.paste(grad, (s(cx0 - pad), s(cy0 - pad)), m)
    d.rounded_rectangle([s(cx0), s(cy0), s(cx0 + cw), s(cy0 + ch)], radius=s(32), fill=(255, 255, 255))
    logo = limpiar(Image.open(PATRO / archivo).convert("RGBA"), archivo)
    alto_logo = 0.62 if archivo in SOLO_ICONO else 0.74
    logo = ImageOps.contain(logo, (s(cw * 0.80), s(ch * alto_logo)), Image.Resampling.LANCZOS)
    ly = s(cy0 + ch / 2) - logo.height // 2 - (s(40) if archivo in SOLO_ICONO else 0)
    img.paste(logo.convert("RGB"), (s(W / 2) - logo.width // 2, ly), logo.getchannel("A"))
    if archivo in SOLO_ICONO:
        t(W / 2, ly / S + logo.height / S + 30, nombre, F(INTER_B, 52), (60, 60, 64), "mt")

    # Agradecimiento
    y = 1420
    for linea in envolver(d, f"¡Gracias, {nombre}!", F(SERIF_BI, 62), W - 2 * M):
        t(W / 2, y, linea, F(SERIF_BI, 62), BLANCO, "mt")
        y += 72
    y += 14
    for linea in envolver(d, "Por impulsar el talento de los builders y hacer posible el Hackathon 24H ITD 2026.",
                          F(INTER_M, 30), W - 2 * M - 40):
        t(W / 2, y, linea, F(INTER_M, 30), SUAVE, "mt")
        y += 42

    errores = [f"'{c[0]}' fuera de la zona segura ({c[2]:.0f}..{c[4]:.0f})"
               for c in cajas if c[1] < 80 or c[3] > W - 80 or c[2] < ZONA_SEGURA[0] or c[4] > ZONA_SEGURA[1]]
    for c in cajas:
        if c[0] != nombre and c[2] < cy0 + ch and c[4] > cy0 and c[1] < cx0 + cw and c[3] > cx0:
            errores.append(f"'{c[0]}' encima de la tarjeta del logo")
    return img.resize((W, H), Image.Resampling.LANCZOS), errores


def historia_circular(img, d, cajas, t, carpeta, archivo, nombre):
    """Variante para una foto redonda: círculo grande con halo de morado a azul."""
    r = 300
    cx, cy = W / 2, 1060
    pad = 90
    m = Image.new("L", (s(2 * (r + pad)), s(2 * (r + pad))), 0)
    ImageDraw.Draw(m).ellipse([s(pad), s(pad), s(pad + 2 * r), s(pad + 2 * r)], outline=240, width=s(10))
    m = m.filter(ImageFilter.GaussianBlur(s(26)))
    grad = Image.new("RGB", m.size)
    gd = ImageDraw.Draw(grad)
    for x in range(m.width):
        gd.line([(x, 0), (x, m.height)], fill=mezcla(ACENTO1, ACENTO2, x / m.width))
    img.paste(grad, (s(cx - r - pad), s(cy - r - pad)), m)
    foto = Image.open(PATRO / archivo).convert("RGB")
    lado = min(foto.size)
    foto = foto.crop(((foto.width - lado) // 2, (foto.height - lado) // 2,
                      (foto.width + lado) // 2, (foto.height + lado) // 2))
    foto = foto.resize((s(2 * r), s(2 * r)), Image.Resampling.LANCZOS)
    mk = Image.new("L", foto.size, 0)
    ImageDraw.Draw(mk).ellipse([0, 0, foto.width - 1, foto.height - 1], fill=255)
    img.paste(foto, (s(cx - r), s(cy - r)), mk)
    anillo = Image.new("RGB", (s(2 * r + 12), s(2 * r + 12)))
    ad = ImageDraw.Draw(anillo)
    for x in range(anillo.width):
        ad.line([(x, 0), (x, anillo.height)], fill=mezcla(CLARO1, CLARO2, x / anillo.width))
    ma = Image.new("L", anillo.size, 0)
    ImageDraw.Draw(ma).ellipse([0, 0, anillo.width - 1, anillo.height - 1], outline=255, width=s(5))
    img.paste(anillo, (s(cx - r - 6), s(cy - r - 6)), ma)

    y = 1420
    for linea in envolver(d, f"¡Gracias, {nombre}!", F(SERIF_BI, 58), W - 2 * M):
        t(W / 2, y, linea, F(SERIF_BI, 58), BLANCO, "mt")
        y += 66
    y += 12
    for linea in envolver(d, "Por impulsar el talento de los builders y hacer posible el Hackathon 24H ITD 2026.",
                          F(INTER_M, 28), W - 2 * M - 40):
        t(W / 2, y, linea, F(INTER_M, 28), SUAVE, "mt")
        y += 38

    errores = [f"'{c[0]}' fuera de la zona segura ({c[2]:.0f}..{c[4]:.0f})"
               for c in cajas if c[1] < 80 or c[3] > W - 80 or c[2] < ZONA_SEGURA[0] or c[4] > ZONA_SEGURA[1]]
    for c in cajas:
        if c[2] < cy + r and c[4] > cy - r and c[1] < cx + r and c[3] > cx - r:
            errores.append(f"'{c[0]}' encima de la foto")
    return img.resize((W, H), Image.Resampling.LANCZOS), errores


def portada(carpeta):
    """Historia principal: todos los patrocinadores y un agradecimiento general."""
    img = fondo()
    d = ImageDraw.Draw(img, "RGBA")
    cajas = []

    def t(x, y, texto, f, color, anchor="la"):
        d.text((s(x), s(y)), texto, font=f, fill=color, anchor=anchor)
        b = d.textbbox((s(x), s(y)), texto, font=f, anchor=anchor)
        cajas.append((texto, b[0] / S, b[1] / S, b[2] / S, b[3] / S))

    r = 34
    fx = F(INTER_B, 30)
    ancho_x = d.textlength("×", font=fx) / S
    total = 2 * r + 16 + ancho_x + 16 + 2 * r
    x0 = (W - total) / 2
    insignia(img, x0 + r, 300, r, LOGO_SBG, 0.17)
    t(x0 + 2 * r + 16, 300, "×", fx, CLARO1, "lm")
    insignia(img, x0 + 2 * r + 32 + ancho_x + r, 300, r, LOGO_ACISTI, 0.0)
    t(W / 2, 372, "AWS STUDENT BUILDER GROUP × ACISTI", F(INTER_B, 20), BLANCO, "mm")
    d.line([(s(M + 60), s(410)), (s(W - M - 60), s(410))], fill=CLARO1, width=s(2))
    d.line([(s(M + 60), s(417)), (s(W - M - 60), s(417))], fill=ACENTO1, width=s(1))

    t(W / 2, 470, "HACKATHON 24H · ITD 2026", F(INTER_B, 22), CLARO1, "mt")
    t(W / 2, 515, "Nuestros patrocinadores", F(SERIF_B, 80), BLANCO, "mt")
    t(W / 2, 600, "oficiales", F(SERIF_BI, 104), ACENTO1, "mt")

    # Número grande en contorno con brillo (sin logos)
    NUM = str(len(PATROCINADORES))
    fnum = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf", s(560))
    cx, cy = W / 2, 1060
    caja = d.textbbox((s(cx), s(cy)), NUM, font=fnum, anchor="mm", stroke_width=s(6))
    pad = s(90)
    m = Image.new("L", (caja[2] - caja[0] + 2 * pad, caja[3] - caja[1] + 2 * pad), 0)
    ImageDraw.Draw(m).text((s(cx) - caja[0] + pad, s(cy) - caja[1] + pad), NUM, font=fnum, fill=0,
                           anchor="mm", stroke_width=s(10), stroke_fill=255)
    m = m.filter(ImageFilter.GaussianBlur(s(26)))
    grad = Image.new("RGB", m.size)
    gd = ImageDraw.Draw(grad)
    for yy in range(m.height):
        gd.line([(0, yy), (m.width, yy)], fill=mezcla(ACENTO1, ACENTO2, yy / m.height))
    img.paste(grad, (caja[0] - pad, caja[1] - pad), m)
    d.text((s(cx), s(cy)), NUM, font=fnum, fill=(20, 18, 40), anchor="mm", stroke_width=s(5), stroke_fill=CLARO2)
    cajas.append((NUM, caja[0] / S, caja[1] / S, caja[2] / S, caja[3] / S))
    t(W / 2, caja[3] / S + 30, "aliados que impulsaron el hackathon", F(SERIF_BI, 44), CLARO2, "mt")
    fin = caja[3] / S + 90

    y = fin + 70
    t(W / 2, y, "¡Gracias por hacerlo posible!", F(SERIF_BI, 60), BLANCO, "mt")
    y += 84
    for linea in envolver(d, "Su apoyo impulsó a 23 equipos de builders durante 24 horas de código.",
                          F(INTER_M, 30), W - 2 * M - 40):
        t(W / 2, y, linea, F(INTER_M, 30), SUAVE, "mt")
        y += 42
    t(W / 2, y + 30, "Toca para conocerlos  →", F(INTER_B, 24), CLARO2, "mt")

    errores = [f"'{c[0]}' fuera de la zona segura ({c[2]:.0f}..{c[4]:.0f})"
               for c in cajas if c[1] < 80 or c[3] > W - 80 or c[2] < ZONA_SEGURA[0] or c[4] > ZONA_SEGURA[1]]
    return img.resize((W, H), Image.Resampling.LANCZOS), errores


def main():
    carpeta, salida = Path(sys.argv[1]), Path(sys.argv[2])
    salida.mkdir(parents=True, exist_ok=True)
    todos = []
    im, errores = portada(carpeta)
    todos += [f"Portada: {e}" for e in errores]
    im.save(salida / "historia_00_portada.png")
    print("Guardada:", salida / "historia_00_portada.png")
    for archivo, nombre, clave in PATROCINADORES:
        im, errores = historia(carpeta, archivo, nombre)
        todos += [f"{nombre}: {e}" for e in errores]
        ruta = salida / f"historia_{clave}.png"
        im.save(ruta)
        print("Guardada:", ruta)
    if todos:
        sys.exit("Errores:\n" + "\n".join(todos))


if __name__ == "__main__":
    main()
