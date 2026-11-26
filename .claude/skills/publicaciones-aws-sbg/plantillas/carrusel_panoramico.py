"""Carrusel recap "Hackathon AWS Student Builder Group × ACISTI" — 11 slides de 1080x1440.

Se dibuja un panorama continuo de 11 880 x 1440 px y se corta en 11 partes.
Mitad 1 (slides 1-6): paleta morada del grupo. Mitad 2 (slides 7-11): azules de ACISTI.
Uso: python carrusel_hackathon.py <carpeta_imagenes> <carpeta_salida> <carpeta_previa>
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
SW, H = 1080, 1440
N = 11
W = SW * N
M = 90
CORTE = 6 * SW                    # unión slide 6 | slide 7
GRAD0, GRAD1 = CORTE - 88, CORTE + 88   # degradado de 176 px, entre los márgenes de texto

# Paleta 1 (grupo)
FONDO1 = (24, 19, 44)
ACENTO1 = (174, 92, 255)
CLARO1 = (198, 152, 255)
RELLENO1 = (40, 32, 66)
# Paleta 2 (ACISTI)
FONDO2 = (4, 28, 56)
ACENTO2 = (0, 190, 226)
CLARO2 = (134, 220, 238)
RELLENO2 = (8, 52, 86)

BLANCO = (240, 242, 247)
SUAVE = (180, 188, 204)
MARCO = (92, 104, 126)
LINEA = (255, 255, 255)

SERIF_B = "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf"
SERIF_BI = "/usr/share/fonts/truetype/crosextra/Caladea-BoldItalic.ttf"
SERIF_I = "/usr/share/fonts/truetype/crosextra/Caladea-Italic.ttf"
INTER = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
INTER_M = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
INTER_SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
INTER_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
DISPLAY = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"

LOGO_SBG = _comun.LOGO_SBG

_cache = {}


def s(v):
    return int(round(v * S))


def F(ruta, tam):
    if (ruta, tam) not in _cache:
        try:
            _cache[(ruta, tam)] = ImageFont.truetype(ruta, s(tam))
        except OSError:
            _cache[(ruta, tam)] = ImageFont.load_default(size=s(tam))
    return _cache[(ruta, tam)]


def acento_global(x):
    t = min(1, max(0, (x - GRAD0) / (GRAD1 - GRAD0)))
    t = t * t * (3 - 2 * t)
    return tuple(round(a + (b - a) * t) for a, b in zip(ACENTO1, ACENTO2))


def pal(n):
    """Paleta de la slide n (1-based)."""
    if n <= 6:
        return dict(acento=ACENTO1, claro=CLARO1, relleno=RELLENO1)
    return dict(acento=ACENTO2, claro=CLARO2, relleno=RELLENO2)


class Lienzo:
    def __init__(self, carpeta):
        self.carpeta = carpeta
        self.img = self._fondo()
        self.d = ImageDraw.Draw(self.img, "RGBA")
        self.textos = []   # (slide, texto, x0, y0, x1, y1) en coordenadas del panorama
        self.fotos = []    # (nombre, x0, y0, x1, y1)
        self._cuadricula()

    # ------------------------------------------------------------------ fondo
    def _fondo(self):
        # Color base por columna con degradado suave en la unión 6|7.
        fila = Image.new("RGB", (W, 1))
        for x in range(W):
            t = min(1, max(0, (x - GRAD0) / (GRAD1 - GRAD0)))
            t = t * t * (3 - 2 * t)
            fila.putpixel((x, 0), tuple(round(a + (b - a) * t) for a, b in zip(FONDO1, FONDO2)))
        base = fila.resize((s(W), s(H)), Image.Resampling.NEAREST)
        # Resplandores (a baja resolución y luego escalados).
        k = 8
        glow = Image.new("RGB", (W // k, H // k), (0, 0, 0))
        g = ImageDraw.Draw(glow)
        brillos = [(950, 120, 420, ACENTO1, 0.30), (2300, 1250, 380, ACENTO1, 0.18),
                   (3950, 200, 420, ACENTO1, 0.22), (5600, 1300, 380, ACENTO1, 0.18),
                   (6120, 740, 560, ACENTO1, 0.45), (6840, 740, 560, ACENTO2, 0.45),
                   (6300, 140, 360, ACENTO1, 0.30), (6660, 1320, 360, ACENTO2, 0.30),
                   (7700, 150, 420, ACENTO2, 0.22), (9100, 1300, 420, ACENTO2, 0.20),
                   (10900, 220, 460, ACENTO2, 0.26)]
        capas = []
        for cx, cy, r, color, a in brillos:
            m = Image.new("L", (W // k, H // k), 0)
            ImageDraw.Draw(m).ellipse([(cx - r) / k, (cy - r) / k, (cx + r) / k, (cy + r) / k], fill=int(255 * a))
            m = m.filter(ImageFilter.GaussianBlur(r / k * 0.55))
            capas.append((m.resize(base.size, Image.Resampling.BILINEAR), color))
        for m, color in capas:
            base.paste(Image.new("RGB", base.size, color), (0, 0), m)
        self._haz(base)
        return base

    def _haz(self, base):
        """Haz de luz vertical en la unión 6|7: franja que pasa de morado a cyan con un filo brillante."""
        import math
        x0, x1 = GRAD0 - 40, GRAD1 + 40
        ancho = x1 - x0
        color = Image.new("RGB", (ancho, 1))
        alfa = Image.new("L", (ancho, 1))
        for i in range(ancho):
            x = x0 + i
            c = acento_global(x)
            d = (x - CORTE) / 46
            nucleo = math.exp(-d * d)
            halo = math.exp(-((x - CORTE) / 110) ** 2)
            color.putpixel((i, 0), tuple(round(v + (255 - v) * 0.55 * nucleo) for v in c))
            alfa.putpixel((i, 0), round(255 * min(1, 0.85 * nucleo + 0.35 * halo)))
        color = color.resize((s(ancho), s(H)), Image.Resampling.BILINEAR)
        alfa = alfa.resize((s(ancho), s(H)), Image.Resampling.BILINEAR)
        # Se desvanece un poco arriba y abajo para que no parezca un corte duro.
        vert = Image.new("L", (1, H))
        for y in range(H):
            vert.putpixel((0, y), round(255 * (0.55 + 0.45 * math.sin(math.pi * y / H))))
        alfa = Image.composite(alfa, Image.new("L", alfa.size, 0), vert.resize(alfa.size, Image.Resampling.BILINEAR))
        base.paste(color, (s(x0), 0), alfa)

    def _cuadricula(self):
        celda = 60
        # Cuadrícula teñida con el color de cada mitad.
        for x in range(0, W + 1, celda):
            self.d.line([(s(x), 0), (s(x), s(H))], fill=acento_global(x) + (30,), width=s(1))
        for y in range(0, H + 1, celda):
            for x in range(0, W, celda):
                self.d.line([(s(x), s(y)), (s(x + celda), s(y))], fill=acento_global(x + celda / 2) + (30,), width=s(1))

    # ------------------------------------------------------------------ primitivas
    def t(self, n, x, y, texto, f, color=BLANCO, anchor="la"):
        """Texto en coordenadas locales de la slide n."""
        ox = (n - 1) * SW
        self.d.text((s(ox + x), s(y)), texto, font=f, fill=color, anchor=anchor)
        b = self.d.textbbox((s(ox + x), s(y)), texto, font=f, anchor=anchor)
        self.textos.append((n, texto[:28], b[0] / S, b[1] / S, b[2] / S, b[3] / S))

    def ancho(self, texto, f):
        return self.d.textlength(texto, font=f) / S

    def envolver(self, texto, f, max_w):
        lineas, act = [], ""
        for p in texto.split():
            prueba = f"{act} {p}".strip()
            if self.ancho(prueba, f) <= max_w or not act:
                act = prueba
            else:
                lineas.append(act)
                act = p
        if act:
            lineas.append(act)
        return lineas

    def parrafo(self, n, x, y, texto, ruta, tam, max_w, color=SUAVE, inter=1.38):
        for linea in self.envolver(texto, F(ruta, tam), max_w):
            self.t(n, x, y, linea, F(ruta, tam), color)
            y += tam * inter
        return y

    def foto(self, nombre, gx, y, h):
        """Foto completa (sin recorte) de alto h, esquina en coordenadas globales (gx, y)."""
        f = Image.open(self.carpeta / nombre).convert("RGB")
        w = round(h * f.width / f.height)
        self.img.paste(f.resize((s(w), s(h)), Image.Resampling.LANCZOS), (s(gx), s(y)))
        self.d.rectangle([s(gx), s(y), s(gx + w), s(y + h)], outline=MARCO, width=s(2))
        self.fotos.append((nombre, gx, y, gx + w, y + h))
        return w

    def ancho_foto(self, nombre, h):
        with Image.open(self.carpeta / nombre) as f:
            return round(h * f.width / f.height)

    def insignia(self, cx, cy, r, ruta, fondo=(255, 255, 255), pad=0.16):
        """Logo dentro de un círculo blanco (coordenadas globales)."""
        self.d.ellipse([s(cx - r), s(cy - r), s(cx + r), s(cy + r)], fill=fondo)
        logo = Image.open(ruta).convert("RGBA")
        lado = s(2 * r * (1 - 2 * pad))
        logo = ImageOps.contain(logo, (lado, lado), Image.Resampling.LANCZOS)
        self.img.paste(logo.convert("RGB"), (s(cx) - logo.width // 2, s(cy) - logo.height // 2), logo.getchannel("A"))

    def lockup(self, n, x, cy, r, color_x):
        """Chip SBG × ACISTI. x = borde izquierdo local. Devuelve el borde derecho local."""
        ox = (n - 1) * SW
        self.insignia(ox + x + r, cy, r, LOGO_SBG, pad=0.17)
        fx = F(INTER_B, int(r * 0.9))
        xm = x + 2 * r + 12
        self.t(n, xm, cy, "×", fx, color_x, "lm")
        xa = xm + self.ancho("×", fx) + 12
        self.insignia(ox + xa + r, cy, r, LOGO_ACISTI, pad=0.0)
        return xa + 2 * r

    def tarjeta_logo(self, gx, y, w, h, nombre):
        self.d.rounded_rectangle([s(gx), s(y), s(gx + w), s(y + h)], radius=s(18), fill=(255, 255, 255))
        logo = Image.open(PATRO / nombre).convert("RGBA")
        if nombre == "republica_coffee.png":
            logo = logo.crop((30, 0, logo.width, logo.height))
        if nombre in ("csni.png", "republica_coffee.png"):
            px = logo.load()
            for yy in range(logo.height):
                for xx in range(logo.width):
                    r_, g_, b_, a_ = px[xx, yy]
                    if min(r_, g_, b_) >= 222 or (nombre == "csni.png" and min(r_, g_, b_) > 140
                                                  and max(r_, g_, b_) - min(r_, g_, b_) < 45):
                        px[xx, yy] = (255, 255, 255, a_)
        logo = ImageOps.contain(logo, (s(w * 0.78), s(h * 0.72)), Image.Resampling.LANCZOS)
        self.img.paste(logo.convert("RGB"), (s(gx + w / 2) - logo.width // 2, s(y + h / 2) - logo.height // 2),
                       logo.getchannel("A"))
        self.fotos.append((nombre, gx, y, gx + w, y + h))

    # ------------------------------------------------------------------ piezas repetidas
    def cabecera(self, n, seccion):
        p = pal(n)
        der = self.lockup(n, M, 104, 24, p["claro"])
        self.t(n, der + 18, 104, "AWS STUDENT BUILDER GROUP × ACISTI", F(INTER_B, 17), BLANCO, "lm")
        self.t(n, SW - M, 104, seccion.upper(), F(INTER_SB, 17), p["claro"], "rm")
        ox = (n - 1) * SW
        self.d.line([(s(ox + M), s(146)), (s(ox + SW - M), s(146))], fill=p["claro"], width=s(2))
        self.d.line([(s(ox + M), s(152)), (s(ox + SW - M), s(152))], fill=p["acento"], width=s(1))

    def pie(self, n):
        ox = (n - 1) * SW
        self.d.line([(s(ox + M), s(1352)), (s(ox + SW - M), s(1352))], fill=pal(n)["acento"] + (150,), width=s(1))
        self.t(n, M, 1384, "Hackathon 24H  —  ITD 2026", F(SERIF_I, 20), SUAVE, "lm")
        self.t(n, SW - M, 1384, f"{n} / {N}" + ("  →" if n < N else ""), F(INTER_SB, 19), BLANCO, "rm")

    def titulo(self, n, l1, l2, y=196, tam=72):
        p = pal(n)
        self.t(n, M, y, l1, F(SERIF_B, tam), BLANCO)
        self.t(n, M, y + tam * 1.06, l2, F(SERIF_BI, tam), p["acento"])
        return y + tam * 2.2

    def numero(self, n, x, y, texto, tam=170, anchor="ra"):
        p = pal(n)
        ox = (n - 1) * SW
        f = F(DISPLAY, tam)
        self.d.text((s(ox + x), s(y)), texto, font=f, fill=p["relleno"], anchor=anchor,
                    stroke_width=s(3), stroke_fill=p["acento"])
        b = self.d.textbbox((s(ox + x), s(y)), texto, font=f, anchor=anchor, stroke_width=s(3))
        self.textos.append((n, texto, b[0] / S, b[1] / S, b[2] / S, b[3] / S))

    def etiqueta(self, n, x, y, texto):
        """Etiqueta pequeña con fondo de color (para lugares y nombres de proyecto)."""
        p = pal(n)
        f = F(INTER_B, 18)
        w = self.ancho(texto, f) + 28
        ox = (n - 1) * SW
        self.d.rounded_rectangle([s(ox + x), s(y), s(ox + x + w), s(y + 36)], radius=s(18), fill=p["acento"])
        self.t(n, x + 14, y + 18, texto, f, FONDO1, "lm")
        return w

    # ------------------------------------------------------------------ verificación
    def verificar(self):
        errores = []
        for n, t, x0, y0, x1, y1 in self.textos:
            ox = (n - 1) * SW
            if x0 < ox + 80 or x1 > ox + SW - 80 or y0 < 60 or y1 > H - 30:
                errores.append(f"slide {n}: '{t}' fuera del margen ({x0 - ox:.0f}..{x1 - ox:.0f}, {y0:.0f}..{y1:.0f})")
            if x0 < GRAD1 and x1 > GRAD0:
                errores.append(f"slide {n}: '{t}' cae en el degradado")
            for nombre, fx0, fy0, fx1, fy1 in self.fotos:
                if x0 < fx1 and x1 > fx0 and y0 < fy1 and y1 > fy0:
                    errores.append(f"slide {n}: '{t}' encima de {nombre}")
        for i, (nombre, x0, y0, x1, y1) in enumerate(self.fotos):
            if x0 < 40 or x1 > W - 40 or y0 < 170 or y1 > 1335:
                errores.append(f"{nombre} fuera del área ({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f})")
            for k in range(1, N):
                b = k * SW
                if x0 < b < x1 and min(b - x0, x1 - b) < 110:
                    errores.append(f"{nombre}: queda un trozo de {min(b - x0, x1 - b):.0f} px al cruzar la división {k}|{k + 1}")
            for otro in self.fotos[i + 1:]:
                if x0 < otro[3] and x1 > otro[1] and y0 < otro[4] and y1 > otro[2]:
                    errores.append(f"{nombre} se encima con {otro[0]}")
        return errores


def main():
    carpeta, salida, previa = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    L = Lienzo(carpeta)

    def g(n, x):
        return (n - 1) * SW + x

    # ── 1 · Portada
    n = 1
    L.cabecera(n, "Recap")
    L.t(n, M, 200, "HACKATHON 24H · ITD 2026", F(INTER_B, 20), CLARO1)
    y = 240
    for linea in ("Hackathon", "AWS Student", "Builder Group"):
        L.t(n, M, y, linea, F(SERIF_B, 84), BLANCO)
        y += 88
    L.t(n, M, y, "× ACISTI", F(SERIF_BI, 84), ACENTO1)
    y += 120
    L.t(n, M, y, "19 de noviembre en el ITD", F(INTER_M, 28), SUAVE)
    L.foto("43.webp", g(n, M), 800, 520)
    L.foto("45.webp", g(n, 520), 800, 520)
    L.t(n, 940, 760, "Así se vivió →", F(SERIF_BI, 34), CLARO1, "ra")

    # ── 2 · Llegada
    n = 2
    L.cabecera(n, "Llegada")
    L.titulo(n, "Llegamos", "con todo")
    L.parrafo(n, M, 380, "Desde temprano, el vestíbulo del ITD se llenó de builders listos para 24 horas de código.",
              INTER, 24, 860)
    L.foto("59.webp", g(n, M), 500, 330)
    L.foto("62.webp", g(n, 560), 500, 330)
    w25 = L.ancho_foto("25.webp", 380)
    L.foto("25.webp", g(n, SW) - w25 // 2, 900, 380)
    L.numero(n, M, 930, "24 h", 150, "la")
    L.t(n, M + 6, 1120, "de código sin parar", F(SERIF_I, 30), SUAVE)

    # ── 3 · Registro
    n = 3
    L.cabecera(n, "Registro")
    L.titulo(n, "Gafete,", "registro y listo")
    L.parrafo(n, M, 380, "El staff recibió a cada participante en la mesa de registro.", INTER, 24, 860)
    L.foto("26.webp", g(n, 300), 480, 380)
    L.foto("27.webp", g(n, 605), 480, 380)
    w28 = L.ancho_foto("28.webp", 360)
    L.foto("28.webp", g(n, SW) - w28 // 2 + 60, 900, 360)
    L.foto("29.webp", g(n, 300), 900, 380)

    # ── 4 · Arranque
    n = 4
    L.cabecera(n, "Arranque")
    L.titulo(n, "Arrancó", "el hackathon")
    L.parrafo(n, M, 380, "Organizadores y profesores del ITD dieron la bienvenida y explicaron el reto.",
              INTER, 24, 860)
    L.foto("31.webp", g(n, 330), 520, 320)
    L.foto("30.webp", g(n, M), 470, 400)
    L.foto("63.webp", g(n, 380), 900, 400)
    w32 = L.ancho_foto("32.webp", 400)
    L.foto("32.webp", g(n, SW) - w32 // 2, 880, 400)
    L.numero(n, 870, 880, "23", 170, "ra")
    L.t(n, 870, 1090, "equipos", F(SERIF_BI, 40), CLARO1, "ra")
    L.t(n, 870, 1146, "en competencia", F(INTER_M, 22), SUAVE, "ra")

    # ── 5 · Equipos de 4
    n = 5
    L.cabecera(n, "Equipos")
    L.titulo(n, "Equipos", "de 1 a 4 integrantes")
    L.parrafo(n, M, 380, "Ideas, pizarrón y código: cada equipo trabajó en su solución durante todo el día.",
              INTER, 24, 860)
    L.foto("61.webp", g(n, 200), 480, 360)
    L.foto("33.webp", g(n, 710), 480, 360)
    L.foto("34.webp", g(n, 160), 900, 340)
    L.foto("35.webp", g(n, 440), 900, 340)
    L.numero(n, SW - M, 930, "1–4", 130, "ra")
    L.t(n, SW - M, 1110, "integrantes", F(SERIF_BI, 34), CLARO1, "ra")
    L.t(n, SW - M, 1155, "por equipo", F(SERIF_BI, 34), CLARO1, "ra")

    # ── 6 · Patrocinadores
    n = 6
    L.cabecera(n, "Patrocinadores")
    L.titulo(n, "Gracias a nuestros", "patrocinadores")
    L.parrafo(n, M, 380, "Hicieron posibles los premios y cada hora del hackathon.", INTER, 24, 860)
    logos = ["dicom.png", "pacs.png", "print_company.png", "csni.png", "caja_hipodromo.png", "republica_coffee.png", "cosmo_carrier.png", "xixim.webp", "cesa.webp"]
    cw, ch, gap = 196, 150, 22
    for i, nombre in enumerate(logos):
        c, r = i % 3, i // 3
        L.tarjeta_logo(g(n, M + c * (cw + gap)), 470 + r * (ch + gap), cw, ch, nombre)
    L.foto("57.webp", g(n, 760), 470, 306)
    L.t(n, 760, 890, "Premios para", F(SERIF_I, 22), SUAVE)
    L.t(n, 760, 918, "los ganadores", F(SERIF_I, 22), SUAVE)
    # Tarjeta ancha para el Departamento de Sistemas y Computación (foto redonda + nombre)
    tx0, ty0, tw, th = g(n, M), 470 + 3 * (ch + gap), 3 * cw + 2 * gap, ch
    L.d.rounded_rectangle([s(tx0), s(ty0), s(tx0 + tw), s(ty0 + th)], radius=s(18), fill=(255, 255, 255))
    rr = 56
    foto = Image.open(PATRO / "sistemas_computacion.webp").convert("RGB").resize((s(2 * rr), s(2 * rr)), Image.Resampling.LANCZOS)
    mk = Image.new("L", foto.size, 0)
    ImageDraw.Draw(mk).ellipse([0, 0, foto.width - 1, foto.height - 1], fill=255)
    L.img.paste(foto, (s(tx0 + 28), s(ty0 + th / 2 - rr)), mk)
    L.d.text((s(tx0 + 28 + 2 * rr + 26), s(ty0 + th / 2 - 4)), "Departamento de", font=F(INTER_B, 26),
             fill=(40, 44, 54), anchor="ls")
    L.d.text((s(tx0 + 28 + 2 * rr + 26), s(ty0 + th / 2 + 30)), "Sistemas y Computación", font=F(INTER_B, 26),
             fill=(40, 44, 54), anchor="ls")
    L.fotos.append(("sistemas_computacion.webp", tx0, ty0, tx0 + tw, ty0 + th))
    nombres = ("DICOM.MX · PACS Computación · Print Company · CSNI · Caja Hipódromo · "
               "República Coffee Roasters · Cosmo Carrier · XIXIM · CESA · Depto. de Sistemas y Computación")
    L.parrafo(n, M, ty0 + th + 34, nombres, INTER_M, 22, 860, SUAVE, 1.45)

    # ── 7 · Pitches y proyectos
    n = 7
    L.cabecera(n, "Pitches")
    L.titulo(n, "Del código", "al pitch")
    L.parrafo(n, M, 380, "Cada equipo presentó su proyecto ante el jurado.", INTER, 24, 860)
    L.foto("36.webp", g(n, M), 450, 330)
    L.foto("39.webp", g(n, 550), 450, 330)
    L.etiqueta(n, M, 800, "PROVEEDON")
    L.parrafo(n, M, 848, "Compara precios de proveedores locales.", INTER, 21, 420)
    L.etiqueta(n, 550, 800, "LOCALIA")
    L.parrafo(n, 550, 848, "Conecta consumidores con productos locales.", INTER, 21, 420)
    w40 = L.ancho_foto("40.webp", 330)
    L.foto("40.webp", g(n, SW) - w40 // 2 + 40, 960, 330)
    L.etiqueta(n, M, 960, "FYNDO →")
    L.parrafo(n, M, 1008, "Descubre lo que se produce cerca de ti: productores y vendedores a unos kilómetros.",
              INTER, 21, 600)

    # ── 8 · Jurado
    n = 8
    L.cabecera(n, "Jurado")
    L.titulo(n, "La evaluación", "del jurado")
    L.parrafo(n, M, 380, "Jueces de la industria y del ITD escucharon cada pitch y eligieron a los ganadores.",
              INTER, 24, 860)
    L.foto("37.webp", g(n, 330), 470, 420)
    L.foto("38.webp", g(n, 670), 470, 420)
    L.foto("44.webp", g(n, 420), 920, 380)

    # ── 9 · Ganadores
    n = 9
    L.cabecera(n, "Ganadores")
    L.titulo(n, "Los", "ganadores")
    L.etiqueta(n, M, 380, "1.ER LUGAR")
    L.foto("48.webp", g(n, M), 430, 450)
    L.etiqueta(n, M, 910, "2.º LUGAR")
    L.foto("47.webp", g(n, M), 960, 330)
    L.etiqueta(n, 560, 910, "3.ER LUGAR")
    L.foto("46.webp", g(n, 560), 960, 200)

    # ── 10 · Reconocimientos
    n = 10
    L.cabecera(n, "Reconocimientos")
    L.titulo(n, "Reconocimientos", "para todos")
    L.parrafo(n, M, 380, "Participantes, jueces y equipo de ACISTI se llevaron su reconocimiento del Hackathon 24H ITD 2026.",
              INTER, 24, 860)
    L.foto("41.webp", g(n, M), 480, 600)
    w42 = L.ancho_foto("42.webp", 420)
    L.foto("42.webp", g(n, SW) - w42 // 2 + 20, 860, 420)

    # ── 11 · Cierre
    n = 11
    L.cabecera(n, "Gracias")
    L.titulo(n, "¡Gracias", "por hacerlo posible!")
    L.parrafo(n, 360, 700, "A los 23 equipos participantes, a los mentores, a los jueces, a los patrocinadores "
              "y al equipo de ACISTI.", INTER_M, 26, 630, BLANCO, 1.4)
    # Cierre editorial: frase grande y lista numerada con filetes (sin tarjeta ni botón)
    x0, x1 = 360, SW - M
    ox = (n - 1) * SW
    L.t(n, x0, 860, "¿NOS VEMOS EN EL PRÓXIMO?", F(INTER_B, 18), ACENTO2)
    L.t(n, x0, 892, "Esto apenas", F(SERIF_BI, 56), BLANCO)
    L.t(n, x0, 952, "empieza.", F(SERIF_BI, 56), ACENTO2)
    pasos = ["Síguenos en Instagram", "Comparte este recap con tu equipo", "Ve preparando tu idea para el próximo"]
    y = 1052
    for i, paso in enumerate(pasos, 1):
        L.d.line([(s(ox + x0), s(y)), (s(ox + x1), s(y))], fill=ACENTO2 + (170,), width=s(1))
        L.t(n, x0, y + 40, f"0{i}", F(DISPLAY, 30), ACENTO2, "lm")
        L.t(n, x0 + 64, y + 40, paso, F(INTER_M, 25), BLANCO, "lm")
        y += 80
    L.d.line([(s(ox + x0), s(y)), (s(ox + x1), s(y))], fill=ACENTO2 + (170,), width=s(1))
    # Lockup grande
    L.lockup(n, 360, 580, 70, CLARO2)

    for k in range(1, N + 1):
        L.pie(k)

    errores = L.verificar()
    final = L.img.resize((W, H), Image.Resampling.LANCZOS)
    previa.mkdir(parents=True, exist_ok=True)
    final.resize((W // 4, H // 4), Image.Resampling.LANCZOS).save(previa / "panorama_preview.png")
    if errores:
        sys.exit("Errores de diseño:\n" + "\n".join(errores))
    salida.mkdir(parents=True, exist_ok=True)
    final.save(previa / "panorama_hackathon.png")
    for k in range(N):
        final.crop((k * SW, 0, (k + 1) * SW, H)).save(salida / f"slide_{k + 1}.png")
    print("ok:", ", ".join(f"slide_{k + 1}.png" for k in range(N)))


if __name__ == "__main__":
    main()
