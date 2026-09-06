from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CANON = ROOT / "canon"
BOOKS = ROOT / "books"
BIBLE = ROOT / "bible"
CHARACTERS = ROOT / "characters"
TEMPLATES = ROOT / "templates"
STUDIO_CONFIG = ROOT / "studio.yaml"
LEDGER = CANON / "series-ledger.json"

# Persistent studio planning memory — NOT canon. See curriculum/README.md.
CURRICULUM = ROOT / "curriculum"
CURRICULUM_CATALOG = CURRICULUM / "catalog.yaml"
CURRICULUM_COVERAGE = CURRICULUM / "coverage-ledger.json"
CURRICULUM_INTENTIONS = CURRICULUM / "intentions.yaml"


def book_id(number: int | str) -> str:
    return f"{int(number):03d}"


def book_dir(number: int | str) -> Path:
    return BOOKS / book_id(number)


def parse_book_ref(value: str) -> int:
    text = value.rstrip("/").split("/")[-1]
    if text.isdigit():
        return int(text)
    raise ValueError(f"Cannot parse book number from {value!r}")
