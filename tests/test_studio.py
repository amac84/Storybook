#!/usr/bin/env python3
"""Smoke tests for studio scripts. Does not author Book 1."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from studio.manuscript import count_words, validate_manuscript  # noqa: E402
from studio.paths import LEDGER, ROOT as STUDIO_ROOT  # noqa: E402
from studio.io import read_json  # noqa: E402


SAMPLE = """# Test

## Spread 01
### Text
The lantern clicked.
### Visual Story Information
A frog copies the click with a pebble.
### Narrative Purpose
Hook.
### Page-Turn Question
What is in the dark?

## Spread 02
### Text
They step closer.
### Visual Story Information
Mars has already seen the door.
### Narrative Purpose
Discovery.
### Page-Turn Question
resolved
"""


class ManuscriptTests(unittest.TestCase):
    def test_valid_spreads(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manuscript-v1.md"
            path.write_text(SAMPLE, encoding="utf-8")
            self.assertEqual(validate_manuscript(path), [])
            self.assertGreater(count_words(path), 5)

    def test_missing_heading(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manuscript-v1.md"
            path.write_text("## Spread 01\n### Text\nhi\n", encoding="utf-8")
            errors = validate_manuscript(path)
            self.assertTrue(any("Visual Story Information" in e for e in errors))


class RepoShapeTests(unittest.TestCase):
    def test_no_book_one_yet(self):
        self.assertFalse((STUDIO_ROOT / "books" / "001").exists())
        ledger = read_json(LEDGER)
        self.assertEqual(ledger.get("books_approved"), 0)

    def test_required_trees(self):
        for path in (
            "AGENTS.md",
            "bible/values-and-principles.md",
            "characters/cove/character.md",
            "characters/mars/character.md",
            ".cursor/agents/story-architect.md",
            "tools/image-generation/protocol.py",
        ):
            self.assertTrue((STUDIO_ROOT / path).exists(), path)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
