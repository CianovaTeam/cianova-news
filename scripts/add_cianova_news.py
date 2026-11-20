#!/usr/bin/env python3
"""Create a Cianova news document from the command line or a workflow.

Usage:
    python scripts/add_cianova_news.py \
        --title-es "Nuevo sistema de perfiles" \
        --summary-es "Los perfiles ahora guardan ajustes por separado." \
        --body-file /tmp/body.md \
        --image https://cianovalauncher.org/img/perfiles.webp \
        --url https://cianovalauncher.org/blog/perfiles

The ``--body``/``--body-file`` content is Markdown and becomes the long-form
document shown in the launcher's news feed.
"""
from __future__ import annotations

import argparse
import os
import sys

from common import NEWS_DIR, slugify, today, validate_id, write_document


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title-es", required=True)
    parser.add_argument("--title-en", default="")
    parser.add_argument("--summary-es", required=True)
    parser.add_argument("--summary-en", default="")
    parser.add_argument("--body", default="")
    parser.add_argument("--body-file", default="")
    parser.add_argument("--image", default="")
    parser.add_argument("--url", default="")
    parser.add_argument("--published", default=today())
    parser.add_argument("--id", default="")
    parser.add_argument("--version", default="")
    args = parser.parse_args(argv)

    body = args.body
    if args.body_file:
        with open(args.body_file, "r", encoding="utf-8") as handle:
            body = handle.read()

    news_id = args.id.strip() or f"cianova-{slugify(args.title_es)}"
    news_id = validate_id(news_id)

    meta = {
        "id": news_id,
        "type": "cianova",
        "title_es": args.title_es.strip(),
        "title_en": args.title_en.strip(),
        "summary_es": args.summary_es.strip(),
        "summary_en": args.summary_en.strip(),
        "image": args.image.strip(),
        "url": args.url.strip(),
        "published": args.published.strip(),
        "version": args.version.strip(),
        "source": "cianova",
    }

    document_body = f"# {args.title_es.strip()}\n\n{args.summary_es.strip()}\n"
    if body.strip():
        document_body += "\n" + body.strip() + "\n"

    path = os.path.join(NEWS_DIR, f"{news_id}.md")
    if os.path.exists(path):
        print(f"Ya existe {path}; no se sobrescribe.", file=sys.stderr)
        return 1

    write_document(path, meta, document_body)
    print(f"Noticia creada: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
