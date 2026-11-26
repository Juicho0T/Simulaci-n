"""Carrusel "Claude Code en Amazon Bedrock", estilo editorial (revista) en versión oscura.

Fondo oscuro de la paleta, titulares serif, fotos con pie de foto y números grandes en morado.
Uso: python carrusel_claude_v4.py <carpeta_fotos> <carpeta_salida>
"""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
import _comun  # noqa: E402  (fuentes y logos portables)
from _comun import LOGO_ACISTI, PATRO  # noqa: E402


import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

S = 2
W, H = 1080, 1440
M = 90
MIN_MARGEN = 80
TOTAL = 5

PAPEL = (21, 28, 38)            # fondo: #151C26 de la paleta
TINTA = (240, 242, 247)         # texto principal claro
TARJETA = (32, 27, 52)          # bloque de llamada a la acción
TINTA_SUAVE = (176, 184, 200)
GRIS = (130, 138, 154)
ACENTO = (174, 92, 255)         # #AE5CFF
ACENTO_OSCURO = (198, 152, 255)  # morado claro para texto pequeño sobre fondo oscuro
LILA = (40, 32, 66)              # relleno morado oscuro (números y recuadros)
LOGO = _comun.LOGO_SBG

SERIF_B = "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf"
SERIF_BI = "/usr/share/fonts/truetype/crosextra/Caladea-BoldItalic.ttf"
SERIF_I = "/usr/share/fonts/truetype/crosextra/Caladea-Italic.ttf"
INTER = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
INTER_M = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
INTER_SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
INTER_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
DISPLAY = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"

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


