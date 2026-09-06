"""Curriculum layer — persistent studio planning memory. NOT canon.

Loads and validates the objective catalog, resolves stable objective IDs,
builds targeted objective slices for context packets, records approval-only
delivery coverage, and ranks advisory candidates for future briefs.

Hard boundaries (see curriculum/README.md):
- never writes to canon/
- never records "mastered" — exposure is depicted | rehearsed | transferred
- absence of objective IDs in a book is always valid (backward compatible)
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

from .io import read_json, read_yaml, write_json
from .paths import (
    CURRICULUM_CATALOG,
    CURRICULUM_COVERAGE,
    CURRICULUM_INTENTIONS,
    book_dir,
)

OBJECTIVE_ID_PATTERN = re.compile(r"^OBJ-[a-z0-9]+(-[a-z0-9]+)+$")
EXPOSURE_TERMS = ("depicted", "rehearsed", "transferred")


# ---------------------------------------------------------------- loading

def load_catalog(path: Path | None = None) -> dict[str, Any]:
    data = read_yaml(path or CURRICULUM_CATALOG)
    return data if isinstance(data, dict) else {}


def load_coverage(path: Path | None = None) -> dict[str, Any]:
    target = path or CURRICULUM_COVERAGE
    if not target.exists():
        return {"version": 1, "entries": []}
    data = read_json(target)
    return data if isinstance(data, dict) else {"version": 1, "entries": []}


def load_intentions(path: Path | None = None) -> dict[str, Any]:
    data = read_yaml(path or CURRICULUM_INTENTIONS)
    return data if isinstance(data, dict) else {}


def catalog_objectives(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    return [o for o in (catalog.get("objectives") or []) if isinstance(o, dict)]


# ------------------------------------------------------------- validation

def validate_catalog(catalog: dict[str, Any]) -> list[str]:
    """Structural integrity of the catalog. An empty catalog is valid."""
    errors: list[str] = []
    domains = catalog.get("domains") or []
    domain_ids: list[str] = []
    for domain in domains:
        if not isinstance(domain, dict) or not domain.get("id"):
            errors.append(f"Domain entry missing id: {domain!r}")
            continue
        did = str(domain["id"])
        if did in domain_ids:
            errors.append(f"Duplicate domain id: {did}")
        domain_ids.append(did)

    objectives = catalog_objectives(catalog)
    seen: set[str] = set()
    for objective in objectives:
        oid = objective.get("id")
        if not oid:
            errors.append(f"Objective missing id: {objective.get('label')!r}")
            continue
        oid = str(oid)
        if not OBJECTIVE_ID_PATTERN.match(oid):
            errors.append(f"Objective id {oid!r} does not match OBJ-<domain>-<slug>")
        if oid in seen:
            errors.append(f"Duplicate objective id: {oid}")
        seen.add(oid)
        status = objective.get("status", "active")
        if status not in ("active", "retired"):
            errors.append(f"{oid}: status {status!r} must be active or retired")
        domain = objective.get("domain")
        if domain and domain_ids and domain not in domain_ids:
            errors.append(f"{oid}: unknown domain {domain!r}")

    ids = {str(o.get("id")) for o in objectives if o.get("id")}
    for objective in objectives:
        oid = str(objective.get("id"))
        for prereq in objective.get("prerequisites") or []:
            if prereq == oid:
                errors.append(f"{oid}: lists itself as a prerequisite")
            elif prereq not in ids:
                errors.append(f"{oid}: unknown prerequisite {prereq!r}")

    errors.extend(_prerequisite_cycles(objectives))
    return errors


def _prerequisite_cycles(objectives: list[dict[str, Any]]) -> list[str]:
    graph = {
        str(o.get("id")): [p for p in (o.get("prerequisites") or [])]
        for o in objectives
        if o.get("id")
    }
    errors: list[str] = []
    WHITE, GRAY, BLACK = 0, 1, 2
    state = dict.fromkeys(graph, WHITE)

    def visit(node: str, trail: list[str]) -> None:
        state[node] = GRAY
        for nxt in graph.get(node, []):
            if nxt not in graph:
                continue
            if state[nxt] == GRAY:
                cycle = trail[trail.index(nxt):] + [nxt] if nxt in trail else [node, nxt]
                errors.append("Prerequisite cycle: " + " -> ".join(cycle))
            elif state[nxt] == WHITE:
                visit(nxt, trail + [nxt])
        state[node] = BLACK

    for node in graph:
        if state[node] == WHITE:
            visit(node, [node])
    return errors


def validate_coverage(coverage: dict[str, Any], catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ids = {str(o.get("id")) for o in catalog_objectives(catalog) if o.get("id")}
    seen_books: set[int] = set()
    for entry in coverage.get("entries") or []:
        number = entry.get("book_number")
        if not isinstance(number, int):
            errors.append(f"Coverage entry missing integer book_number: {entry!r}")
            continue
        if number in seen_books:
            errors.append(f"Duplicate coverage entry for book {number}")
        seen_books.add(number)
        primary = entry.get("primary_objective_id")
        if primary and primary not in ids:
            errors.append(f"Book {number}: unknown objective id {primary!r}")
        for oid in entry.get("secondary_objective_ids") or []:
            if oid not in ids:
                errors.append(f"Book {number}: unknown secondary objective id {oid!r}")
        exposure = entry.get("exposure")
        if exposure and exposure not in EXPOSURE_TERMS:
            errors.append(
                f"Book {number}: exposure {exposure!r} must be one of {EXPOSURE_TERMS}"
            )
    return errors


def validate_intentions(intentions: dict[str, Any], catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ids = {str(o.get("id")) for o in catalog_objectives(catalog) if o.get("id")}
    for section in ("priorities", "deferrals"):
        for item in intentions.get(section) or []:
            oid = (item or {}).get("objective_id")
            if oid and oid not in ids:
                errors.append(f"intentions.{section}: unknown objective id {oid!r}")
    return errors


# ------------------------------------------------------------- resolution

def resolve_objective(
    objective_id: str, catalog: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    """Exact, stable ID lookup. Returns None for unknown IDs — no fuzzy matching."""
    catalog = catalog if catalog is not None else load_catalog()
    for objective in catalog_objectives(catalog):
        if str(objective.get("id")) == objective_id:
            return objective
    return None


def objective_slice(
    objective_id: str,
    catalog: dict[str, Any] | None = None,
    coverage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Targeted context-packet slice for one objective: definition, prerequisite
    readiness, this objective's coverage history, and warnings. Not a repo dump."""
    catalog = catalog if catalog is not None else load_catalog()
    coverage = coverage if coverage is not None else load_coverage()
    objective = resolve_objective(objective_id, catalog)
    if objective is None:
        return {
            "objective_id": objective_id,
            "resolved": False,
            "warnings": [f"Unknown objective id {objective_id!r} — not in curriculum/catalog.yaml"],
        }

    depicted = _depicted_objective_ids(coverage)
    prerequisites = []
    warnings: list[str] = []
    for prereq_id in objective.get("prerequisites") or []:
        prereq = resolve_objective(prereq_id, catalog)
        covered = prereq_id in depicted
        prerequisites.append(
            {
                "objective_id": prereq_id,
                "label": (prereq or {}).get("label"),
                "already_depicted": covered,
            }
        )
        if not covered:
            warnings.append(
                f"Prerequisite {prereq_id} has not been depicted in an approved book yet"
            )
    if objective.get("status") == "retired":
        warnings.append(f"Objective {objective_id} is retired in the catalog")

    history = [
        {
            "book_number": e.get("book_number"),
            "title": e.get("title"),
            "exposure": e.get("exposure"),
            "portable_phrase": e.get("portable_phrase"),
        }
        for e in _sorted_entries(coverage)
        if e.get("primary_objective_id") == objective_id
        or objective_id in (e.get("secondary_objective_ids") or [])
    ]

    return {
        "objective_id": objective_id,
        "resolved": True,
        "definition": {
            key: objective.get(key)
            for key in (
                "label",
                "domain",
                "family_code_values",
                "age_fit",
                "developmental_objective",
                "observable_story_behaviours",
                "common_misconceptions",
                "story_affordances",
                "transfer_opportunities",
                "portable_phrase_examples",
                "revisit_guidance",
            )
        },
        "prerequisites": prerequisites,
        "coverage_history": history,
        "warnings": warnings,
        "reminder": "Coverage is exposure, not mastery. Story first — the objective grows out of the trouble.",
    }


