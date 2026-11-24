"""Genera la voz en off por frases y un mapa de tiempos para los subtítulos.

Cada frase: (subtítulo, texto_para_la_voz | None). *palabra* = resaltada en pantalla.
"""
import json, os, subprocess, sys

PROJ = sys.argv[1]
WORK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tts")
os.makedirs(WORK, exist_ok=True)
ENV = dict(os.environ, HYPERFRAMES_PYTHON=os.path.join(os.path.dirname(os.path.abspath(__file__)), "tts-venv/bin/python"))
VOICE = "ef_dora"
GAP = 0.22

SCENES = [
    (0, 8, 0.7, [
        ("Una hamburguesería de *California*", None),
        ("se convirtió en la cadena de comida rápida", None),
        ("*más grande del mundo.*", None),
    ]),
    (8, 25, 0.6, [
        ("En *1937,* los hermanos Richard y Maurice McDonald", "En mil novecientos treinta y siete, los hermanos Richard y Maurice Mac Dónald"),
        ("abrieron un puesto de *hot dogs*", "abrieron un puesto de jot dogs"),
        ("cerca de Los Ángeles.", None),
        ("En *1940* lo llevaron a *San Bernardino*", "En mil novecientos cuarenta lo llevaron a San Bernardino"),
        ("y lo convirtieron en un *restaurante de carretera,*", None),
        ("con meseras que servían en los autos.", None),
    ]),
    (25, 45, 0.6, [
        ("En *1948* cerraron unos meses", "En mil novecientos cuarenta y ocho cerraron unos meses"),
        ("y reorganizaron todo el negocio.", None),
        ("Redujeron el menú a *nueve productos*", None),
        ("y montaron una *cocina en línea:*", None),
        ("cada empleado hacía *un solo paso.*", None),
        ("Lo llamaron *Speedee Service System.*", "Lo llamaron Spídi Sérvis Sístem."),
        ("Una hamburguesa costaba *quince centavos.*", None),
    ]),
    (45, 70, 0.6, [
        ("En *1954* apareció *Ray Kroc,*", "En mil novecientos cincuenta y cuatro apareció Rei Krok,"),
        ("un vendedor de *máquinas para batidos.*", None),
        ("Le intrigó que un solo restaurante", None),
        ("comprara tantas máquinas.", None),
        ("Se asoció con los hermanos", None),
        ("para *vender franquicias*", None),
        ("y en *1955* abrió su local en Des Plaines, Illinois.", "y en mil novecientos cincuenta y cinco abrió su local en Des Pléins, Ilinói."),
        ("En pocos años, la cadena llegó", None),
        ("a *cientos de restaurantes.*", None),
    ]),
    (70, 100, 0.6, [
        ("Primero cubrió *Estados Unidos:*", None),
        ("mil locales en *1968.*", "mil locales en mil novecientos sesenta y ocho."),
        ("En *1967* cruzó a *Canadá* y *Puerto Rico.*", "En mil novecientos sesenta y siete cruzó a Canadá y Puerto Rico."),
        ("En *1971* llegó a *Japón,* Europa y Australia.", "En mil novecientos setenta y uno llegó a Japón, Europa y Australia."),
        ("En *1990,* a *Moscú* y a *China.*", "En mil novecientos noventa, a Moscú y a China."),
        ("En cada país adaptó el menú:", None),
        ("hamburguesa *teriyaki* en Japón,", None),
        ("el *Maharaja Mac,* sin carne de res, en India,", "el Majarajá Mak, sin carne de res, en India,"),
        ("y la *McArabia* en Medio Oriente.", "y la Mak Arabia en Medio Oriente."),
        ("Hoy supera los *40 000* locales.", "Hoy supera los cuarenta mil locales."),
    ]),
    (100, 110, 0.4, [
        ("En *1961,* Kroc compró los derechos", "En mil novecientos sesenta y uno, Krok compró los derechos"),
        ("por *2,7 millones* de dólares.", "por dos coma siete millones de dólares."),
        ("La familia habla de un trato incumplido;", None),
        ("la empresa, de una compra legal.", None),
    ]),
    (110, 120, 1.2, [
        ("Una idea de *cocina simple*", None),
        ("cambió la forma de *comer en el mundo.*", None),
        ("¿Y tú? ¿*Qué idea simple* cambiarías?", "¿Y tú? ¿Qué idea simple cambiarías?"),
    ]),
]


def dur(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).decode())


def tts(text, path, speed):
    subprocess.run(["npx", "hyperframes", "tts", text, "-v", VOICE, "-s", f"{speed:.2f}", "-o", path],
                   check=True, env=ENV, cwd=WORK, capture_output=True)


cues, clips = [], []
for si, (s0, s1, lead, lines) in enumerate(SCENES):
    speed = 1.0
    while True:
        items = []
        for li, (cap, voice) in enumerate(lines):
            p = os.path.join(WORK, f"s{si}_{li}_{speed:.2f}.wav")
            if not os.path.exists(p):
                tts(voice or cap.replace("*", ""), p, speed)
            items.append((cap, p, dur(p)))
        total = lead + sum(d for _, _, d in items) + GAP * (len(items) - 1)
        if s0 + total <= s1 - 0.35 or speed >= 1.3:
            break
        speed = round(speed + 0.05, 2)
    t = s0 + lead
    for cap, p, d in items:
        cues.append({"start": round(t, 3), "end": round(t + d, 3), "text": cap, "scene": si})
        clips.append((p, t))
        t += d + GAP
    print(f"escena {si + 1}: velocidad {speed}, termina en {t - GAP:.2f}s (límite {s1})")

# Mezcla en una sola pista de 120 s
os.makedirs(os.path.join(PROJ, "assets"), exist_ok=True)
args = ["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-t", "120", "-i", "anullsrc=r=24000:cl=mono"]
for p, _ in clips:
    args += ["-i", p]
fl = "".join(f"[{i + 1}]adelay={int(t * 1000)}:all=1[a{i}];" for i, (_, t) in enumerate(clips))
fl += "[0]" + "".join(f"[a{i}]" for i in range(len(clips))) + f"amix=inputs={len(clips) + 1}:normalize=0,atrim=0:120[out]"
args += ["-filter_complex", fl, "-map", "[out]", "-ar", "48000", "-ac", "2", os.path.join(PROJ, "assets/narracion.wav")]
subprocess.run(args, check=True)
with open(os.path.join(PROJ, "assets/narracion.js"), "w") as f:
    f.write("window.NARR = " + json.dumps(cues, ensure_ascii=False) + ";\n")
print("cues:", len(cues))
