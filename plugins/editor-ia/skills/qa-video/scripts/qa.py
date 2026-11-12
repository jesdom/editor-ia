"""QA de un video vertical -> qa.json y hoja.png (con zona segura). Sale con código 1 si falla un criterio."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

W, H = 1080, 1920
SEGURA = (120, 190, 960, 1500)


def filtros(video, af=None, vf=None):
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", str(video)]
    cmd += ["-af", af, "-vn"] if af else ["-vf", vf, "-an"]
    return subprocess.run(cmd + ["-f", "null", "-"], capture_output=True, encoding="utf8", errors="replace").stderr


def cuadro(video, t, ancho=270):
    alto = ancho * 16 // 9
    data = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", str(video), "-frames:v", "1", "-vf", f"scale={ancho}:{alto}",
                           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(data, np.uint8).reshape(alto, ancho, 3) if len(data) == ancho * alto * 3 else None


def tramos_sin_cara(video, dur):
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    data = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", "fps=4,scale=270:480,format=gray", "-f", "rawvideo", "-"],
                          capture_output=True).stdout
    fr = np.frombuffer(data, np.uint8).reshape(-1, 480, 270)
    hay = [len(casc.detectMultiScale(f, 1.1, 6, minSize=(45, 45))) > 0 for f in fr]
    res, ini = [], None
    for i, v in enumerate(hay + [True]):
        if not v and ini is None:
            ini = i
        elif v and ini is not None:
            if (i - ini) / 4 >= 1.0:
                res.append([round(ini / 4, 2), round(min(i / 4, dur), 2)])
            ini = None
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--n", type=int, default=12)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)

    p = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(a.video)],
                                  capture_output=True, encoding="utf8", check=True).stdout)
    v = next(s for s in p["streams"] if s["codec_type"] == "video")
    au = next((s for s in p["streams"] if s["codec_type"] == "audio"), None)
    dur = float(p["format"]["duration"])
    num, den = v["avg_frame_rate"].split("/")
    fps = float(num) / float(den)

    fallos, avisos = [], []
    if (v["width"], v["height"]) != (W, H):
        fallos.append(f"Resolución {v['width']}x{v['height']}")
    if abs(fps - 30) > 0.05:
        fallos.append(f"FPS {fps:.2f}")
    if v["codec_name"] != "h264" or v.get("pix_fmt") != "yuv420p":
        fallos.append(f"Video {v['codec_name']}/{v.get('pix_fmt')}")

    lufs = pico = None
    if au is None:
        fallos.append("Sin pista de audio")
    else:
        if au["codec_name"] != "aac":
            fallos.append(f"Audio {au['codec_name']}")
        txt = filtros(a.video, af="ebur128=peak=true")
        resumen = txt[txt.rfind("Summary:"):]
        m1, m2 = re.search(r"I:\s+(-?[\d.]+) LUFS", resumen), re.search(r"Peak:\s+(-?[\d.]+) dBFS", resumen)
        if m1 and m2:
            lufs, pico = float(m1.group(1)), float(m2.group(1))
            if abs(lufs + 14) > 1.5:
                fallos.append(f"Volumen {lufs} LUFS")
            if pico > -1.0:
                fallos.append(f"Pico {pico} dBTP")
        else:
            fallos.append("No se pudo medir el volumen")

    txt = filtros(a.video, vf="blackdetect=d=0.1:pix_th=0.08")
    negros = [[float(x), float(y)] for x, y in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", txt)]
    if negros:
        fallos.append(f"Cuadros negros: {negros}")
    txt = filtros(a.video, vf="freezedetect=n=0.001:d=1.2")
    congelados = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", txt)]
    if congelados:
        avisos.append(f"Imagen fija desde: {congelados}")

    f0 = cuadro(a.video, 0)
    if f0 is None or f0.mean() < 8:
        fallos.append("El primer cuadro está vacío o negro")
    sin_cara = tramos_sin_cara(a.video, dur)
    if sin_cara:
        avisos.append(f"Sin cara frontal (compara con el guion): {sin_cara}")

    ts = [dur * (i + 0.5) / a.n for i in range(a.n)]
    columnas, escala = 6, 270 / W
    filas = (a.n + columnas - 1) // columnas
    hoja = Image.new("RGB", (columnas * 278, filas * 488), (30, 30, 30))
    d = ImageDraw.Draw(hoja)
    for i, t in enumerate(ts):
        f = cuadro(a.video, t)
        if f is None:
            continue
        x, y = (i % columnas) * 278 + 4, (i // columnas) * 488 + 4
        hoja.paste(Image.fromarray(f), (x, y))
        d.rectangle([x + SEGURA[0] * escala, y + SEGURA[1] * escala, x + SEGURA[2] * escala, y + SEGURA[3] * escala], outline=(0, 255, 90), width=2)
        d.text((x + 6, y + 6), f"{t:.1f}s", fill=(255, 255, 0))
    hoja.save(a.out / "hoja.png")

    rep = {"video": str(a.video), "dur": round(dur, 2), "res": f"{v['width']}x{v['height']}", "fps": round(fps, 2), "lufs": lufs, "pico_dbtp": pico,
           "aprobado": not fallos, "fallos": fallos, "avisos": avisos}
    json.dump(rep, open(a.out / "qa.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    sys.stdout.reconfigure(encoding="utf8")
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
