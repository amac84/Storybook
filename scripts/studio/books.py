from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import studio_meta
from .io import read_json, read_yaml, write_json, write_yaml
from .paths import BOOKS, LEDGER, TEMPLATES, book_dir, book_id


BOOK_SUBDIRS = (
    "art/references",
    "art/generated",
    "art/approved",
    "production/final",
)

TEMPLATE_COPIES = {
    "brief.yaml": "book-brief.yaml",
    "context-packet.yaml": "context-packet.yaml",
    "proposed-canon.yaml": "proposed-canon.yaml",
    "book-report.yaml": "final-book-report.yaml",
    "art/direction.yaml": "art-direction.yaml",
    "art/visual-state.yaml": "visual-state.yaml",
    "art/qa.yaml": "visual-qa.yaml",
}


def next_book_number() -> int:
    existing = []
    if BOOKS.exists():
        existing = [int(p.name) for p in BOOKS.iterdir() if p.is_dir() and p.name.isdigit()]
    ledger = read_json(LEDGER) if LEDGER.exists() else {}
    return max([0, *existing, int(ledger.get("next_book_number", 1)) - 1]) + 1


def create_book(brief: dict[str, Any] | None = None, number: int | None = None) -> Path:
    meta = studio_meta()
    n = number or next_book_number()
    dest = book_dir(n)
    if dest.exists():
        raise FileExistsError(f"Book directory already exists: {dest}")

    dest.mkdir(parents=True)
    for sub in BOOK_SUBDIRS:
        (dest / sub).mkdir(parents=True, exist_ok=True)
        (dest / sub / ".gitkeep").write_text("", encoding="utf-8")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for dest_name, template_name in TEMPLATE_COPIES.items():
        src = TEMPLATES / template_name
        target = dest / dest_name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, target)
        data = read_yaml(target) or {}
        if isinstance(data, dict):
            if "book_number" in data:
                data["book_number"] = n
            if dest_name == "brief.yaml":
                data = _merge_brief(data, brief or {})
                data["book_number"] = n
            if dest_name == "book-report.yaml":
                data["status"] = "draft"
                data["pages"] = meta.get("default_pages", 32)
                data["spread_count"] = meta.get("default_spreads", 16)
            if dest_name == "context-packet.yaml":
                data["book_number"] = n
                data["compiled_at"] = None
            write_yaml(target, data)

    (dest / "production" / "layout.json").write_text(
        '{\n  "book_number": %d,\n  "spreads": []\n}\n' % n,
        encoding="utf-8",
    )
    (dest / "STATUS.md").write_text(
        f"# Book {book_id(n)}\n\nStatus: draft\nCreated: {now}\n\n"
        "Manuscript files are created when the Showrunner writes them.\n"
        "Do not overwrite versioned drafts.\n",
        encoding="utf-8",
    )

    _register_in_progress(n)
    return dest


def _merge_brief(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in incoming.items():
        if value is not None:
            merged[key] = value
    return merged


def _register_in_progress(number: int) -> None:
    ledger = read_json(LEDGER)
    entry = {
        "book_number": number,
        "directory": f"books/{book_id(number)}",
        "status": "draft",
    }
    in_progress = list(ledger.get("books_in_progress") or [])
    if not any(item.get("book_number") == number for item in in_progress):
        in_progress.append(entry)
    ledger["books_in_progress"] = in_progress
    ledger["next_book_number"] = max(int(ledger.get("next_book_number", 1)), number + 1)
    write_json(LEDGER, ledger)


def load_brief(number: int) -> dict[str, Any]:
    path = book_dir(number) / "brief.yaml"
    return read_yaml(path) or {}
