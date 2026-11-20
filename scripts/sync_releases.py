#!/usr/bin/env python3
"""Turn launcher GitHub releases into Cianova news documents.

Runs on a schedule (and on demand). For every published, non-prerelease
release of the launcher that does not have a news document yet, it creates
``news/cianova-<tag>.md`` using the release notes as the long-form body.

Usage:
    python scripts/sync_releases.py [--limit 5] [--repo OWNER/NAME]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

from common import NEWS_DIR, slugify, today, validate_id, write_document

DEFAULT_REPO = "CianovaTeam/CianovaLauncher-mcpelauncher"
USER_AGENT = "CianovaNewsBot/1.0 (+https://github.com/CianovaTeam/cianova-news)"


def fetch_releases(repo: str, limit: int = 10) -> list[dict]:
    url = f"https://api.github.com/repos/{repo}/releases?per_page={limit}"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))


def first_paragraph(markdown: str) -> str:
    for block in re.split(r"\n\s*\n", markdown or ""):
        block = " ".join(block.split())
        if not block or block.startswith(("#", ">", "-", "*", "|")):
            continue
        if len(block) < 20:
            continue
        if len(block) > 320:
            block = block[:317].rsplit(" ", 1)[0] + "…"
        return block
    return ""


def strip_leading_heading(markdown: str, title: str) -> str:
    lines = (markdown or "").strip().splitlines()
    if lines and lines[0].lstrip().startswith("#"):
        lines = lines[1:]
    text = "\n".join(lines).strip()
    if text.startswith(title):
        text = text[len(title) :].lstrip("\n: ")
    return text.strip()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args(argv)

    try:
        releases = fetch_releases(args.repo)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"No se pudieron leer las releases: {exc}", file=sys.stderr)
        return 1

    created = 0
    for release in releases:
        if release.get("draft") or release.get("prerelease"):
            continue
        tag = str(release.get("tag_name") or "").strip()
        if not tag:
            continue
        news_id = validate_id(f"cianova-{slugify(tag)}")
        path = os.path.join(NEWS_DIR, f"{news_id}.md")
        if os.path.exists(path):
            continue
        if created >= args.limit:
            break

        title = (release.get("name") or tag).strip()
        body_md = strip_leading_heading(release.get("body") or "", title)
        summary = first_paragraph(body_md) or f"Nueva versión de CianovaLauncher: {title}."
        published = str(release.get("published_at") or today())[:10]

        meta = {
            "id": news_id,
            "type": "cianova",
            "title_es": title,
            "title_en": title,
            "summary_es": summary,
            "summary_en": summary,
            "url": release.get("html_url") or "",
            "published": published,
            "version": tag,
            "source": "cianova",
        }
        document = f"# {title}\n\n{summary}\n"
        if body_md:
            document += "\n" + body_md + "\n"

        write_document(path, meta, document)
        print(f"Importada release {tag} -> {news_id}")
        created += 1

    print(f"{created} release(s) importada(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
