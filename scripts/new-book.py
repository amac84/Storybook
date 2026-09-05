#!/usr/bin/env python3
"""Scaffold the next book directory. Does not write a story."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from studio.books import create_book  # noqa: E402
from studio.io import read_yaml  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Create the next numbered book folder.")
    parser.add_argument("--brief", type=Path, help="Optional YAML brief to merge")
    parser.add_argument("--number", type=int, help="Force a book number (default: next)")
    parser.add_argument("--goal", help="Short creative goal")
    parser.add_argument("--adventure", help="Adventure seed")
    parser.add_argument("--character-focus", dest="character_focus")
    parser.add_argument("--tone")
    parser.add_argument("--working-title", dest="working_title")
    args = parser.parse_args()

    brief = read_yaml(args.brief) if args.brief else {}
    if not isinstance(brief, dict):
        brief = {}
    for field in ("goal", "adventure", "character_focus", "tone", "working_title"):
        value = getattr(args, field)
        if value:
            brief[field] = value

    dest = create_book(brief=brief or None, number=args.number)
    print(f"Created {dest.relative_to(dest.parents[1])}")
    print("Next: fill brief.yaml, then run python3 scripts/build-context.py", dest.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
