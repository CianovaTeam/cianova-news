"""Shared helpers for the Cianova News repository.

The repository is a static data source: a ``news.json`` index generated from a
set of Markdown documents in ``news/``.  Everything here is dependency-free so
that it can run in CI and locally without extra wheels.
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
from datetime import date, datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEWS_DIR = os.path.join(ROOT, "news")
INDEX_PATH = os.path.join(ROOT, "news.json")

SCHEMA_VERSION = 1
MAX_INDEX_ITEMS = 50

NEWS_TYPES = ("minecraft", "cianova")
SOURCES = ("mojang", "wiki", "cianova", "manual")
LANGS = ("es", "en")

ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,79}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DOC_PREFIX = "news/"

REQUIRED_KEYS = ("id", "type", "published")


class NewsError(ValueError):
    """Raised when a news document is malformed."""


def today() -> str:
    """Return the current UTC date as ``YYYY-MM-DD``."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def slugify(text: str, fallback: str = "noticia") -> str:
    """Turn arbitrary text into a safe, lowercase ASCII slug."""
    text = unicodedata.normalize("NFKD", text or "")
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:60] or fallback


def validate_id(news_id: str) -> str:
    if not news_id or not ID_RE.match(news_id):
        raise NewsError(
            f"id inválido: {news_id!r} (usa minúsculas, números, '.', '_' o '-')"
        )
    return news_id


def validate_date(value: str) -> str:
    if not DATE_RE.match(value or ""):
        raise NewsError(f"fecha inválida: {value!r} (formato YYYY-MM-DD)")
    try:
        date.fromisoformat(value)
    except ValueError as exc:  # pragma: no cover - defensive
        raise NewsError(f"fecha inválida: {value!r}") from exc
    return value


def _encode(value) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    return json.dumps(value, ensure_ascii=False)


def _decode(value: str):
    value = value.strip()
    if not value:
        return ""
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return value


def render_document(meta: dict, body: str) -> str:
    """Serialise front matter plus Markdown body into a document string."""
    lines = ["---"]
    for key, value in meta.items():
        if value is None or value == "":
            continue
        lines.append(f"{key}: {_encode(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n\n" + body.strip() + "\n"


def parse_document(text: str) -> tuple[dict, str]:
    """Split a Markdown document into ``(front_matter, body)``.

    Front matter values are JSON scalars, which keeps the format unambiguous
    without pulling in a YAML dependency.
    """
    if not text.startswith("---\n"):
        raise NewsError("el documento no empieza con front matter ('---')")
    end = text.find("\n---", 4)
    if end == -1:
        raise NewsError("front matter sin cierre ('---')")
    raw_meta = text[4:end]
    body = text[end + 4 :].lstrip("\n")

    meta: dict = {}
    for line in raw_meta.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise NewsError(f"línea de front matter inválida: {line!r}")
        key, value = line.split(":", 1)
        meta[key.strip()] = _decode(value)
    return meta, body


def load_document(path: str) -> tuple[dict, str]:
    with open(path, "r", encoding="utf-8") as handle:
        return parse_document(handle.read())


def write_document(path: str, meta: dict, body: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(render_document(meta, body))


def document_id_from_path(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


def iter_documents(news_dir: str = NEWS_DIR):
    """Yield ``(path, meta, body)`` for every Markdown document, sorted."""
    if not os.path.isdir(news_dir):
        return
    for name in sorted(os.listdir(news_dir)):
        if not name.endswith(".md") or name.startswith("."):
            continue
        path = os.path.join(news_dir, name)
        meta, body = load_document(path)
        yield path, meta, body


def build_item(meta: dict, body: str, path: str) -> dict:
    """Validate a document and turn it into an index entry."""
    missing = [key for key in REQUIRED_KEYS if not str(meta.get(key, "")).strip()]
    if missing:
        raise NewsError(f"{os.path.basename(path)}: faltan campos {missing}")

    if not (meta.get("title_es") or meta.get("title_en")):
        raise NewsError(f"{os.path.basename(path)}: falta title_es/title_en")
    if not (meta.get("summary_es") or meta.get("summary_en")):
        raise NewsError(f"{os.path.basename(path)}: falta summary_es/summary_en")

    news_id = validate_id(str(meta["id"]))
    if document_id_from_path(path) != news_id:
        raise NewsError(
            f"{os.path.basename(path)}: el nombre del archivo debe ser {news_id}.md"
        )

    news_type = str(meta["type"])
    if news_type not in NEWS_TYPES:
        raise NewsError(f"{news_id}: type debe ser uno de {NEWS_TYPES}")

    published = validate_date(str(meta["published"]))

    title = {"es": str(meta.get("title_es") or meta.get("title_en") or "")}
    summary = {"es": str(meta.get("summary_es") or meta.get("summary_en") or "")}
    if meta.get("title_en"):
        title["en"] = str(meta["title_en"])
    if meta.get("summary_en"):
        summary["en"] = str(meta["summary_en"])

    if not title["es"] or not summary["es"]:
        raise NewsError(f"{news_id}: título o resumen vacío")

    item = {
        "id": news_id,
        "type": news_type,
        "title": title,
        "summary": summary,
        "doc": DOC_PREFIX + os.path.basename(path),
        "published": published,
        "source": str(meta.get("source") or ("cianova" if news_type == "cianova" else "mojang")),
    }
    if meta.get("image"):
        item["image"] = str(meta["image"])
    if meta.get("url"):
        item["url"] = str(meta["url"])
    if meta.get("version"):
        item["version"] = str(meta["version"])
    if body.strip():
        # Cheap signal for the launcher: there is a long-form document.
        item["has_doc"] = True
    return item


def build_index(news_dir: str = NEWS_DIR, limit: int = MAX_INDEX_ITEMS) -> dict:
    items = []
    seen = set()
    for path, meta, body in iter_documents(news_dir):
        item = build_item(meta, body, path)
        if item["id"] in seen:
            raise NewsError(f"id duplicado: {item['id']}")
        seen.add(item["id"])
        items.append(item)

    items.sort(key=lambda entry: (entry["published"], entry["id"]), reverse=True)
    return {
        "schema": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(items[:limit]),
        "items": items[:limit],
    }


def dump_index(index: dict, path: str = INDEX_PATH) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(index, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def load_index(path: str = INDEX_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)
