---
name: guion-video
description: Escribe guiones de videos cortos verticales con el método de Jesdom - gancho, tabla voz-pantalla, guion para leer en cámara y notas de grabación, en el tono del alumno. Usar cuando pida un guion, ideas de gancho, adaptar una referencia, "escríbeme un video de" o una versión para anuncio.
---

# Guion de video

Guarda cada guion en `guiones/guion_<tema>.md`. Antes de escribir, lee `mi-estilo.md` (tono y palabra CTA).

## Antes de escribir

1. Pregunta solo lo que falte: tema, objetivo (alcance, comentarios o venta) y duración (por defecto 30–45 s).
2. Si hay una referencia analizada, usa su `ficha.md` de `medir-referencia`.
3. No inventes datos, precios ni funciones. Si algo no se puede confirmar, no va en el guion.

## Formatos del método

- **Tutorial:** primero el resultado, luego pasos que se puedan copiar y un recurso para guardar.
- **Fast Food:** persona en cámara y una lista o demo rápida, un elemento por corte.
- **Serie "Día N":** mismo gancho y encuadre cada día, solo cambia el número y el elemento sorpresa. Cada episodio se entiende solo.
- **Reveal:** "Este video lo editó mi IA", y lo demuestras.

## Reglas

- Frases cortas, fáciles de decir y con el tono del alumno. Que no suene a anuncio traducido.
- **Gancho (0–3 s):** una sola idea que abra una pregunta o muestre el resultado. Escribe 5 opciones y recomienda una.
- Unas 2,5 palabras por segundo. Cada bloque tiene algo nuevo que ver.
- Cierra con el CTA de `mi-estilo.md`.

## Formato

```markdown
# Guion: "<título>"
Formato, objetivo y duración.

| Bloque | Voz | Pantalla |
|---|---|---|

## Ganchos alternativos
## Guion corrido (para leer en cámara)
## Notas de grabación
## Nombres para la transcripción
```

En las notas de grabación: repetir cada frase hasta que salga bien (la última toma suele ser la mejor), mirar a cámara y dejar un segundo de silencio entre tomas. En "Nombres para la transcripción" lista marcas y nombres propios para el `--prompt` de `montar-tomas`.
