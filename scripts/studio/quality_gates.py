from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import quality_gates
from .curriculum import validate_book_linkage
from .io import read_yaml
from .manuscript import validate_manuscript
from .paths import book_dir


STAGES = ("scaffold", "manuscript", "illustration", "approval")


def latest_editorial(book: Path) -> tuple[Path | None, dict[str, Any]]:
    versions = sorted(book.glob("editorial-v*.yaml"))
    if not versions:
        return None, {}
    path = versions[-1]
    return path, read_yaml(path) or {}


def evaluate(number: int, stage: str = "manuscript") -> dict[str, Any]:
    if stage not in STAGES:
        raise ValueError(f"Unknown stage {stage!r}. Expected one of {STAGES}")

    book = book_dir(number)
    gates = quality_gates()
    failures: list[str] = []
    warnings: list[str] = []
    checks: dict[str, Any] = {}

    if not book.exists():
        return _result(False, [f"Missing book directory {book}"], warnings, checks, None, {})

    brief = read_yaml(book / "brief.yaml") or {}
    if not brief:
        failures.append("brief.yaml is missing or empty")

    if stage == "scaffold":
        for required in ("brief.yaml", "context-packet.yaml"):
            if not (book / required).exists():
                failures.append(f"Missing {required}")
        return _result(not failures, failures, warnings, checks, None, {})

    editorial_path, editorial = latest_editorial(book)
    report = read_yaml(book / "book-report.yaml") or {}
    overrides = {item.get("gate"): item for item in report.get("quality_gate_overrides") or []}

    manuscript = book / "manuscript-final.md"
    if not manuscript.exists():
        manuscript = book / "manuscript-v2.md"
    if not manuscript.exists():
        manuscript = book / "manuscript-v1.md"

    if stage in ("manuscript", "illustration", "approval"):
        if not manuscript.exists():
            failures.append("No manuscript-v1/v2/final.md found")
        else:
            ms_errors = validate_manuscript(manuscript)
            failures.extend(ms_errors)
            checks["manuscript"] = str(manuscript.relative_to(book.parent.parent))
        if not editorial:
            failures.append("No editorial-vN.yaml found")
        else:
            checks["editorial"] = editorial_path.name if editorial_path else None
            _score_gates(editorial, gates, overrides, failures, warnings, checks)
            _flag_gates(editorial, gates, overrides, failures, warnings, checks)

        proposed = read_yaml(book / "proposed-canon.yaml") or {}
        checks["proposed_canon_items"] = len(proposed.get("items") or [])

        # Optional curriculum linkage: absence is always valid; invalid IDs fail.
        curriculum_failures, curriculum_warnings = validate_book_linkage(number)
        failures.extend(curriculum_failures)
        warnings.extend(curriculum_warnings)
        checks["curriculum_linkage"] = (
            "none"
            if not curriculum_failures and not curriculum_warnings and not _has_linkage(book)
            else ("invalid" if curriculum_failures else "ok")
        )

    if stage in ("illustration", "approval"):
        if not (book / "art" / "direction.yaml").exists():
            failures.append("Missing art/direction.yaml")
        qa = read_yaml(book / "art" / "qa.yaml") or {}
        if qa.get("result") == "FAIL":
            _fail_or_override("visual_qa", "Visual QA is FAIL", overrides, failures, warnings)
        elif stage == "approval" and qa.get("result") not in {"PASS", None}:
            warnings.append("Visual QA is not PASS")
        if qa.get("result") is None and stage == "approval":
            warnings.append("Visual QA has not been recorded (acceptable if no images yet)")

    if stage == "approval":
        if report.get("human_approval") != "approved":
            failures.append("book-report.yaml human_approval is not 'approved'")

    passed = not failures
    return _result(passed, failures, warnings, checks, editorial_path, editorial)


