from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from .config import studio_meta
from .io import read_json, read_text, read_yaml, write_yaml
from .paths import BIBLE, CANON, CHARACTERS, LEDGER, book_dir


CHARACTER_FILES = (
    "character.md",
    "personality.md",
    "voice.md",
    "developmental-arc.md",
    "visual-rules.md",
)


def build_context(number: int) -> dict[str, Any]:
    book = book_dir(number)
    brief = read_yaml(book / "brief.yaml") or {}
    meta = studio_meta()
    window = int(meta.get("recent_book_window", 6))

    ids = _character_ids(brief)
    packet = {
        "book_number": number,
        "compiled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "compiler": "scripts/build-context.py",
        "brief_digest": _brief_digest(brief),
        "characters": [_character_slice(cid, fuller=(cid in ids["focus"])) for cid in ids["include"]],
        "relationships": _relevant_relationships(ids["include"]),
        "values": _values_slice(brief),
        "world_rules_relevant": _extract_filled_sections(BIBLE / "world-rules.md"),
        "locations_relevant": _keyword_items(
            read_json(CANON / "locations.json").get("locations") or [],
            _brief_text(brief),
        ),
        "recurring_elements_relevant": _keyword_items(
            read_json(CANON / "recurring-elements.json").get("elements") or [],
            _brief_text(brief),
        ),
        "open_threads_relevant": _keyword_items(
            read_json(CANON / "open-story-threads.json").get("threads") or [],
            _brief_text(brief),
            include_all_if_few=True,
        ),
        "recent_books": _recent_books(window),
        "older_canon_relevant": _older_canon(window, _brief_text(brief)),
        "writing_principles": [
            "Use spread-based picture-book form",
            "One owner of prose — the Showrunner",
            "Obey bible/family-code.md and bible/story-design-principles.md",
            "Story first. One precise situation/feeling/belief/strategy. One portable phrase.",
            "See → try → own. Setback. Transfer once. Do not explain the ending.",
            "Lesson demonstrated through choices, problem, escalation, climax, resolution",
            "Confidence is earned: Choose → Attempt → Struggle → Adjust → Recover",
            "Child agency at the resolution; adults do not solve the central problem",
            "Repair is action, not a last-page apology",
            "Do not invent permanent canon to fill [CREATOR INPUT REQUIRED]",
        ],
        "family_code": "bible/family-code.md",
        "creator_preferences_relevant": _taste_notes(),
        "fear_and_content_constraints": _extract_filled_sections(
            BIBLE / "fear-and-content-boundaries.md"
        ),
        "gaps_and_local_inventions": _gaps(ids["include"]),
        "do_not_contradict": [
            "Approved facts in canon/ and filled character fields",
            "The McAulay Family Code",
            "Temporary story state from earlier approved books does not persist unless promoted",
        ],
    }
    write_yaml(book / "context-packet.yaml", packet)
    return packet


def _character_ids(brief: dict[str, Any]) -> dict[str, list[str]]:
    known = [p.name for p in CHARACTERS.iterdir() if p.is_dir() and not p.name.startswith("_") and p.name != "supporting"]
    focus: list[str] = []
    raw_focus = brief.get("character_focus")
    if isinstance(raw_focus, str) and raw_focus.strip():
        focus.append(raw_focus.strip().lower())
    required = brief.get("characters_required") or []
    include = []
    for name in [*focus, *required, "cove", "mars"]:
        key = str(name).strip().lower()
        if key in known and key not in include:
            include.append(key)
    return {"include": include, "focus": focus or include[:1]}


def _brief_digest(brief: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "working_title",
        "goal",
        "adventure",
        "character_focus",
        "supporting_character_role",
        "tone",
        "special_elements",
        "primary_value",
        "secondary_value",
        "setting",
        "avoid",
        "specific_requests",
    )
    return {k: brief.get(k) for k in keys if brief.get(k) not in (None, [], "")}


def _brief_text(brief: dict[str, Any]) -> str:
    return " ".join(str(v) for v in brief.values() if v not in (None, [], "")).lower()


def _character_slice(character_id: str, fuller: bool) -> dict[str, Any]:
    folder = CHARACTERS / character_id
    files = CHARACTER_FILES if fuller else ("character.md", "personality.md", "developmental-arc.md")
    return {
        "id": character_id,
        "role_in_this_book": "focus" if fuller else "supporting-or-ensemble",
        "files": {name: _trim_placeholder_doc(read_text(folder / name)) for name in files},
    }


def _trim_placeholder_doc(text: str, limit: int = 1800) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n… [truncated for packet; read the source file if needed]"


