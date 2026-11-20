#!/usr/bin/env python3
"""Import Minecraft: Bedrock Edition changelogs into ``news/``.

Sources (no HTML scraping of the wiki UI is needed):

* ``launchercontent.mojang.com/v2/bedrockPatchNotes.json`` – official launcher
  feed with version, date, image and a ``contentPath`` pointing at the body.
* ``es.minecraft.wiki/api.php`` – Spanish intro used for the short summary.
  The wiki text is CC BY-NC-SA 3.0; only a short intro is used and the source
  is credited in every generated document.

Usage:
    python scripts/scrape_minecraft.py [--limit 10] [--dry-run]
"""
from __future__ import annotations

import argparse
import html as html_lib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from common import NEWS_DIR, slugify, today, validate_id, write_document

PATCH_NOTES_URL = "https://launchercontent.mojang.com/v2/bedrockPatchNotes.json"
HOST = "https://launchercontent.mojang.com"
CONTENT_BASE = HOST + "/v2/"
WIKI_API = "https://es.minecraft.wiki/api.php"
WIKI_BASE = "https://es.minecraft.wiki/wiki/"
USER_AGENT = (
    "CianovaNewsBot/1.0 (https://github.com/CianovaTeam/cianova-news; "
    "contacto@cianovalauncher.org)"
)

MAX_SUMMARY = 320
RETRIES = 2
TIMEOUT = 25


# ── HTTP ────────────────────────────────────────────────────────────────────

