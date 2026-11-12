---
name: medir-referencia
description: Mide con ffmpeg el ritmo y la estructura de un video de referencia (cortes, duración de planos, gancho, volumen) y lo convierte en una ficha para copiar el estilo con propósito. Usar cuando el alumno pase un TikTok o Reel, diga "analiza este video", "edítalo como este" o "qué tiene este video".
---

# Medir referencia

Convierte "me gusta este estilo" en números. Si llega un link, descárgalo:

```bash
python -m yt_dlp -o "referencias/<nombre>/ref.mp4" "<URL>"
```

Luego mide:

```bash
python "<carpeta de esta skill>/scripts/medir.py" referencias/<nombre>/ref.mp4 --out referencias/<nombre>
```

`<carpeta de esta skill>` es el directorio base de esta skill. Genera `medidas.json`, `hoja_cortes.png` (un cuadro por plano) y `hoja_gancho.png` (0 a 3 s).

## Ficha

Mira las hojas y escribe `referencias/<nombre>/ficha.md` en lenguaje simple:

- **Datos:** creador, link, duración.
- **Ritmo:** cortes por segundo, duración media de plano, cortes en los primeros 3 s.
- **Gancho:** qué se ve y se dice en 0–3 s, y por qué engancha.
- **Estructura:** bloques con tiempos (gancho, promesa, desarrollo, CTA).
- **Sistema visual:** subtítulos, textos, posiciones y colores.
- **Sonido:** música, efectos y volumen.
- **Qué tomar y qué cambiar:** la referencia es la base, nunca una copia. Aplica `mi-estilo.md`.

El detector puede confundir fundidos con cortes. Si en un video con la cara fija da 0 cortes, repite con `--umbral 0.12`. Comprueba siempre los números contra `hoja_cortes.png`. No copies texto, logos ni material del creador original.