def _relevant_relationships(character_ids: list[str]) -> list[dict[str, Any]]:
    pairs = read_json(CANON / "relationships.json").get("pairs") or []
    wanted = set(character_ids)
    return [p for p in pairs if p.get("a") in wanted or p.get("b") in wanted]


def _values_slice(brief: dict[str, Any]) -> dict[str, Any]:
    names = [brief.get("primary_value"), brief.get("secondary_value"), brief.get("goal")]
    names = [str(n).strip() for n in names if n]
    bible = read_text(BIBLE / "values-and-principles.md")
    definitions = []
    for name in names:
        block = _value_block(bible, name)
        if block:
            definitions.append({"requested": name, "definition_block": block})
        else:
            definitions.append(
                {
                    "requested": name,
                    "definition_block": "[CREATOR INPUT REQUIRED] — no matching defined value yet",
                }
            )
    return {
        "primary": brief.get("primary_value") or brief.get("goal"),
        "secondary": [brief.get("secondary_value")] if brief.get("secondary_value") else [],
        "definitions": definitions,
        "governing_document": "bible/family-code.md",
        "strength_definition": "A strong boy makes other people feel safer, stronger and more included around him.",
    }


def _value_block(bible: str, name: str) -> str | None:
    needle = name.strip().lower().replace(" ", "_")
    chunks = re.split(r"\n###\s+", bible)
    for chunk in chunks[1:]:
        title, _, body = chunk.partition("\n")
        blob = (title + "\n" + body[:200]).lower()
        if needle in blob.replace(" ", "_") or name.strip().lower() in blob:
            return ("### " + title + "\n" + body).strip()[:2000]
    # Also match yaml value: fields (confidence, strength)
    for match in re.finditer(r"```yaml\n(value:\s*(\w+)[\s\S]*?)```", bible):
        if needle in match.group(2).lower() or name.strip().lower() in match.group(1)[:80].lower():
            return match.group(1).strip()[:2000]
    return None


def _extract_filled_sections(path) -> list[str]:
    text = read_text(path)
    sections = re.split(r"\n##\s+", text)
    filled = []
    for section in sections[1:]:
        if "[CREATOR INPUT REQUIRED]" in section and not re.search(
            r"[A-Za-z].*\n(?!\[CREATOR)", section
        ):
            title = section.split("\n", 1)[0]
            filled.append(f"{title}: still placeholder — stay conservative / escalate if locking")
        else:
            filled.append(section.strip()[:1200])
    return filled


def _keyword_items(items: list[Any], brief_text: str, include_all_if_few: bool = False) -> list[Any]:
    if include_all_if_few and len(items) <= 8:
        return items
    if not brief_text:
        return items[:5]
    matched = []
    for item in items:
        blob = " ".join(str(v) for v in (item.values() if isinstance(item, dict) else [item])).lower()
        if any(token in blob for token in brief_text.split() if len(token) > 3):
            matched.append(item)
    return matched or items[:3]


def _recent_books(window: int) -> list[dict[str, Any]]:
    ledger = read_json(LEDGER)
    approved = list(ledger.get("approved_books") or [])
    return approved[-window:]


def _older_canon(window: int, brief_text: str) -> list[dict[str, Any]]:
    ledger = read_json(LEDGER)
    approved = list(ledger.get("approved_books") or [])
    older = approved[:-window] if len(approved) > window else []
    compressed = []
    for book in older:
        entry = {
            "book_number": book.get("book_number"),
            "title": book.get("title"),
            "summary_compressed": book.get("summary_compressed") or book.get("adventure"),
            "new_canon": book.get("new_canon") or [],
        }
        compressed.append(entry)
    return _keyword_items(compressed, brief_text, include_all_if_few=True)


def _taste_notes() -> list[str]:
    text = read_text(BIBLE / "creator-taste.md")
    notes = []
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
        elif line.startswith("- ") and "(none recorded yet)" not in line:
            notes.append(f"{current}: {line[2:].strip()}")
    return notes


def _gaps(character_ids: list[str]) -> list[str]:
    gaps = []
    for cid in character_ids:
        text = read_text(CHARACTERS / cid / "character.md")
        if "[CREATOR INPUT REQUIRED]" in text:
            gaps.append(f"{cid} identity/personality/visual fields are still placeholders")
    if "[CREATOR INPUT REQUIRED]" in read_text(BIBLE / "world-rules.md"):
        gaps.append("Major world rules are placeholders — do not invent persistent metaphysics")
    if "[CREATOR INPUT REQUIRED]" in read_text(BIBLE / "values-and-principles.md"):
        gaps.append("Value definitions are placeholders — treat a briefed value as provisional")
    return gaps
