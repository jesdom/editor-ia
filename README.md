# Editor IA · Kit del alumno

Tu propio editor de video con IA, dentro de Claude. Lo que viste en la clase, ahora en tu computadora.

**IA con propósito, no IA por usar.** — Jesdom

## Qué hace

| Skill | Le dices a Claude | Qué hace |
|---|---|---|
| `empezar` | "empezar" | Instala Python, ffmpeg y las librerías, crea tus carpetas y guarda tu estilo |
| `mi-estilo` | "aplica mi estilo" | Tus colores, fuente, tono y CTA en cada video |
| `medir-referencia` | "analiza este video" + link | Mide ritmo, cortes y gancho de un viral y te dice qué tomar |
| `guion-video` | "escríbeme un guion sobre ___" | 5 ganchos, tabla voz-pantalla y texto para leer en cámara |
| `montar-tomas` | "monta mis tomas" | Elige la mejor toma de cada frase y arma el montado |
| `qa-video` | "revisa mi video" | Volumen, formato, cuadros negros y zona segura antes de subir |

## Necesitas

- Claude Pro (o un plan superior)
- La app de Claude en tu computadora (pestaña **Code**) o Claude Code en la terminal
- Windows o Mac con unos 5 GB libres

## Instalar

**Opción fácil.** Abre una carpeta nueva en Claude Code y pega esto:

```
Instala mi kit Editor IA de Jesdom:
1. Descarga el repositorio https://github.com/jesdom/editor-ia
2. Copia todas las carpetas de plugins/editor-ia/skills a mi carpeta de skills personales (~/.claude/skills).
3. Después usa la skill "empezar" para dejar todo listo.
```

**Terminal.** En Claude Code:

```
/plugin marketplace add jesdom/editor-ia
/plugin install editor-ia@jesdom
```

Luego escribe `empezar`.

## Actualizar

Dile a Claude: `actualiza mi kit Editor IA`. Las novedades salen en tu hub del alumno.

---

Kit exclusivo para alumnos de la clase en vivo de Jesdom · TikTok [@jesdomm](https://www.tiktok.com/@jesdomm)