def _depicted_objective_ids(coverage: dict[str, Any]) -> set[str]:
    depicted: set[str] = set()
    for entry in coverage.get("entries") or []:
        if entry.get("primary_objective_id"):
            depicted.add(str(entry["primary_objective_id"]))
        depicted.update(str(x) for x in entry.get("secondary_objective_ids") or [])
    return depicted


def _sorted_entries(coverage: dict[str, Any]) -> list[dict[str, Any]]:
    entries = [e for e in (coverage.get("entries") or []) if isinstance(e, dict)]
    return sorted(entries, key=lambda e: e.get("book_number") or 0)


def recent_coverage(
    coverage: dict[str, Any] | None = None, window: int = 6
) -> list[dict[str, Any]]:
    coverage = coverage if coverage is not None else load_coverage()
    return _sorted_entries(coverage)[-window:]


# --------------------------------------------------------------- advisory

def advise_candidates(
    catalog: dict[str, Any] | None = None,
    coverage: dict[str, Any] | None = None,
    intentions: dict[str, Any] | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Deterministic advisory ranking of active objectives for a next brief.

    Order: creator/Series Editor priorities first, then never-depicted objectives
    whose prerequisites are met, then least-recently depicted. Deferred objectives
    are excluded. Purely advisory — never forces a brief.
    """
    catalog = catalog if catalog is not None else load_catalog()
    coverage = coverage if coverage is not None else load_coverage()
    intentions = intentions if intentions is not None else load_intentions()

    objectives = [
        o for o in catalog_objectives(catalog) if o.get("status", "active") == "active"
    ]
    if not objectives:
        return []

    depicted = _depicted_objective_ids(coverage)
    last_book: dict[str, int] = {}
    for entry in _sorted_entries(coverage):
        number = entry.get("book_number") or 0
        for oid in [entry.get("primary_objective_id"), *(entry.get("secondary_objective_ids") or [])]:
            if oid:
                last_book[str(oid)] = number

    deferred = {
        str(d.get("objective_id"))
        for d in (intentions.get("deferrals") or [])
        if d.get("objective_id")
    }
    priority_rank = {
        str(p.get("objective_id")): index
        for index, p in enumerate(intentions.get("priorities") or [])
        if p.get("objective_id")
    }

    candidates = []
    for index, objective in enumerate(objectives):
        oid = str(objective.get("id"))
        if oid in deferred:
            continue
        prereqs = objective.get("prerequisites") or []
        prereqs_met = all(p in depicted for p in prereqs)
        reasons = []
        if oid in priority_rank:
            reasons.append("listed in curriculum/intentions.yaml priorities")
        if oid not in depicted:
            reasons.append("never depicted in an approved book")
        else:
            reasons.append(f"last depicted in book {last_book.get(oid)}")
        if not prereqs_met:
            reasons.append("prerequisites not yet depicted")
        candidates.append(
            {
                "objective_id": oid,
                "label": objective.get("label"),
                "reasons": reasons,
                "_sort": (
                    priority_rank.get(oid, len(priority_rank) + 1),
                    0 if prereqs_met else 1,
                    last_book.get(oid, -1),
                    index,
                ),
            }
        )

    candidates.sort(key=lambda c: c["_sort"])
    for candidate in candidates:
        candidate.pop("_sort")
    return candidates[:limit]


# ------------------------------------------------------ book-level checks

def brief_objective_ids(brief: dict[str, Any]) -> tuple[str | None, list[str]]:
    primary = brief.get("primary_objective_id") or None
    secondary = [s for s in (brief.get("secondary_objective_ids") or []) if s]
    return primary, secondary


def validate_book_linkage(number: int) -> tuple[list[str], list[str]]:
    """Gate checks for a book's optional curriculum linkage.

    Returns (failures, warnings). Books with no objective IDs pass untouched.
    """
    failures: list[str] = []
    warnings: list[str] = []
    book = book_dir(number)
    brief = read_yaml(book / "brief.yaml") or {}
    report = read_yaml(book / "book-report.yaml") or {}
    catalog = load_catalog()
    known = {str(o.get("id")) for o in catalog_objectives(catalog) if o.get("id")}

    brief_primary, brief_secondary = brief_objective_ids(brief)
    report_block = report.get("curriculum") or {}
    report_primary = report_block.get("primary_objective_id") or None
    report_secondary = [s for s in (report_block.get("secondary_objective_ids") or []) if s]

    all_ids = [
        ("brief primary_objective_id", brief_primary),
        *[("brief secondary_objective_ids", s) for s in brief_secondary],
        ("report curriculum.primary_objective_id", report_primary),
        *[("report curriculum.secondary_objective_ids", s) for s in report_secondary],
    ]
    if not any(oid for _, oid in all_ids):
        return failures, warnings  # no linkage — always valid

    for label, oid in all_ids:
        if oid and oid not in known:
            failures.append(f"{label}: unknown objective id {oid!r}")
        elif oid:
            objective = resolve_objective(oid, catalog)
            if objective and objective.get("status") == "retired":
                warnings.append(f"{label}: objective {oid} is retired in the catalog")

    if brief_primary and brief_primary in brief_secondary:
        failures.append("brief: primary objective also listed as secondary")
    if report_primary and report_primary in report_secondary:
        failures.append("report: primary objective also listed as secondary")
    if brief_primary and report_primary and brief_primary != report_primary:
        failures.append(
            f"brief primary_objective_id {brief_primary!r} does not match "
            f"report curriculum.primary_objective_id {report_primary!r}"
        )

    exposure = report_block.get("exposure")
    if exposure and exposure not in EXPOSURE_TERMS:
        failures.append(
            f"report curriculum.exposure {exposure!r} must be one of {EXPOSURE_TERMS}"
        )
    return failures, warnings


# ------------------------------------------------------------ persistence

def record_delivery(number: int, coverage_path: Path | None = None) -> dict[str, Any] | None:
    """Write one delivery record for an approved book. Idempotent by book number.

    Refuses without human approval. Returns the entry, or None when the book
    declares no curriculum linkage (which is always allowed).
    Never touches canon/.
    """
    book = book_dir(number)
    report = read_yaml(book / "book-report.yaml") or {}
    if report.get("human_approval") != "approved":
        raise PermissionError(
            f"Book {number:03d} is not approved. Refusing to record curriculum delivery."
        )

    brief = read_yaml(book / "brief.yaml") or {}
    report_block = report.get("curriculum") or {}
    brief_primary, brief_secondary = brief_objective_ids(brief)
    primary = report_block.get("primary_objective_id") or brief_primary
    secondary = [
        s for s in (report_block.get("secondary_objective_ids") or brief_secondary) if s
    ]
    if not primary and not secondary:
        return None  # book has no curriculum linkage — nothing to record

    failures, _ = validate_book_linkage(number)
    if failures:
        raise ValueError(
            f"Book {number:03d} curriculum linkage invalid: " + "; ".join(failures)
        )

    entry = {
        "book_number": number,
        "title": report.get("title") or brief.get("working_title"),
        "primary_objective_id": primary,
        "secondary_objective_ids": secondary,
        "exposure": report_block.get("exposure") or "depicted",
        "delivery_evidence": report_block.get("delivery_evidence") or [],
        "portable_phrase": report.get("portable_phrase"),
        "character_focus": brief.get("character_focus"),
        "approved_at": report.get("approved_at") or date.today().isoformat(),
    }

    target = coverage_path or CURRICULUM_COVERAGE
    coverage = load_coverage(target)
    entries = [
        e for e in (coverage.get("entries") or []) if e.get("book_number") != number
    ]
    entries.append(entry)
    coverage["entries"] = sorted(entries, key=lambda e: e.get("book_number") or 0)
    write_json(target, coverage)
    return entry
