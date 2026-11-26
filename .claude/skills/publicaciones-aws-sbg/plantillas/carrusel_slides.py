"""Carrusel "Explorando Skill Builder" — 5 slides independientes 3:4 (1080x1440), paleta morada del grupo.

Uso: python carrusel_skillbuilder.py <carpeta_fotos> <carpeta_salida>
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
W, H = 1080, 1440
M = 90
N = 5

# Paleta del grupo (morado)
SQUID = (24, 19, 44)        # fondo arriba
SQUID_OSC = (14, 16, 28)    # fondo abajo
NARANJA = (174, 92, 255)    # acento morado #AE5CFF (se conserva el nombre de la variable)
NARANJA_CLARO = (198, 152, 255)
BLANCO = (245, 246, 248)
GRIS = (170, 178, 190)
GRIS_OSC = (84, 96, 112)

DISPLAY = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
INTER = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
INTER_M = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
INTER_SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
INTER_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
LOGO_SBG = _comun.LOGO_SBG

_cache = {}


def s(v):
    return int(round(v * S))


def F(ruta, tam):
    if (ruta, tam) not in _cache:
        _cache[(ruta, tam)] = ImageFont.truetype(ruta, s(tam))
    return _cache[(ruta, tam)]


def logo_naranja(lado):
    """El chip del grupo con sus colores originales."""
    logo = Image.open(LOGO_SBG).convert("RGBA")
    return ImageOps.contain(logo, (s(lado), s(lado)), Image.Resampling.LANCZOS)


class Slide:
    def __init__(self, n, seccion, carpeta):
        self.n, self.carpeta = n, carpeta
        self.img = self._fondo()
        self.d = ImageDraw.Draw(self.img, "RGBA")
        self.textos, self.fotos = [], []
        self._cuadricula()
        self._cabecera(seccion)
        self._pie()

    def _fondo(self):
        col = Image.new("RGB", (1, H))
        for y in range(H):
            t = y / H
            col.putpixel((0, y), tuple(round(a + (b - a) * t) for a, b in zip(SQUID, SQUID_OSC)))
        img = col.resize((s(W), s(H)), Image.Resampling.NEAREST)
        k = 8
        brillos = [(1000, 120, 420, 0.16), (60, 1380, 380, 0.10)] if self.n % 2 else \
                  [(80, 140, 400, 0.14), (1020, 1360, 400, 0.12)]
        for cx, cy, r, a in brillos:
            m = Image.new("L", (W // k, H // k), 0)
            ImageDraw.Draw(m).ellipse([(cx - r) / k, (cy - r) / k, (cx + r) / k, (cy + r) / k], fill=int(255 * a))
            m = m.filter(ImageFilter.GaussianBlur(r / k * 0.55)).resize(img.size, Image.Resampling.BILINEAR)
            img.paste(Image.new("RGB", img.size, NARANJA), (0, 0), m)
        return img

    def _cuadricula(self):
        for x in range(0, W + 1, 60):
            self.d.line([(s(x), 0), (s(x), s(H))], fill=(255, 255, 255, 13), width=s(1))
        for y in range(0, H + 1, 60):
            self.d.line([(0, s(y)), (s(W), s(y))], fill=(255, 255, 255, 13), width=s(1))
        # Píxeles decorativos (como en el arte del evento), fuera de las zonas de texto
        for x, y, c in [(960, 30, NARANJA), (1020, 30, BLANCO + (160,)), (1020, 0, NARANJA + (120,)),
                        ]:
            self.d.rectangle([s(x + 6), s(y + 6), s(x + 54), s(y + 54)], fill=c)

    def _cabecera(self, seccion):
        lado = 48
        logo = logo_naranja(lado)
        self.img.paste(logo, (s(M), s(104) - logo.height // 2), logo)
        self.t(M + lado + 16, 104, "AWS STUDENT BUILDER GROUP · ITD", F(INTER_B, 18), BLANCO, "lm")
        self.t(W - M, 104, seccion.upper(), F(INTER_B, 18), NARANJA, "rm")
        self.d.line([(s(M), s(146)), (s(W - M), s(146))], fill=BLANCO, width=s(2))
        self.d.line([(s(M), s(152)), (s(W - M), s(152))], fill=NARANJA, width=s(1))

    def _pie(self):
        self.d.line([(s(M), s(1352)), (s(W - M), s(1352))], fill=GRIS_OSC, width=s(1))
        self.t(M, 1384, "Explorando Skill Builder  —  30 de septiembre", F(INTER_M, 19), GRIS, "lm")
        self.t(W - M, 1384, f"{self.n} / {N}" + ("  →" if self.n < N else ""), F(INTER_B, 19), BLANCO, "rm")

    # -------------------------------------------------------------- primitivas
    def t(self, x, y, texto, f, color=BLANCO, anchor="la"):
        self.d.text((s(x), s(y)), texto, font=f, fill=color, anchor=anchor)
        b = self.d.textbbox((s(x), s(y)), texto, font=f, anchor=anchor)
        self.textos.append((texto[:28], b[0] / S, b[1] / S, b[2] / S, b[3] / S))

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

    def parrafo(self, x, y, texto, ruta, tam, max_w, color=GRIS, inter=1.42):
        for linea in self.envolver(texto, F(ruta, tam), max_w):
            self.t(x, y, linea, F(ruta, tam), color)
            y += tam * inter
        return y

    def titulo(self, l1, l2, y=188, tam=96):
        for linea in (l1, l2):
            while self.ancho(linea, F(DISPLAY, tam)) > W - 2 * M:
                tam -= 2
        self.t(M, y, l1, F(DISPLAY, tam), BLANCO)
        self.t(M, y + tam * 1.02, l2, F(DISPLAY, tam), NARANJA)
        return y + tam * 2.4

    def foto(self, nombre, x, y, h):
        f = ImageOps.exif_transpose(Image.open(self.carpeta / nombre)).convert("RGB")
        w = round(h * f.width / f.height)
        # sombra naranja desplazada, como bloque de píxel
        self.d.rectangle([s(x + 12), s(y + 12), s(x + w + 12), s(y + h + 12)], fill=NARANJA)
        self.img.paste(f.resize((s(w), s(h)), Image.Resampling.LANCZOS), (s(x), s(y)))
        self.d.rectangle([s(x), s(y), s(x + w), s(y + h)], outline=BLANCO, width=s(2))
        self.fotos.append((nombre, x, y, x + w + 12, y + h + 12))
        return w

    def ancho_foto(self, nombre, h):
        with Image.open(self.carpeta / nombre) as f:
            f = ImageOps.exif_transpose(f)
            return round(h * f.width / f.height)

    def fila(self, nombres, y, h=None, x0=M, x1=W - M, gap=30):
        props = []
        for nombre in nombres:
            with Image.open(self.carpeta / nombre) as f:
                f = ImageOps.exif_transpose(f)
                props.append(f.width / f.height)
        disponible = x1 - x0 - gap * (len(nombres) - 1) - 12
        alto = disponible / sum(props) if h is None else min(h, disponible / sum(props))
        total = alto * sum(props) + gap * (len(nombres) - 1) + 12
        x = x0 + (x1 - x0 - total) / 2
        for nombre, p in zip(nombres, props):
            self.foto(nombre, x, y, alto)
            x += alto * p + gap
        return y + alto + 12

    def chip(self, x, y, texto):
        f = F(INTER_B, 22)
        w = self.ancho(texto, f) + 36
        self.d.rectangle([s(x), s(y), s(x + w), s(y + 48)], fill=NARANJA)
        self.t(x + 18, y + 24, texto, f, SQUID, "lm")
        return w

    def verificar(self):
        errores = []
        for t, x0, y0, x1, y1 in self.textos:
            if x0 < 80 or x1 > W - 80 or y0 < 80 or y1 > H - 30:
                errores.append(f"slide {self.n}: '{t}' fuera del margen ({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f})")
            for nombre, fx0, fy0, fx1, fy1 in self.fotos:
                if x0 < fx1 + 8 and x1 > fx0 - 8 and y0 < fy1 + 8 and y1 > fy0 - 8:
                    errores.append(f"slide {self.n}: '{t}' encima de {nombre}")
        for i, (nombre, x0, y0, x1, y1) in enumerate(self.fotos):
            if x0 < 80 or x1 > W - 80 or y0 < 170 or y1 > 1335:
                errores.append(f"slide {self.n}: foto {nombre} fuera del área ({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f})")
            for otra in self.fotos[i + 1:]:
                if x0 < otra[3] and x1 > otra[1] and y0 < otra[4] and y1 > otra[2]:
                    errores.append(f"slide {self.n}: {nombre} se encima con {otra[0]}")
        return errores

    def guardar(self, ruta):
        self.img.resize((W, H), Image.Resampling.LANCZOS).save(ruta)


def main():
    carpeta, salida = Path(sys.argv[1]), Path(sys.argv[2])
    slides = []

    # 1 · Portada
    sl = Slide(1, "Recap", carpeta)
    sl.t(M, 196, "RECAP DE LA ACTIVIDAD", F(INTER_B, 22), NARANJA)
    sl.t(M, 236, "Explorando", F(DISPLAY, 128), BLANCO)
    sl.t(M, 370, "Skill Builder", F(DISPLAY, 128), NARANJA)
    sl.t(M, 532, "30 de septiembre  ·  Instituto Tecnológico de Durango", F(INTER_M, 26), GRIS)
    sl.fila(["foto_02.jpg"], 610)
    slides.append(sl)

    # 2 · La charla
    sl = Slide(2, "La charla", carpeta)
    y = sl.titulo("Tu perfil puede", "contar una historia")
    puntos = [
        ("AWS Skill Builder", "La plataforma de AWS para aprender la nube en línea y a tu ritmo."),
        ("Certificaciones de AWS", "Una meta para estudiar y una prueba visible de tus habilidades."),
        ("CV con evidencia", "Rumbo claro para estudiar, confianza al hablar y algo que contar en entrevistas."),
    ]
    y += 6
    for titulo, detalle in puntos:
        sl.d.rectangle([s(M), s(y + 6), s(M + 18), s(y + 24)], fill=NARANJA)
        sl.t(M + 40, y, titulo, F(INTER_B, 30), BLANCO)
        y = sl.parrafo(M + 40, y + 44, detalle, INTER, 23, W - 2 * M - 40) + 22
    alto_fila = (W - 2 * M - 30 - 12) / (2 * 4 / 3)
    sl.fila(["foto_01.jpg", "foto_09.jpg"], y + 16 + max(0, (1322 - y - 16 - alto_fila - 12) / 2))
    slides.append(sl)

    # 3 · Trivia
    sl = Slide(3, "Dinámica", carpeta)
    y = sl.titulo("Trivia", "por equipos")
    y = sl.parrafo(M, y, "Pusimos a prueba lo aprendido: preguntas sobre la nube, turnos por equipo y puntos en juego.",
                   INTER, 25, W - 2 * M) + 20
    sl.chip(M, y, "¿Qué hace un servidor?")
    sl.fila(["foto_05.jpg", "foto_08.jpg"], y + 90, x0=M, x1=W - M)
    slides.append(sl)

    # 4 · Snacks
    sl = Slide(4, "Convivencia", carpeta)
    y = sl.titulo("Hecho por", "el equipo")
    y = sl.parrafo(M, y, "Sándwiches, donas, papitas y bebidas: el staff preparó todo para recargar energía.",
                   INTER, 25, W - 2 * M) + 24
    fin = sl.fila(["foto_06.jpg", "foto_07.jpg"], y, h=430)
    sl.fila(["foto_03.jpg", "foto_04.jpg"], fin + 26, h=1322 - fin - 26 - 12)
    slides.append(sl)

    # 5 · Cierre
    sl = Slide(5, "Gracias", carpeta)
    y = sl.titulo("¡Gracias", "por venir!", tam=110)
    y = sl.parrafo(M, y, "A todos los builders que se sumaron a explorar AWS Skill Builder con nosotros.",
                   INTER_M, 28, W - 2 * M, BLANCO) + 60
    sl.t(M, y, "TU SIGUIENTE PASO", F(INTER_B, 20), NARANJA)
    y += 50
    pasos = ["Crea tu cuenta en AWS Skill Builder", "Elige tu primera ruta de aprendizaje",
             "Síguenos en Instagram para la próxima"]
    for i, paso in enumerate(pasos, 1):
        sl.d.line([(s(M), s(y)), (s(W - M), s(y))], fill=NARANJA + (170,), width=s(1))
        sl.t(M, y + 46, f"0{i}", F(DISPLAY, 36), NARANJA, "lm")
        sl.t(M + 84, y + 46, paso, F(INTER_M, 30), BLANCO, "lm")
        y += 92
    sl.d.line([(s(M), s(y)), (s(W - M), s(y))], fill=NARANJA + (170,), width=s(1))
    # Bloque de píxeles + chip grande
    logo = logo_naranja(150)
    sl.img.paste(logo, (s(W - M - 150), s(1170)), logo)
    for i, (dx, dy) in enumerate([(0, 0), (60, 0), (0, 60), (120, 60), (60, 120)]):
        c = NARANJA if i % 2 == 0 else BLANCO + (170,)
        sl.d.rectangle([s(M + dx), s(1180 + dy), s(M + dx + 48), s(1180 + dy + 48)], fill=c)
    slides.append(sl)

    errores = [e for sl in slides for e in sl.verificar()]
    if errores:
        sys.exit("Errores de diseño:\n" + "\n".join(errores))
    salida.mkdir(parents=True, exist_ok=True)
    for sl in slides:
        ruta = salida / f"skillbuilder_slide_{sl.n}.png"
        sl.guardar(ruta)
        print("Guardada:", ruta)


if __name__ == "__main__":
    main()
