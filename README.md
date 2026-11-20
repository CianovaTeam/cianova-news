# cianova-news

Fuente estática de noticias para CianovaLauncher.

El repositorio publica un único índice (`news.json`) y un documento Markdown
por noticia (`news/<id>.md`). El launcher descarga el índice desde GitHub Pages
o jsDelivr y solo pide el documento cuando el usuario abre una noticia.

- Índice: <https://cianovateam.github.io/cianova-news/news.json>
- Espejo: <https://cdn.jsdelivr.net/gh/CianovaTeam/cianova-news@main/news.json>

## Estructura

```
news.json                 índice generado (no editar a mano)
news/<id>.md              documento completo con front matter
scripts/common.py         esquema, validación y utilidades
scripts/build_index.py    regenera news.json desde news/*.md
scripts/scrape_minecraft.py  importa changelogs de Mojang + resumen de la wiki ES
scripts/add_cianova_news.py  crea una noticia de Cianova
scripts/sync_releases.py     convierte releases del launcher en noticias
.github/workflows/        automatización (scrape, add, sync, validate)
```

## Esquema del índice

```json
{
  "schema": 1,
  "generated_at": "2026-11-20T06:00:00Z",
  "count": 1,
  "items": [
    {
      "id": "bedrock-26.60",
      "type": "minecraft",
      "title": { "es": "Minecraft Bedrock 26.60", "en": "Minecraft: Bedrock Edition 26.60" },
      "summary": { "es": "…", "en": "…" },
      "image": "https://launchercontent.mojang.com/v2/images/26.60.jpg",
      "doc": "news/bedrock-26.60.md",
      "url": "https://es.minecraft.wiki/wiki/Bedrock_Edition_26.60",
      "published": "2026-10-27",
      "version": "26.60",
      "source": "wiki",
      "has_doc": true
    }
  ]
}
```

- `id` estable y único; el archivo debe llamarse `<id>.md`.
- `type`: `minecraft` o `cianova`.
- `title`/`summary`: objeto por idioma; el launcher usa el idioma activo y cae
  a `es` y luego a `en`.
- `image` y `url` son opcionales. Las imágenes de Minecraft se enlazan desde el
  CDN de Mojang; no se rehospedan.
- `doc` siempre empieza por `news/`.

## Front matter

```markdown
---
id: "bedrock-26.60"
type: "minecraft"
title_es: "Minecraft Bedrock 26.60"
title_en: "Minecraft: Bedrock Edition 26.60"
summary_es: "…"
summary_en: "…"
image: "https://launchercontent.mojang.com/v2/images/26.60.jpg"
url: "https://es.minecraft.wiki/wiki/Bedrock_Edition_26.60"
published: "2026-10-27"
version: "26.60"
source: "wiki"
---

# Minecraft Bedrock 26.60
…
```

Los valores son escalares JSON, así que las comillas y los saltos no rompen el
parseo. `build_index.py` valida el esquema y falla si algo no cuadra.

## Añadir una noticia de Cianova

Desde GitHub: **Actions → Add Cianova news → Run workflow** con título, resumen,
cuerpo Markdown, imagen y enlace.

En local:

```bash
python scripts/add_cianova_news.py \
  --title-es "Nuevo sistema de perfiles" \
  --summary-es "Los perfiles guardan ajustes por separado." \
  --body-file /tmp/body.md \
  --image https://cianovalauncher.org/img/perfiles.webp \
  --url https://cianovalauncher.org/blog/perfiles
python scripts/build_index.py
```

También puedes abrir un PR añadiendo el `.md` y ejecutando `build_index.py`.

## Noticias automáticas

| Workflow | Cuándo | Qué hace |
|---|---|---|
| `scrape.yml` | diario 06:00 UTC + manual | importa versiones retail nuevas de Bedrock (cuerpo oficial + intro de la wiki ES) |
| `sync-releases.yml` | diario + manual | convierte releases publicadas del launcher en noticias `cianova` |
| `add-news.yml` | manual | crea una noticia de Cianova desde el formulario |
| `validate.yml` | push / PR | tests + validación del esquema |

Los bots solo hacen commit si `news/` o `news.json` cambian.

## Atribución y licencias

- Los resúmenes de Minecraft se elaboran a partir de
  [Minecraft Wiki](https://es.minecraft.wiki/) (**CC BY-NC-SA 3.0**) usando solo
  el intro, con atribución y enlace en cada documento. No se copia la página
  completa.
- Las notas de versión provienen del feed público de Mojang
  (`launchercontent.mojang.com`). Las imágenes se enlazan desde su CDN.
- Minecraft es una marca de Mojang Studios. Este proyecto no está afiliado a
  Mojang ni a Microsoft.
- El código de este repositorio se publica bajo licencia MIT.