class Slide:
    def __init__(self, n, seccion):
        self.n = n
        self.img = Image.new("RGB", (s(W), s(H)), PAPEL)
        self.d = ImageDraw.Draw(self.img, "RGBA")
        self.textos, self.fotos = [], []
        self._cabecera(seccion)
        self._pie()

    def _cabecera(self, seccion):
        lado = 40
        logo = Image.open(LOGO).convert("RGBA")
        logo.thumbnail((s(lado), s(lado)), Image.Resampling.LANCZOS)
        self.img.paste(logo.convert("RGB"), (s(M), s(84) + (s(lado) - logo.height) // 2), logo.getchannel("A"))
        self.t(M + lado + 16, 104, "AWS STUDENT BUILDER GROUP", F(INTER_B, 19), TINTA, "lm")
        self.t(W - M, 104, seccion.upper(), F(INTER_SB, 19), ACENTO_OSCURO, "rm")
        self.d.line([(s(M), s(140)), (s(W - M), s(140))], fill=TINTA, width=s(2))
        self.d.line([(s(M), s(146)), (s(W - M), s(146))], fill=TINTA, width=s(1))

    def _pie(self):
        self.d.line([(s(M), s(1352)), (s(W - M), s(1352))], fill=TINTA, width=s(1))
        self.t(M, 1380, "Taller  —  Claude Code en Amazon Bedrock", F(SERIF_I, 21), TINTA_SUAVE, "lm")
        self.t(W - M, 1380, f"{self.n} / {TOTAL}" + ("  →" if self.n < TOTAL else ""), F(INTER_SB, 20), TINTA, "rm")

    # primitivas
    def t(self, x, y, texto, f, color=TINTA, anchor="la", **kw):
        self.d.text((s(x), s(y)), texto, font=f, fill=color, anchor=anchor, **kw)
        b = self.d.textbbox((s(x), s(y)), texto, font=f, anchor=anchor, **kw)
        self.textos.append((texto[:24], b[0] / S, b[1] / S, b[2] / S, b[3] / S))

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

    def parrafo(self, x, y, texto, ruta, tam, max_w, color=TINTA_SUAVE, inter=1.38):
        for linea in self.envolver(texto, F(ruta, tam), max_w):
            self.t(x, y, linea, F(ruta, tam), color)
            y += tam * inter
        return y

    def foto(self, ruta, x, y, w, pie, n_fig):
        """Foto con marco fino de tinta y pie de foto en itálica debajo. Devuelve la y final del pie."""
        f = Image.open(ruta).convert("RGB")
        h = round(w * f.height / f.width)
        self.img.paste(f.resize((s(w), s(h)), Image.Resampling.LANCZOS), (s(x), s(y)))
        self.d.rectangle([s(x), s(y), s(x + w), s(y + h)], outline=(92, 100, 120), width=s(2))
        self.fotos.append((ruta.name, x, y, x + w, y + h))
        fy = y + h + 12
        self.t(x, fy, f"Fig. {n_fig}", F(INTER_B, 17), ACENTO_OSCURO)
        dx = self.ancho(f"Fig. {n_fig}  ", F(INTER_B, 17))
        lineas = self.envolver(pie, F(SERIF_I, 19), w - dx)
        for i, linea in enumerate(lineas):
            self.t(x + dx, fy - 2 + i * 24, linea, F(SERIF_I, 19), TINTA_SUAVE)
        return fy + 24 * len(lineas)

    def numero(self, x, y, texto, tam=190):
        """Número grande decorativo con contorno morado (anclado arriba a la derecha)."""
        f = F(DISPLAY, tam)
        self.d.text((s(x), s(y)), texto, font=f, fill=LILA, anchor="ra", stroke_width=s(3), stroke_fill=ACENTO)
        b = self.d.textbbox((s(x), s(y)), texto, font=f, anchor="ra", stroke_width=s(3))
        self.textos.append((texto, b[0] / S, b[1] / S, b[2] / S, b[3] / S))

    def verificar(self):
        errores = []
        for t, x0, y0, x1, y1 in self.textos:
            if x0 < MIN_MARGEN or y0 < MIN_MARGEN - 10 or x1 > W - MIN_MARGEN or y1 > H - 30:
                errores.append(f"slide {self.n}: '{t}' fuera del margen ({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f})")
            for nombre, fx0, fy0, fx1, fy1 in self.fotos:
                if x0 < fx1 and x1 > fx0 and y0 < fy1 and y1 > fy0:
                    errores.append(f"slide {self.n}: '{t}' encima de {nombre}")
        for i, a in enumerate(self.fotos):
            if a[1] < MIN_MARGEN or a[3] > W - MIN_MARGEN or a[4] > 1340:
                errores.append(f"slide {self.n}: foto {a[0]} fuera del área")
            for b in self.fotos[i + 1:]:
                if a[1] < b[3] and a[3] > b[1] and a[2] < b[4] and a[4] > b[2]:
                    errores.append(f"slide {self.n}: {a[0]} se encima con {b[0]}")
        return errores

    def guardar(self, ruta):
        self.img.resize((W, H), Image.Resampling.LANCZOS).save(ruta)


def main():
    fotos, salida = Path(sys.argv[1]), Path(sys.argv[2])
    salida.mkdir(parents=True, exist_ok=True)
    slides = []

    # 1 ── Portada: titular serif a la izquierda, foto vertical a la derecha, foto grande abajo
    sl = Slide(1, "Taller")
    col = 520
    y = 184
    sl.t(M, y, "TALLER PRÁCTICO", F(INTER_B, 20), ACENTO_OSCURO)
    y += 46
    for linea in ("Claude Code", "en Amazon"):
        sl.t(M, y, linea, F(SERIF_B, 84), TINTA)
        y += 86
    sl.t(M, y, "Bedrock", F(SERIF_BI, 84), ACENTO)
    y += 108
    sl.d.rectangle([s(M), s(y), s(M + 70), s(y + 5)], fill=ACENTO)
    y += 26
    fin_txt = sl.parrafo(M, y, "Construye, programa y automatiza con Claude Code usando Amazon Bedrock.",
                         INTER_M, 25, col, TINTA_SUAVE, 1.35)
    w22 = 300
    fin22 = sl.foto(fotos / "22.webp", W - M - w22, 184, w22, "Mentoría uno a uno.", 1)
    top16 = max(fin_txt, fin22) + 34
    h16 = 1300 - top16
    w16 = min(W - 2 * M, round(h16 * 4 / 3))
    sl.foto(fotos / "16.webp", (W - w16) // 2, top16, w16, "Arranque del taller en el laboratorio de cómputo.", 2)
    slides.append(sl)

    MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

    def titulo(sl, num, l1, l2):
        sl.numero(W - M, 168, num)
        sl.t(M, 196, l1, F(SERIF_B, 76), TINTA)
        sl.t(M, 278, l2, F(SERIF_BI, 76), ACENTO)

    # 2 ── Lo que vimos: temas a todo el ancho; abajo, recuadro de CLAUDE.md y foto
    sl = Slide(2, "Lo que vimos")
    titulo(sl, "02", "Lo que", "vimos")
    y = 410
    temas = [
        ("I.", "Claude Code + Amazon Bedrock",
         "Un asistente de programación con IA en la terminal, con los modelos de Claude a través de Amazon Bedrock."),
        ("II.", "CLAUDE.md, la memoria del proyecto",
         "Instrucciones por niveles —usuario, repositorio y submódulos— para que Claude Code entienda tu código."),
        ("III.", "Estándares de equipo",
         "Convenciones compartidas para que la IA programe con las mismas reglas que todo el equipo."),
    ]
    for num, tit, detalle in temas:
        sl.t(M, y, num, F(SERIF_BI, 30), ACENTO_OSCURO)
        y = sl.parrafo(M + 62, y, tit, SERIF_B, 32, W - 2 * M - 62, TINTA, 1.12) + 6
        y = sl.parrafo(M + 62, y, detalle, INTER, 23, W - 2 * M - 62) + 26
    top = y + 6
    h18 = 1296 - top
    w18 = round(h18 * 0.75)
    sl.foto(fotos / "18.webp", W - M - w18, top, w18, "CLAUDE.md, explicado en pizarra.", 3)
    colw = W - 2 * M - w18 - 30
    arbol = [("~/.claude/CLAUDE.md", "usuario"), ("repo/CLAUDE.md", "proyecto"),
             ("├─ frontend/CLAUDE.md", ""), ("├─ backend/CLAUDE.md", ""), ("└─ tests/CLAUDE.md", "submódulos")]
    sl.d.rectangle([s(M), s(top), s(M + colw), s(top + h18)], fill=LILA)
    sl.d.rectangle([s(M), s(top), s(M + 6), s(top + h18)], fill=ACENTO)
    temas_extra = ["Skills", "Plugins", "Planificación de tareas",
                   "Trabajo en paralelo con múltiples sesiones", "Manejo de memoria"]
    paso_a, paso_t = 31, 34
    ancho_txt = colw - 28 - 46
    lineas_t = [sl.envolver(x, F(INTER_M, 20), ancho_txt) for x in temas_extra]
    alto_cont = 36 + len(arbol) * paso_a + 34 + 36 + sum(len(l) for l in lineas_t) * 26 + (len(temas_extra) - 1) * 8
    yy = top + (h18 - alto_cont) / 2
    sl.t(M + 28, yy, "NIVELES DE CLAUDE.md", F(INTER_B, 17), ACENTO_OSCURO)
    yy += 36
    for ruta, nota in arbol:
        sl.t(M + 28, yy, ruta, F(MONO_B if not ruta.startswith(("├", "└")) else MONO, 17), TINTA)
        if nota:
            sl.t(M + colw - 20, yy + 1, nota, F(SERIF_I, 16), TINTA_SUAVE, "ra")
        yy += paso_a
    yy += 12
    sl.d.line([(s(M + 28), s(yy)), (s(M + colw - 20), s(yy))], fill=(84, 70, 130), width=s(1))
    yy += 22
    sl.t(M + 28, yy, "TAMBIÉN VIMOS", F(INTER_B, 17), ACENTO_OSCURO)
    yy += 36
    for lineas in lineas_t:
        sl.d.rectangle([s(M + 30), s(yy + 7), s(M + 40), s(yy + 17)], fill=ACENTO)
        for k, linea in enumerate(lineas):
            sl.t(M + 28 + 46 - 24, yy + k * 26, linea, F(INTER_M, 20), TINTA)
        yy += len(lineas) * 26 + 8
    if yy > top + h18 - 10:
        sys.exit("El recuadro de la slide 2 no cabe")
    slides.append(sl)

    # 3 ── Manos a la obra: dos fotos en fila y dos columnas de texto
    sl = Slide(3, "Manos a la obra")
    titulo(sl, "03", "Manos", "a la obra")
    hueco = 24
    h = (W - 2 * M - hueco) / (0.75 + 4 / 3)
    w17, w23 = round(h * 0.75), round(h * 4 / 3)
    top = 450
    fin = sl.foto(fotos / "17.webp", M, top, w17, "Labs guiados en el laboratorio.", 4)
    fin = max(fin, sl.foto(fotos / "23.webp", W - M - w23, top, w23, "Dudas resueltas en vivo.", 5))
    y = fin + 60
    sl.d.line([(s(M), s(y)), (s(W - M), s(y))], fill=TINTA, width=s(1))
    y += 30
    practicas = [
        ("Labs guiados", "Cada asistente trabajó en su propia computadora, acompañado por los instructores."),
        ("CLAUDE.md en un repo real", "Escribimos instrucciones para que Claude Code entienda el proyecto desde el primer prompt."),
    ]
    cw = (W - 2 * M - 40) / 2
    for i, (tit, detalle) in enumerate(practicas):
        cx = M + i * (cw + 40)
        sl.t(cx, y, f"0{i + 1}", F(INTER_B, 20), ACENTO_OSCURO)
        yy = sl.parrafo(cx, y + 38, tit, SERIF_B, 36, cw, TINTA, 1.1) + 10
        sl.parrafo(cx, yy, detalle, INTER, 26, cw, TINTA_SUAVE, 1.4)
    slides.append(sl)

    # 4 ── Lo que construimos: los dos juegos en grande
    sl = Slide(4, "Proyectos")
    titulo(sl, "04", "Lo que", "construimos")
    y = sl.parrafo(M, 410, "Juegos en 3D que corren en el navegador, construidos con Claude Code durante el taller.",
                   INTER_M, 25, W - 2 * M, TINTA_SUAVE, 1.35) + 24
    hueco = 28
    h = min(1296 - y, (W - 2 * M - hueco) / (2 * 720 / 1280))
    w = round(h * 720 / 1280)
    x0 = (W - (2 * w + hueco)) / 2
    sl.foto(fotos / "19.webp", x0, y, w, "Ajedrez 3D.", 6)
    sl.foto(fotos / "21.webp", x0 + w + hueco, y, w, "2048 en 3D.", 7)
    slides.append(sl)

    # 5 ── Cierre: gran agradecimiento, fotos y bloque de llamada a la acción
    sl = Slide(5, "Gracias")
    sl.numero(W - M, 168, "05")
    sl.t(M, 196, "¡Gracias", F(SERIF_B, 84), TINTA)
    sl.t(M, 286, "por asistir!", F(SERIF_BI, 84), ACENTO)
    y = sl.parrafo(M, 410, "Gracias a los instructores y a todos los builders que programaron con nosotros.",
                   INTER_M, 25, W - 2 * M, TINTA_SUAVE, 1.35) + 20
    hueco = 24
    h = (W - 2 * M - hueco) / (1280 / 720 + 0.75)
    w20, w24 = round(h * 1280 / 720), round(h * 0.75)
    yf = sl.foto(fotos / "20.webp", M, y, w20, "Así se vio el laboratorio durante el taller.", 8)
    yf = max(yf, sl.foto(fotos / "24.webp", W - M - w24, y, w24, "Builders atentos.", 9))
    top = yf + 32
    alto = 1325 - top
    bx1 = W - M
    sl.d.rectangle([s(M), s(top), s(bx1), s(top + alto)], fill=TARJETA, outline=ACENTO, width=s(2))
    pad = 34
    ancho_int = bx1 - M - 2 * pad
    n_tit = len(sl.envolver("Síguenos para el próximo taller", F(SERIF_B, 40), ancho_int))
    n_desc = len(sl.envolver("Activa las notificaciones y comparte este post con quien quiera programar con IA.",
                             F(INTER, 22), ancho_int))
    contenido = 38 + n_tit * 44 + 14 + n_desc * 22 * 1.38 + 30 + 56
    yy = top + (alto - contenido) / 2
    sl.t(M + pad, yy, "PRÓXIMAMENTE", F(INTER_B, 18), ACENTO)
    yy += 38
    yy = sl.parrafo(M + pad, yy, "Síguenos para el próximo taller", SERIF_B, 40, ancho_int, TINTA, 1.1) + 14
    yy = sl.parrafo(M + pad, yy, "Activa las notificaciones y comparte este post con quien quiera programar con IA.",
                    INTER, 22, ancho_int, TINTA_SUAVE, 1.38)
    fb = F(INTER_B, 21)
    texto_b = "SÍGUENOS PARA MÁS  →"
    bw = sl.ancho(texto_b, fb) + 52
    by = yy + 30
    sl.d.rectangle([s(M + pad), s(by), s(M + pad + bw), s(by + 56)], fill=ACENTO)
    sl.t(M + pad + bw / 2, by + 28, texto_b, fb, PAPEL, "mm")
    if by + 56 > top + alto - 10:
        sys.exit("El bloque de llamada a la acción no cabe")
    slides.append(sl)

    errores = [e for sl in slides for e in sl.verificar()]
    if errores:
        sys.exit("Errores de diseño:\n" + "\n".join(errores))
    for sl in slides:
        ruta = salida / f"slide_{sl.n}.png"
        sl.guardar(ruta)
        print("Guardada:", ruta, [(f[0], f[3] - f[1], f[4] - f[2]) for f in sl.fotos])


if __name__ == "__main__":
    main()
