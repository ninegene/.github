#!/usr/bin/env python3
"""Encode a wiki URL candidate or a verified decoded slug; no network or writes."""

import argparse
from urllib.parse import quote

WIKI_BASE = "https://github.com/ninegene/.github/wiki/"


def page_url(value: str, *, slug: bool = False) -> str:
    if not value or "/" in value or "\\" in value:
        raise ValueError("Supply one nonempty root-level filename or decoded slug")
    if not slug:
        for extension in (".markdown", ".md"):
            if value.lower().endswith(extension):
                value = value[: -len(extension)]
                break
        else:
            raise ValueError("Filename must end in .md or .markdown; use --slug otherwise")
        value = value.replace(" ", "-")
    if not value or value in (".", ".."):
        raise ValueError("Page slug cannot be empty or a dot path segment")
    return WIKI_BASE + quote(value, safe="-._~")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("value", help="Markdown filename, or decoded slug with --slug")
    parser.add_argument("--slug", action="store_true", help="Encode a verified decoded slug")
    args = parser.parse_args()
    try:
        print(page_url(args.value, slug=args.slug))
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
