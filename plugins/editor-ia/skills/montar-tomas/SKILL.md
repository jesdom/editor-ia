---
name: montar-tomas
description: Convierte el video bruto del celular, con muchas tomas repetidas, en un montado limpio. Transcribe por palabra, separa las tomas, mide si mira a cámara, elige la mejor de cada frase y corta con color parejo. Usar cuando el alumno pase un video bruto, diga "monta mis tomas", "corta el bruto", "elige las tomas" o al empezar la edición de un video hablado.
---

# Montar tomas

Del bruto al `montado.mov`. Trabaja en `ediciones/<proyecto>/`. Los scripts están en `<carpeta de esta skill>/scripts/` (el directorio base de esta skill).

## Pasos

1. **Analiza el bruto.** En `--prompt` van los nombres propios del guion, para que la transcripción los escriba bien.

   ```bash
   python "<carpeta de esta skill>/scripts/tomas.py" brutos/VIDEO.MOV --out ediciones/<proyecto> --prompt "Claude, nombre de tu marca..."
   ```

   Genera `<nombre>.json` (palabras), `islas.json` y `tomas.md`. En una computadora normal tarda bastante (unos 30 min por 7 min de video con el modelo `medium`): lánzalo en segundo plano y avísale al alumno. Si tiene prisa, usa `--modelo small`.

2. **Elige las tomas** comparando `tomas.md` con el guion:
   - Por defecto, la **última toma limpia** de cada frase: suele ser la mejor.
   - Descarta tomas donde no mira a cámara. Si una frase solo existe leyendo, márcala `"tipo": "pantalla"`: irá tapada con un gráfico.
   - No dejes cuadros de perfil al inicio o final de una toma.
   - Revisa los inicios: a veces la transcripción corta la primera sílaba.

3. **Escribe `segmentos.json`** con los segundos del bruto:

   ```json
   {"raw": "brutos/VIDEO.MOV", "segmentos": [
     {"s": 12.40, "e": 15.10, "tipo": "camara", "nombre": "gancho"},
     {"s": 48.02, "e": 51.33, "tipo": "pantalla", "nombre": "paso1"}
   ]}
   ```

4. **Monta.**

   ```bash
   python "<carpeta de esta skill>/scripts/montar.py" ediciones/<proyecto>/segmentos.json --out ediciones/<proyecto> --palabras ediciones/<proyecto>/VIDEO.json
   ```

   Genera `montado.mov`, `voz.wav`, `montaje.json` y `palabras.json` con los tiempos ya ajustados. **No vuelvas a transcribir el montado**: inventa palabras.

5. **Muéstrale** la lista de tomas elegidas y confirma con el alumno antes de seguir.

## Notas técnicas

- Los iPhone graban con cuadros variables: el script pasa a 30 fps y corta por cuadros.
- El color se empareja entre tomas (máximo ±7 %). Para desactivarlo, `--sin-color`; para quitar el aclarado final, `--sin-grade`.
