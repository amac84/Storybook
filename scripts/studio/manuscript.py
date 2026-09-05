from __future__ import annotations

import re
from pathlib import Path

SPREAD_RE = re.compile(r"^##\s+Spread\s+(\d+)\s*$", re.MULTILINE)
REQUIRED_HEADINGS = (
    "Text",
    "Visual Story Information",
    "Narrative Purpose",
    "Page-Turn Question",
)


def validate_manuscript(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"Missing manuscript: {path}"]
    text = path.read_text(encoding="utf-8")
    ids = [int(m.group(1)) for m in SPREAD_RE.finditer(text)]
    if not ids:
        errors.append(f"{path.name}: no '## Spread NN' headings found")
        return errors
    if ids != list(range(1, len(ids) + 1)) and ids != list(range(ids[0], ids[0] + len(ids))):
        errors.append(f"{path.name}: spread numbers should be contiguous ({ids})")
    parts = SPREAD_RE.split(text)
    # split keeps capture groups: preamble, id, body, id, body...
    bodies = parts[2::2]
    for spread_id, body in zip(ids, bodies):
        for heading in REQUIRED_HEADINGS:
            if not re.search(rf"^###\s+{re.escape(heading)}\s*$", body, re.MULTILINE):
                errors.append(f"{path.name} Spread {spread_id:02d}: missing ### {heading}")
    return errors


def count_words(path: Path) -> int:
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")
    blocks = re.findall(
        r"^###\s+Text\s*$([\s\S]*?)(?=^###\s|\Z)",
        text,
        re.MULTILINE,
    )
    words = 0
    for block in blocks:
        words += len(re.findall(r"\b[\w']+\b", block))
    return words
