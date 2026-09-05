from __future__ import annotations

from datetime import date
from typing import Any

from .io import read_json, read_yaml, write_json
from .paths import CANON, LEDGER, book_dir
from .config import studio_meta


def archive_approved(number: int) -> dict[str, Any]:
    book = book_dir(number)
    report = read_yaml(book / "book-report.yaml") or {}
    if report.get("human_approval") != "approved":
        raise PermissionError(
            f"Book {number:03d} is not approved. Refusing to update canon."
        )

    proposed = read_yaml(book / "proposed-canon.yaml") or {}
    brief = read_yaml(book / "brief.yaml") or {}
    items = [i for i in (proposed.get("items") or []) if i.get("recommend_promote") == "yes"]
    if report.get("potential_new_canon"):
        # Prefer the human-facing list when present; keep structured items too.
        pass

    summary = _book_summary(number, report, brief, items)
    _update_ledger(summary)
    _update_timeline(summary)
    _update_locations(items, number)
    _update_elements(items, number)
    _update_threads(items, number, summary)
    _update_character_state(summary)
    _update_decisions(items, number)
    return summary


def _book_summary(
    number: int,
    report: dict[str, Any],
    brief: dict[str, Any],
    items: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "book_number": number,
        "title": report.get("title") or brief.get("working_title"),
        "primary_character": brief.get("character_focus"),
        "primary_value": report.get("primary_value") or brief.get("primary_value") or brief.get("goal"),
        "secondary_values": brief.get("secondary_value") and [brief.get("secondary_value")] or [],
        "adventure": brief.get("adventure") or brief.get("adventure_seed"),
        "major_events": report.get("major_events") or [],
        "character_growth": report.get("character_development") or [],
        "new_canon": [i.get("fact") for i in items if i.get("fact")]
        or report.get("potential_new_canon")
        or [],
        "temporary_state": (read_yaml(book_dir(number) / "art" / "visual-state.yaml") or {}).get(
            "characters"
        )
        or {},
        "new_locations": [i.get("fact") for i in items if i.get("category") == "location"],
        "new_characters": [i.get("fact") for i in items if i.get("category") == "character"],
        "recurring_elements": [i.get("fact") for i in items if i.get("category") in {"object", "ritual", "phrase"}],
        "unresolved_threads": [i.get("fact") for i in items if i.get("category") == "thread"],
        "important_visual_details": report.get("important_visual_details") or [],
        "summary_rich": report.get("summary_rich") or report.get("character_development"),
        "summary_compressed": None,
        "approved_at": report.get("approved_at") or date.today().isoformat(),
        "directory": f"books/{number:03d}",
    }


def _update_ledger(summary: dict[str, Any]) -> None:
    ledger = read_json(LEDGER)
    window = int(studio_meta().get("recent_book_window", 6))
    approved = list(ledger.get("approved_books") or [])
    approved = [b for b in approved if b.get("book_number") != summary["book_number"]]
    approved.append(summary)
    if len(approved) > window:
        aging = approved[-(window + 1)]
        if not aging.get("summary_compressed"):
            aging["summary_compressed"] = _compress(aging)
            aging["summary_rich"] = None
    ledger["approved_books"] = approved
    ledger["books_approved"] = len(approved)
    ledger["status"] = "active"
    ledger["next_book_number"] = max(int(ledger.get("next_book_number", 1)), summary["book_number"] + 1)
    ledger["books_in_progress"] = [
        b for b in (ledger.get("books_in_progress") or []) if b.get("book_number") != summary["book_number"]
    ]
    write_json(LEDGER, ledger)


def _compress(book: dict[str, Any]) -> str:
    parts = [
        f"Book {book.get('book_number')}: {book.get('title') or 'Untitled'}.",
        f"Adventure: {book.get('adventure') or 'n/a'}.",
        f"Value: {book.get('primary_value') or 'n/a'}.",
    ]
    if book.get("new_canon"):
        parts.append("Canon: " + "; ".join(map(str, book["new_canon"])) + ".")
    return " ".join(parts)


def _update_timeline(summary: dict[str, Any]) -> None:
    timeline = read_json(CANON / "timeline.json")
    events = list(timeline.get("events") or [])
    for event in summary.get("major_events") or []:
        events.append(
            {
                "book_number": summary["book_number"],
                "event": event,
                "approved_at": summary["approved_at"],
            }
        )
    if not summary.get("major_events") and summary.get("adventure"):
        events.append(
            {
                "book_number": summary["book_number"],
                "event": summary["adventure"],
                "approved_at": summary["approved_at"],
            }
        )
    timeline["events"] = events
    write_json(CANON / "timeline.json", timeline)


def _update_locations(items: list[dict[str, Any]], number: int) -> None:
    data = read_json(CANON / "locations.json")
    locations = list(data.get("locations") or [])
    for item in items:
        if item.get("category") != "location":
            continue
        locations.append(
            {
                "name": item.get("fact"),
                "first_book": number,
                "notes": item.get("why_it_might_persist"),
            }
        )
    data["locations"] = locations
    write_json(CANON / "locations.json", data)


def _update_elements(items: list[dict[str, Any]], number: int) -> None:
    data = read_json(CANON / "recurring-elements.json")
    elements = list(data.get("elements") or [])
    for item in items:
        if item.get("category") not in {"object", "ritual", "phrase"}:
            continue
        elements.append(
            {
                "name": item.get("fact"),
                "category": item.get("category"),
                "first_book": number,
            }
        )
    data["elements"] = elements
    write_json(CANON / "recurring-elements.json", data)


def _update_threads(items: list[dict[str, Any]], number: int, summary: dict[str, Any]) -> None:
    data = read_json(CANON / "open-story-threads.json")
    threads = list(data.get("threads") or [])
    for item in items:
        if item.get("category") != "thread":
            continue
        threads.append(
            {
                "fact": item.get("fact"),
                "opened_in": number,
                "status": "open",
            }
        )
    data["threads"] = threads
    write_json(CANON / "open-story-threads.json", data)


def _update_character_state(summary: dict[str, Any]) -> None:
    data = read_json(CANON / "character-state.json")
    characters = data.get("characters") or {}
    focus = (summary.get("primary_character") or "").strip().lower()
    if focus in characters:
        characters[focus]["last_approved_book"] = summary["book_number"]
        growth = summary.get("character_growth") or []
        learned = list(characters[focus].get("lessons_learned") or [])
        for item in growth:
            if item and item not in learned:
                learned.append(item)
        characters[focus]["lessons_learned"] = learned
    data["characters"] = characters
    write_json(CANON / "character-state.json", data)


def _update_decisions(items: list[dict[str, Any]], number: int) -> None:
    data = read_json(CANON / "canon-decisions.json")
    decisions = list(data.get("decisions") or [])
    existing_ids = {d.get("id") for d in decisions}
    for item in items:
        if item.get("category") not in {"world_rule", "relationship"}:
            continue
        next_id = f"DEC-{len(decisions) + 1:04d}"
        while next_id in existing_ids:
            next_id = f"DEC-{len(existing_ids) + 1:04d}"
        decisions.append(
            {
                "id": next_id,
                "date": date.today().isoformat(),
                "status": "approved",
                "decision": item.get("fact"),
                "affects": [item.get("category")],
                "decided_by": f"book {number:03d}",
            }
        )
        existing_ids.add(next_id)
    data["decisions"] = decisions
    write_json(CANON / "canon-decisions.json", data)
