"""Mide cortes, ritmo y volumen de una referencia -> medidas.json, hoja_cortes.png, hoja_gancho.png."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def cuadro(video, t, ancho=180):
    alto = ancho * 16 // 9
    vf = f"scale={ancho}:{alto}:force_original_aspect_ratio=decrease,pad={ancho}:{alto}:(ow-iw)/2:(oh-ih)/2"
    data = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", str(video), "-frames:v", "1", "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                          capture_output=True).stdout
    return Image.fromarray(np.frombuffer(data, np.uint8).reshape(alto, ancho, 3)) if len(data) == ancho * alto * 3 else None


def hoja(video, tiempos, ruta, columnas=8):
    w, h = 180, 320
    filas = max(1, (len(tiempos) + columnas - 1) // columnas)
    img = Image.new("RGB", (columnas * (w + 4), filas * (h + 4)), (25, 25, 25))
    d = ImageDraw.Draw(img)
    for i, t in enumerate(tiempos):
        f = cuadro(video, t)
        if f is not None:
            x, y = (i % columnas) * (w + 4) + 2, (i // columnas) * (h + 4) + 2
            img.paste(f, (x, y))
            d.text((x + 5, y + 5), f"{t:.2f}s", fill=(255, 255, 0))
    img.save(ruta)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--umbral", type=float, default=0.3)
    ap.add_argument("--palabras", type=int, help="Palabras habladas, para calcular palabras por segundo")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)

    p = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(a.video)],
                                  capture_output=True, encoding="utf8", check=True).stdout)
    v = next(s for s in p["streams"] if s["codec_type"] == "video")
    dur = float(p["format"]["duration"])
    txt = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(a.video), "-vf", f"scale=270:-2,select='gt(scene,{a.umbral})',showinfo", "-an", "-f", "null", "-"],
                         capture_output=True, encoding="utf8", errors="replace").stderr
    cortes = [float(x) for x in re.findall(r"pts_time:([\d.]+)", txt)]
    limpios = [t for i, t in enumerate(cortes) if i == 0 or t - cortes[i - 1] >= 0.1]
    bordes = [0.0] + limpios + [dur]
    planos = np.diff(bordes)

    txt = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(a.video), "-af", "ebur128=peak=true", "-vn", "-f", "null", "-"],
                         capture_output=True, encoding="utf8", errors="replace").stderr
    resumen = txt[txt.rfind("Summary:"):]
    lufs = re.search(r"I:\s+(-?[\d.]+) LUFS", resumen)

    med = {"archivo": a.video.name, "dur": round(dur, 2), "res": f"{v['width']}x{v['height']}", "cortes": len(limpios),
           "cortes_por_seg": round(len(limpios) / dur, 2), "plano_mediano": round(float(np.median(planos)), 2), "plano_max": round(float(planos.max()), 2),
           "cortes_0_3s": sum(t < 3 for t in limpios), "tiempos_corte": [round(t, 2) for t in limpios], "lufs": float(lufs.group(1)) if lufs else None,
           "palabras_por_seg": round(a.palabras / dur, 2) if a.palabras else None}
    json.dump(med, open(a.out / "medidas.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    centros = [(x + y) / 2 for x, y in zip(bordes, bordes[1:])][:48]
    hoja(a.video, centros, a.out / "hoja_cortes.png")
    hoja(a.video, [0.05, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], a.out / "hoja_gancho.png")
    sys.stdout.reconfigure(encoding="utf8")
    print(json.dumps({k: x for k, x in med.items() if k != "tiempos_corte"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
