#!/usr/bin/env python3
"""Regenerate ``news.json`` from the Markdown documents in ``news/``.

Usage:
    python scripts/build_index.py            # write news.json
    python scripts/build_index.py --check    # exit 1 if news.json is stale
"""
from __future__ import annotations

import argparse
import json
import sys

from common import INDEX_PATH, build_index, dump_index, load_index


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="no escribir, solo validar")
    args = parser.parse_args(argv)

    index = build_index()

    if args.check:
        try:
            current = load_index(INDEX_PATH)
        except FileNotFoundError:
            print("news.json no existe; ejecuta scripts/build_index.py", file=sys.stderr)
            return 1
        if current.get("items") != index.get("items"):
            print(
                "news.json está desactualizado; ejecuta scripts/build_index.py",
                file=sys.stderr,
            )
            return 1
        print(f"news.json al día ({index['count']} noticias)")
        return 0

    dump_index(index)
    print(f"news.json generado con {index['count']} noticias")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
