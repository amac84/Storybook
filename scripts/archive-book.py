#!/usr/bin/env python3
"""Promote an approved book into canon. Refuses to run without approval."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from studio.canon import archive_approved  # noqa: E402
from studio.paths import parse_book_ref  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive an approved book into canon/.")
    parser.add_argument("book", help="Book number or path")
    parser.add_argument(
        "--approved",
        action="store_true",
        help="Required confirmation flag. Canon does not update from drafts.",
    )
    args = parser.parse_args()
    if not args.approved:
        raise SystemExit("Refusing to archive. Pass --approved after human approval.")

    number = parse_book_ref(args.book)
    try:
        summary = archive_approved(number)
    except PermissionError as exc:
        print(exc, file=sys.stderr)
        return 2
    print(f"Canon updated from book {number:03d}: {summary.get('title') or '(untitled)'}")
    print(json.dumps({"new_canon": summary.get("new_canon"), "approved_at": summary.get("approved_at")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
