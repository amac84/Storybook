#!/usr/bin/env python3
"""Compile a targeted context packet for one book."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from studio.context import build_context  # noqa: E402
from studio.paths import book_dir, parse_book_ref  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Build books/NNN/context-packet.yaml")
    parser.add_argument("book", help="Book number or path")
    args = parser.parse_args()
    number = parse_book_ref(args.book)
    if not book_dir(number).exists():
        raise SystemExit(f"No book directory for {number:03d}. Run scripts/new-book.py first.")
    packet = build_context(number)
    dest = book_dir(number) / "context-packet.yaml"
    print(f"Wrote {dest}")
    print(f"Characters: {', '.join(c['id'] for c in packet.get('characters') or [])}")
    print(f"Recent books in packet: {len(packet.get('recent_books') or [])}")
    print(f"Gaps: {len(packet.get('gaps_and_local_inventions') or [])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
