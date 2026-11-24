"""Voz en off con ElevenLabs (una petición por escena, con tiempos por carácter).

Uso: python3 tools/elevenlabs.py <carpeta_del_proyecto> [voice_id]
La clave la inyecta el proxy del entorno (cabecera xi-api-key); aquí no se guarda ninguna.
Genera assets/narracion.wav y assets/narracion.js (tiempos de cada frase para los subtítulos).
"""
import base64, json, os, subprocess, sys, urllib.request

PROJ = sys.argv[1]
VOICE = sys.argv[2] if len(sys.argv) > 2 else "nPczCjzI2devNBz1zQrb"  # Brian
MODEL = "eleven_multilingual_v2"
CACHE = os.path.join(PROJ, ".hyperframes", "elevenlabs")
os.makedirs(CACHE, exist_ok=True)

# (inicio, fin, retardo inicial, frases). Frase = (subtítulo, texto_para_la_voz | None); *x* = resaltado.
SCENES = [
    (0, 8, 0.5, [
        ("Una hamburguesería de *California*", None),
        ("se convirtió en la cadena de comida rápida", None),
        ("*más grande del mundo.*", None),
    ]),
    (8, 25, 0.5, [
        ("En *1937,* los hermanos Richard y Maurice McDonald", None),
        ("abrieron un puesto de *hot dogs*", None),
        ("cerca de Los Ángeles.", None),
        ("En *1940* lo llevaron a *San Bernardino*", None),
        ("y lo convirtieron en un *restaurante de carretera,*", None),
        ("con meseras que servían en los autos.", None),
    ]),
    (25, 45, 0.5, [
        ("En *1948* cerraron unos meses", None),
        ("y reorganizaron todo el negocio.", None),
        ("Redujeron el menú a *nueve productos*", None),
        ("y montaron una *cocina en línea:*", None),
        ("cada empleado hacía *un solo paso.*", None),
        ("Lo llamaron *Speedee Service System.*", None),
        ("Una hamburguesa costaba *quince centavos.*", None),
    ]),
    (45, 70, 0.5, [
        ("En *1954* apareció *Ray Kroc,*", None),
        ("un vendedor de *máquinas para batidos.*", None),
        ("Le intrigó que un solo restaurante", None),
        ("comprara tantas máquinas.", None),
        ("Se asoció con los hermanos", None),
        ("para *vender franquicias*", None),
        ("y en *1955* abrió su local en Des Plaines, Illinois.", None),
        ("En pocos años, la cadena llegó", None),
        ("a *cientos de restaurantes.*", None),
    ]),
    (70, 100, 0.5, [
        ("Primero cubrió *Estados Unidos:*", None),
        ("mil locales en *1968.*", None),
        ("En *1967* cruzó a *Canadá* y *Puerto Rico.*", None),
        ("En *1971* llegó a *Japón,* Europa y Australia.", None),
        ("En *1990,* a *Moscú* y a *China.*", None),
        ("En cada país adaptó el menú:", None),
        ("hamburguesa *teriyaki* en Japón,", None),
        ("el *Maharaja Mac,* sin carne de res, en India,", None),
        ("y la *McArabia* en Medio Oriente.", None),
        ("Hoy supera los *40 000* locales.", "Hoy supera los cuarenta mil locales."),
    ]),
    (100, 110, 0.3, [
        ("En *1961,* Kroc compró los derechos", None),
        ("por *2,7 millones* de dólares.", "por dos coma siete millones de dólares."),
        ("La familia habla de un trato incumplido;", None),
        ("la empresa, de una compra legal.", None),
    ]),
    (110, 120, 1.0, [
        ("Una idea de *cocina simple*", None),
        ("cambió la forma de *comer en el mundo.*", None),
        ("¿Y tú? ¿*Qué idea simple* cambiarías?", None),
    ]),
]


def tts(text, speed, path):
    if os.path.exists(path):
        return json.load(open(path))
    body = json.dumps({
        "text": text, "model_id": MODEL,
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.25, "use_speaker_boost": True, "speed": speed},
    }).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128",
        data=body, headers={"Content-Type": "application/json", "xi-api-key": "proxy-injected"})
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.load(r)
    json.dump(data, open(path, "w"))
    return data


def to_wav(data, path):
    mp3 = path.replace(".wav", ".mp3")
    open(mp3, "wb").write(base64.b64decode(data["audio_base64"]))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp3, "-ar", "48000", "-ac", "1", path], check=True)
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).decode())


cues, clips = [], []
for si, (s0, s1, lead, lines) in enumerate(SCENES):
    spoken = [(v or c.replace("*", "")) for c, v in lines]
    text = " ".join(spoken)
    budget = s1 - s0 - lead - 0.35
    speed = 1.0
    while True:
        key = f"{VOICE}_s{si}_{speed:.2f}"
        data = tts(text, speed, os.path.join(CACHE, key + ".json"))
        wav = os.path.join(CACHE, key + ".wav")
        dur = to_wav(data, wav)
        if dur <= budget or speed >= 1.2:
            break
        speed = min(1.2, round(speed * dur / budget + 0.02, 2))
    tempo = 1.0
    if dur > budget:  # último recurso: acelerar un poco sin cambiar el tono
        tempo = dur / budget
        fixed = wav.replace(".wav", "_fit.wav")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav, "-filter:a", f"atempo={tempo:.4f}", fixed], check=True)
        wav, dur = fixed, budget
    al = data["alignment"]
    starts, ends = al["character_start_times_seconds"], al["character_end_times_seconds"]
    off = 0
    for (cap, _), sp in zip(lines, spoken):
        a, b = off, off + len(sp) - 1
        cues.append({"start": round(s0 + lead + starts[a] / tempo, 3), "end": round(s0 + lead + ends[b] / tempo, 3), "text": cap, "scene": si})
        off += len(sp) + 1
    clips.append((wav, s0 + lead))
    print(f"escena {si + 1}: {dur:.2f}s (cabe en {budget:.2f}s) velocidad {speed} tempo {tempo:.3f}")

args = ["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-t", "120", "-i", "anullsrc=r=48000:cl=mono"]
for p, _ in clips:
    args += ["-i", p]
fl = "".join(f"[{i + 1}]adelay={int(t * 1000)}:all=1[a{i}];" for i, (_, t) in enumerate(clips))
fl += "[0]" + "".join(f"[a{i}]" for i in range(len(clips))) + f"amix=inputs={len(clips) + 1}:normalize=0,atrim=0:120,loudnorm=I=-16:TP=-1.5[out]"
args += ["-filter_complex", fl, "-map", "[out]", "-ar", "48000", "-ac", "2", os.path.join(PROJ, "assets/narracion.wav")]
subprocess.run(args, check=True)
with open(os.path.join(PROJ, "assets/narracion.js"), "w") as f:
    f.write("window.NARR = " + json.dumps(cues, ensure_ascii=False) + ";\n")
print("frases:", len(cues), "caracteres enviados:", sum(len(" ".join((v or c.replace("*", "")) for c, v in l)) for *_, l in SCENES))