def _has_linkage(book: Path) -> bool:
    brief = read_yaml(book / "brief.yaml") or {}
    report = read_yaml(book / "book-report.yaml") or {}
    report_block = report.get("curriculum") or {}
    return bool(
        brief.get("primary_objective_id")
        or brief.get("secondary_objective_ids")
        or report_block.get("primary_objective_id")
        or report_block.get("secondary_objective_ids")
    )


def _score_gates(
    editorial: dict[str, Any],
    gates: dict[str, Any],
    overrides: dict[str, Any],
    failures: list[str],
    warnings: list[str],
    checks: dict[str, Any],
) -> None:
    mapping = {
        "engagement_score": "engagement_score_minimum",
        "story_score": "story_score_minimum",
        "character_score": "character_score_minimum",
        "values_score": "values_score_minimum",
    }
    for field, gate in mapping.items():
        score = editorial.get(field)
        minimum = gates[gate]
        checks[field] = score
        if score is None:
            _fail_or_override(gate, f"{field} is missing", overrides, failures, warnings)
            continue
        if score < minimum:
            _fail_or_override(
                gate,
                f"{field} {score} < minimum {minimum}",
                overrides,
                failures,
                warnings,
            )


def _flag_gates(
    editorial: dict[str, Any],
    gates: dict[str, Any],
    overrides: dict[str, Any],
    failures: list[str],
    warnings: list[str],
    checks: dict[str, Any],
) -> None:
    numeric = {
        "canon_violations": editorial.get("canon_violations_noted", 0),
        "character_violations": editorial.get("character_violations_noted", 0),
        "unresolved_major_plot_issues": editorial.get("unresolved_major_plot_issues", 0),
    }
    for gate, value in numeric.items():
        checks[gate] = value
        if value != gates[gate]:
            _fail_or_override(gate, f"{gate} is {value}, required {gates[gate]}", overrides, failures, warnings)

    flags = {
        "meaningful_protagonist_choice": editorial.get("meaningful_protagonist_choice"),
        "climax_driven_by_character_action": editorial.get("climax_driven_by_character_action"),
        "lesson_demonstrated_through_story": editorial.get("lesson_demonstrated_through_story"),
        "would_still_be_good_without_lesson": editorial.get("would_still_be_good_without_lesson"),
        "precise_developmental_objective": editorial.get("precise_developmental_objective"),
        "portable_phrase_present": editorial.get("portable_phrase_present"),
        "setback_present": editorial.get("setback_present"),
        "ending_does_not_explain_lesson": editorial.get("ending_does_not_explain_lesson"),
    }
    if editorial.get("adult_solves_central_problem") is True:
        flags["climax_driven_by_character_action"] = False
    if editorial.get("preachiness_detected") is True:
        flags["ending_does_not_explain_lesson"] = False
        flags["would_still_be_good_without_lesson"] = False
    for gate, value in flags.items():
        checks[gate] = value
        if value is not True:
            _fail_or_override(gate, f"{gate} is {value}, required true", overrides, failures, warnings)


def _fail_or_override(
    gate: str,
    message: str,
    overrides: dict[str, Any],
    failures: list[str],
    warnings: list[str],
) -> None:
    if gate in overrides and overrides[gate].get("reason"):
        warnings.append(f"OVERRIDE {gate}: {message} — {overrides[gate]['reason']}")
        return
    failures.append(message)


def _result(
    passed: bool,
    failures: list[str],
    warnings: list[str],
    checks: dict[str, Any],
    editorial_path: Path | None,
    editorial: dict[str, Any],
) -> dict[str, Any]:
    return {
        "passed": passed,
        "failures": failures,
        "warnings": warnings,
        "checks": checks,
        "editorial_file": editorial_path.name if editorial_path else None,
        "scores": {
            "engagement": editorial.get("engagement_score"),
            "story": editorial.get("story_score"),
            "character": editorial.get("character_score"),
            "values": editorial.get("values_score"),
            "read_aloud": editorial.get("read_aloud_score"),
            "overall": editorial.get("overall_score"),
        },
    }