def http_get(url: str, timeout: int = TIMEOUT, retries: int = RETRIES) -> bytes:
    last_error = None
    for attempt in range(1, retries + 1):
        request = urllib.request.Request(
            url,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json, */*"},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1.5 * attempt)
    raise RuntimeError(f"No se pudo descargar {url}: {last_error}")


def fetch_json(url: str) -> dict:
    return json.loads(http_get(url).decode("utf-8"))


# ── Wiki ────────────────────────────────────────────────────────────────────

def _strip_templates(text: str) -> str:
    """Remove ``{{...}}`` blocks, including nested ones, until stable."""
    pattern = re.compile(r"\{\{[^{}]*\}\}", re.S)
    for _ in range(12):
        new = pattern.sub("", text)
        if new == text:
            break
        text = new
    return text


def clean_wikitext(text: str) -> str:
    """Turn a wikitext fragment into readable plain text."""
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.S | re.I)
    text = re.sub(r"<ref[^>]*/>", "", text, flags=re.I)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = _strip_templates(text)
    text = re.sub(r"\{\|.*?\|\}", "", text, flags=re.S)  # tables
    text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", text)  # [[a|b]] -> b
    text = re.sub(r"\[(?:https?://\S+)\s+([^\]]+)\]", r"\1", text)  # [url label]
    text = re.sub(r"\[(?:https?://\S+)\]", "", text)
    text = re.sub(r"'{2,}", "", text)  # bold/italic
    text = re.sub(r"<[^>]+>", "", text)
    text = html_lib.unescape(text)
    return re.sub(r"[ \t]+", " ", text)


def wiki_intro(version: str) -> str:
    """Return the Spanish intro paragraph for a Bedrock version, if any.

    Prefers the rendered lead section (natural prose) and falls back to a
    wikitext cleanup if the API returns no HTML.
    """
    html_text = _wiki_section_html(version)
    if html_text:
        intro = _extract_html_intro(html_text, version)
        if intro:
            return intro
    return _wiki_intro_wikitext(version)


def _wiki_api(params: dict) -> dict:
    query = urllib.parse.urlencode(params)
    return fetch_json(f"{WIKI_API}?{query}")


def _wiki_section_html(version: str) -> str:
    try:
        payload = _wiki_api(
            {
                "action": "parse",
                "page": f"Bedrock_Edition_{version}",
                "prop": "text",
                "section": "0",
                "format": "json",
                "formatversion": "2",
                "redirects": "1",
            }
        )
    except Exception as exc:
        print(f"  aviso: wiki no disponible para {version}: {exc}", file=sys.stderr)
        return ""
    return (payload.get("parse") or {}).get("text") or ""


def _extract_html_intro(html_text: str, version: str) -> str:
    try:
        from bs4 import BeautifulSoup
    except ImportError:  # pragma: no cover - CI installs requirements
        return ""
    soup = BeautifulSoup(html_text, "html.parser")
    for paragraph in soup.find_all("p"):
        text = re.sub(r"\s+", " ", paragraph.get_text()).strip()
        text = re.sub(r"\[\s*\d+\s*\]", "", text).strip()
        if len(text) < 90 or len(text.split()) < 12:
            continue
        if re.match(r"^(Windows|Android|iOS|iPadOS|ChromeOS|PlayStation|Nintendo)", text):
            continue
        return _trim_sentences(text, MAX_SUMMARY)
    return ""


def _wiki_intro_wikitext(version: str) -> str:
    try:
        payload = _wiki_api(
            {
                "action": "parse",
                "page": f"Bedrock_Edition_{version}",
                "prop": "wikitext",
                "format": "json",
                "formatversion": "2",
                "redirects": "1",
            }
        )
    except Exception as exc:  # network/API errors are non fatal
        print(f"  aviso: wiki no disponible para {version}: {exc}", file=sys.stderr)
        return ""

    wikitext = (payload.get("parse") or {}).get("wikitext") or ""
    if not wikitext:
        return ""

    cleaned = clean_wikitext(wikitext)
    for block in re.split(r"\n\s*\n", cleaned):
        block = " ".join(block.split())
        if not block or block.startswith(("==", "|", "{", "}", "[[Archivo:", "[[File:")):
            continue
        if len(block) < 80:
            continue
        return _trim_sentences(block, MAX_SUMMARY)
    return ""


def _trim_sentences(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit]
    for separator in (". ", "! ", "? "):
        index = cut.rfind(separator)
        if index > limit // 2:
            return cut[: index + 1].strip()
    return cut.rsplit(" ", 1)[0].rstrip(",;:") + "…"


# ── Mojang feed ─────────────────────────────────────────────────────────────

def html_to_markdown(body: str) -> str:
    """Convert the Mojang changelog HTML into Markdown."""
    if not body:
        return ""
    try:
        from bs4 import BeautifulSoup
        from markdownify import markdownify
    except ImportError as exc:  # pragma: no cover - CI installs requirements
        raise SystemExit(
            "Faltan dependencias: pip install -r requirements.txt"
        ) from exc

    soup = BeautifulSoup(body, "html.parser")
    for tag in soup(["script", "style", "iframe", "noscript"]):
        tag.decompose()
    for image in soup.find_all("img"):
        src = image.get("src") or ""
        if src.startswith("/"):
            image["src"] = HOST + src

    text = markdownify(str(soup), heading_style="ATX", bullets="-")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _absolute_image(entry: dict) -> str:
    image = entry.get("image") or {}
    url = image.get("url") if isinstance(image, dict) else None
    if not url:
        return ""
    if url.startswith("/"):
        return HOST + url
    return url


def _version_key(version: str):
    parts = re.findall(r"\d+", version or "")
    return tuple(int(part) for part in parts) or (0,)


def existing_versions(news_dir: str = NEWS_DIR) -> set:
    versions = set()
    if not os.path.isdir(news_dir):
        return versions
    for name in os.listdir(news_dir):
        if name.startswith("bedrock-") and name.endswith(".md"):
            versions.add(name[len("bedrock-") : -len(".md")])
    return versions


def build_document(entry: dict) -> tuple[dict, str] | None:
    version = str(entry.get("version") or "").strip()
    if not version:
        return None
    safe_version = re.sub(r"[^a-z0-9.]+", "-", version.lower()).strip("-")
    news_id = validate_id(f"bedrock-{safe_version}")

    body_html = ""
    content_path = entry.get("contentPath")
    if content_path:
        try:
            content = fetch_json(CONTENT_BASE + content_path.lstrip("/"))
            body_html = content.get("body") or ""
        except Exception as exc:
            print(f"  aviso: sin cuerpo para {version}: {exc}", file=sys.stderr)

    summary_es = wiki_intro(version)
    markdown_body = html_to_markdown(body_html)

    summary_en = ""
    if markdown_body:
        plain = re.sub(r"[#>*_`\-]+", " ", markdown_body)
        plain = " ".join(plain.split())
        summary_en = _trim_sentences(plain, MAX_SUMMARY)

    summary = summary_es or summary_en
    if not summary:
        summary = f"Nueva actualización de Minecraft: Bedrock Edition {version}."

    title_es = f"Minecraft Bedrock {version}"
    title_en = entry.get("title") or f"Minecraft: Bedrock Edition {version}"

    published = str(entry.get("date") or today())[:10]
    wiki_url = f"{WIKI_BASE}Bedrock_Edition_{urllib.parse.quote(version)}"

    footer = (
        "---\n\n"
        f"*Resumen elaborado a partir de [Minecraft Wiki]({wiki_url}) "
        "(CC BY-NC-SA 3.0) y de las notas oficiales de Mojang. "
        "Minecraft es una marca de Mojang Studios.*"
    )
    body = f"# {title_es}\n\n{summary}\n\n"
    if markdown_body:
        body += f"## Notas de la versión\n\n{markdown_body}\n\n"
    body += footer + "\n"

    meta = {
        "id": news_id,
        "type": "minecraft",
        "title_es": title_es,
        "title_en": title_en,
        "summary_es": summary,
        "summary_en": summary_en or summary,
        "image": _absolute_image(entry),
        "url": wiki_url,
        "published": published,
        "version": version,
        "source": "wiki" if summary_es else "mojang",
    }
    return meta, body


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=10, help="máximo de noticias nuevas")
    parser.add_argument("--dry-run", action="store_true", help="no escribir archivos")
    args = parser.parse_args(argv)

    feed = fetch_json(PATCH_NOTES_URL)
    entries = [
        entry
        for entry in feed.get("entries", [])
        if entry.get("patchNoteType") == "retail" and entry.get("version")
    ]
    entries.sort(key=lambda entry: _version_key(str(entry.get("version"))), reverse=True)

    known = existing_versions()
    pending = [entry for entry in entries if str(entry["version"]) not in known][: args.limit]

    if not pending:
        print("No hay versiones nuevas de Minecraft.")
        return 0

    written = 0
    for entry in pending:
        version = str(entry["version"])
        print(f"Importando Bedrock {version}…")
        try:
            result = build_document(entry)
        except Exception as exc:
            print(f"  error: {exc}", file=sys.stderr)
            continue
        if not result:
            continue
        meta, body = result
        if args.dry_run:
            print(f"  (dry-run) {meta['id']} · {meta['published']}")
            continue
        write_document(os.path.join(NEWS_DIR, f"{meta['id']}.md"), meta, body)
        written += 1

    print(f"{written} noticia(s) escrita(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
