---
name: qa-video
description: Control de calidad antes de subir un video vertical. Revisa formato, volumen, picos, cuadros negros o congelados, inicio limpio, zona segura y tramos sin cara. Usar al terminar cualquier export y cuando el alumno diga "revisa mi video", "QA", "está listo para subir" o "valida el export".
---

# QA de video

Corre esto sobre **cada video antes de subirlo**:

```bash
python "<carpeta de esta skill>/scripts/qa.py" VIDEO.mp4 --out ediciones/<proyecto>/qa
```

`<carpeta de esta skill>` es el directorio base de esta skill. Genera `qa.json` y `hoja.png`. El comando termina con error si falla un control automático.

## Controles automáticos

| Control | Objetivo |
|---|---|
| Formato | 1080x1920, 30 fps, H.264, AAC |
| Volumen | -14 LUFS (±1,5) |
| Pico | -1,0 dBTP como máximo |
| Cuadros negros | Ninguno de 0,1 s o más |
| Primer cuadro | Con imagen desde el cuadro 0 |

Las congelaciones y los tramos sin cara salen como avisos: pueden ser gráficos a propósito.

## Revisión visual

Abre `hoja.png`. El rectángulo verde es la zona segura. Revisa:

1. Ningún texto importante sale del rectángulo.
2. Los textos no tapan la cara.
3. Los textos se leen bien sobre el fondo.
4. El CTA es grande, está arriba y no lo tapa la interfaz.
5. No hay planos de perfil.

Explícale al alumno qué falló, en qué segundo y cómo corregirlo, en palabras simples. Si un control no se pudo ejecutar, dilo. Si todo pasa: "Aprobado. Este video lo editó tu IA."
