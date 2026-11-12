"""Analiza un bruto: transcripción por palabra, islas de voz, mirada a cámara y tomas repetidas.
Salida en --out: <nombre>.json, islas.json, tomas.md."""
import argparse
import difflib
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np

SR, HOP = 16000, 320  # 20 ms
FPS_MIRA, W, H = 5, 270, 480


def transcribir(raw, destino, modelo, idioma, prompt):
    from faster_whisper import WhisperModel

    wav = destino.with_name(destino.stem + "_16k.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-map", "0:a:0", "-ac", "1", "-ar", str(SR), str(wav)], check=True)
    segs, _ = WhisperModel(modelo, device="cpu", compute_type="int8").transcribe(
        str(wav), language=idioma, word_timestamps=True, vad_filter=False, beam_size=5, initial_prompt=prompt or None)
    out = []
    for s in segs:
        out.append({"s": s.start, "e": s.end, "t": s.text.strip(),
                    "words": [{"w": w.word.strip(), "s": w.start, "e": w.end} for w in (s.words or [])]})
        print(f"{s.start:7.2f}-{s.end:7.2f} {s.text.strip()}", flush=True)
    json.dump(out, open(destino, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    wav.unlink(missing_ok=True)
    return out


def islas_de_voz(raw, hueco=0.35, minimo=0.4):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(raw), "-map", "0:a:0", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, np.float32)
    db = np.array([20 * np.log10(np.sqrt((x[i:i + HOP] ** 2).mean()) + 1e-9) for i in range(0, len(x) - HOP, HOP)])
    on = db > max(np.percentile(db, 15) + 14, -42)
    dt = HOP / SR
    res, ini, gap = [], None, 0
    for i, v in enumerate(on):
        if v:
            ini = i if ini is None else ini
            gap = 0
        elif ini is not None:
            gap += 1
            if gap * dt > hueco:
                if (i - gap - ini) * dt > minimo:
                    res.append((ini * dt, (i - gap) * dt))
                ini, gap = None, 0
    if ini is not None and (len(on) - ini) * dt > minimo:
        res.append((ini * dt, len(on) * dt))
    return res


def cuadros(raw):
    data = subprocess.run(["ffmpeg", "-v", "error", "-i", str(raw), "-vf", f"fps={FPS_MIRA},scale={W}:{H},format=gray",
                           "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(data, np.uint8).reshape(-1, H, W)


def grupo_repetido(items, umbral=0.62):
    """Asigna el mismo grupo a islas con texto parecido (repeticiones de una frase)."""
    grupos, n = [], 0
    for i, it in enumerate(items):
        g = None
        for j in range(i - 1, max(i - 12, -1), -1):
            a, b = it["t"].lower(), items[j]["t"].lower()
            if a and b and difflib.SequenceMatcher(None, a, b).ratio() >= umbral:
                g = grupos[j]
                break
        if g is None:
            n += 1
            g = n
        grupos.append(g)
    return grupos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--modelo", default="medium")
    ap.add_argument("--idioma", default="es")
    ap.add_argument("--prompt", default="")
    ap.add_argument("--sin-transcribir", action="store_true")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)

    tr = a.out / f"{a.raw.stem}.json"
    if tr.exists():
        segs = json.load(open(tr, encoding="utf8"))
    elif a.sin_transcribir:
        segs = []
    else:
        segs = transcribir(a.raw, tr, a.modelo, a.idioma, a.prompt)
    palabras = [w for s in segs for w in s["words"]]

    fr = cuadros(a.raw)
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def frontal(t):
        caras = casc.detectMultiScale(fr[min(int(t * FPS_MIRA), len(fr) - 1)], 1.1, 6, minSize=(50, 50))
        return any(abs(x + w / 2 - W / 2) < 45 for x, y, w, h in caras)

    items = []
    for s, e in islas_de_voz(a.raw):
        ts = np.arange(s, e, 0.2)
        items.append({"s": round(s, 2), "e": round(e, 2), "mira": round(float(np.mean([frontal(t) for t in ts])), 2) if len(ts) else 0.0,
                      "t": " ".join(w["w"] for w in palabras if w["s"] < e - 0.05 and w["e"] > s + 0.05)})
    for it, g in zip(items, grupo_repetido(items)):
        it["grupo"] = g
    ultimo = {it["grupo"]: i for i, it in enumerate(items)}
    for i, it in enumerate(items):
        it["sugerida"] = bool(ultimo[it["grupo"]] == i and it["mira"] >= 0.5 and it["t"])
    json.dump(items, open(a.out / "islas.json", "w", encoding="utf8"), ensure_ascii=False, indent=0)

    filas = ["| Grupo | Inicio | Fin | Dur | Mira | Sug. | Texto |", "|---|---|---|---|---|---|---|"]
    filas += [f"| {i['grupo']} | {i['s']:.2f} | {i['e']:.2f} | {i['e'] - i['s']:.1f} | {i['mira']:.0%} | {'SI' if i['sugerida'] else ''} | {i['t']} |" for i in items]
    (a.out / "tomas.md").write_text("\n".join(filas) + "\n", encoding="utf8")
    print(f"{len(items)} islas, {items[-1]['grupo'] if items else 0} grupos, {sum(i['sugerida'] for i in items)} sugeridas -> {a.out / 'tomas.md'}")


if __name__ == "__main__":
    main()
