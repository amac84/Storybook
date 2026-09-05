#!/usr/bin/env python3
"""Validate a book against quality gates and file conventions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from studio.manuscript import count_words  # noqa: E402
from studio.paths import book_dir, parse_book_ref  # noqa: E402
from studio.quality_gates import STAGES, evaluate  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a book at a production stage.")
    parser.add_argument("book", help="Book number or path, e.g. 1 or books/001")
    parser.add_argument(
        "--stage",
        default="manuscript",
        choices=STAGES,
        help="scaffold | manuscript | illustration | approval",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable result")
    args = parser.parse_args()

    number = parse_book_ref(args.book)
    result = evaluate(number, args.stage)
    manuscript = book_dir(number) / "manuscript-final.md"
    if not manuscript.exists():
        manuscript = book_dir(number) / "manuscript-v2.md"
    if not manuscript.exists():
        manuscript = book_dir(number) / "manuscript-v1.md"
    result["word_count"] = count_words(manuscript)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"Book {number:03d}  stage={args.stage}  {status}")
        if result.get("scores"):
            scores = result["scores"]
            print(
                "Scores:",
                ", ".join(
                    f"{k}={v}" for k, v in scores.items() if v is not None
                )
                or "(none)",
            )
        if result.get("word_count"):
            print(f"Word count (Text sections): {result['word_count']}")
        for warning in result["warnings"]:
            print(f"  warning: {warning}")
        for failure in result["failures"]:
            print(f"  fail: {failure}")
        if result["passed"] and not result["failures"]:
            print("Quality gates cleared (or documented overrides applied).")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
