"""Corta un bruto según segmentos.json -> montado.mov, voz.wav, montaje.json y palabras.json (en tiempo final).
iPhone graba VFR: se pasa a 30 fps y se corta por cuadros."""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np

FPS = 30


def medir(raw, t):
    data = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", str(raw), "-frames:v", "1", "-vf", "scale=270:480",
                           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    f = np.frombuffer(data, np.uint8).reshape(480, 270, 3).astype(float)
    return f[150:230, 105:165].mean((0, 1)), f[20:120, 20:90].mean((0, 1))  # cara, pared


def ganancias(raw, segs):
    """Ganancia RGB por toma respecto del primer segmento (cara 60 %, pared 40 %), limitada a ±7 %."""
    pts = [[medir(raw, s["s"] + (s["e"] - s["s"]) * k) for k in (0.3, 0.5, 0.7)] for s in segs]
    cara0, pared0 = (np.mean([p[i] for p in pts[0]], 0) for i in (0, 1))
    res = []
    for p, s in zip(pts, segs):
        if s.get("tipo") == "pantalla":
            res.append((1.0, 1.0, 1.0))
            continue
        cara, pared = (np.mean([x[i] for x in p], 0) for i in (0, 1))
        res.append(tuple(round(float(v), 4) for v in np.clip(0.6 * cara0 / cara + 0.4 * pared0 / pared, 0.93, 1.07)))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("segmentos", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--palabras", type=Path, help="JSON de tomas.py para remapear palabras")
    ap.add_argument("--sin-color", action="store_true")
    ap.add_argument("--sin-grade", action="store_true")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)

    cfg = json.load(open(a.segmentos, encoding="utf8"))
    raw, segs = Path(cfg["raw"]), cfg["segmentos"]
    if not raw.is_absolute() and not raw.exists():
        raw = a.segmentos.parent / raw
    for i, s in enumerate(segs):
        if s["e"] - s["s"] < 0.1:
            raise SystemExit(f"Segmento {i} demasiado corto: {s}")

    G = [(1.0, 1.0, 1.0)] * len(segs) if a.sin_color else ganancias(raw, segs)
    n = len(segs)
    fc = [f"[0:v]setpts=PTS-STARTPTS,fps={FPS},split={n}" + "".join(f"[v{i}]" for i in range(n)),
          f"[0:a]aresample=48000,aformat=channel_layouts=mono,asplit={n}" + "".join(f"[s{i}]" for i in range(n))]
    inicios, cortes, off = [], [], 0.0
    for i, s in enumerate(segs):
        ca, cb = round(s["s"] * FPS), round(s["e"] * FPS)
        fa, fb = ca / FPS, cb / FPS
        inicios.append(round(off, 4))
        cortes.append((fa, fb, off))
        off += fb - fa
        r, g, b = G[i]
        fc.append(f"[v{i}]trim=start_frame={ca}:end_frame={cb},setpts=PTS-STARTPTS,colorchannelmixer=rr={r}:gg={g}:bb={b}[w{i}]")
        fc.append(f"[s{i}]atrim={fa:.4f}:{fb:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={fb - fa - 0.025:.4f}:d=0.025[a{i}]")
    fc.append("".join(f"[w{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[cv][ca]")
    fc.append("[cv]fps=30[ov]" if a.sin_grade else "[cv]fps=30,eq=brightness=0.03:contrast=1.03:saturation=1.06:gamma=1.04[ov]")

    mov, voz = a.out / "montado.mov", a.out / "voz.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-filter_complex", ";".join(fc), "-map", "[ov]", "-c:v", "libx264",
                    "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", "-map", "[ca]", "-c:a", "pcm_s16le", str(mov)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mov), "-vn", "-c:a", "pcm_s16le", str(voz)], check=True)
    json.dump({"dur": round(off, 4), "seg": inicios, "tipo": [s.get("tipo", "camara") for s in segs],
               "nombre": [s.get("nombre", "") for s in segs]}, open(a.out / "montaje.json", "w", encoding="utf8"), ensure_ascii=False)

    if a.palabras:
        todas = [w for s in json.load(open(a.palabras, encoding="utf8")) for w in s["words"]]
        salida = []
        for fa, fb, ini in cortes:
            for w in todas:
                centro = (w["s"] + w["e"]) / 2
                if fa <= centro < fb or min(w["e"], fb) - max(w["s"], fa) >= 0.05:  # incluye palabras en el borde del corte
                    salida.append({"w": w["w"], "s": round(max(w["s"], fa) - fa + ini, 3), "e": round(min(w["e"], fb) - fa + ini, 3)})
        json.dump(salida, open(a.out / "palabras.json", "w", encoding="utf8"), ensure_ascii=False, indent=0)
        print(f"{len(salida)} palabras remapeadas")
    print(f"montado {off:.2f} s, {n} segmentos -> {mov}")


if __name__ == "__main__":
    main()
