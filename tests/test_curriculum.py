#!/usr/bin/env python3
"""Tests for the curriculum layer: catalog validation, exact ID resolution,
advisory ranking, targeted context injection, per-book linkage gates, and
approval-only idempotent coverage persistence — all strictly separate from canon."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from studio import curriculum  # noqa: E402
from studio.curriculum import (  # noqa: E402
    advise_candidates,
    load_coverage,
    objective_slice,
    record_delivery,
    resolve_objective,
    validate_book_linkage,
    validate_catalog,
    validate_coverage,
)


CATALOG = {
    "version": 1,
    "domains": [{"id": "courage", "label": "Courage", "family_code_values": ["courage"]}],
    "objectives": [
        {
            "id": "OBJ-courage-first-try",
            "status": "active",
            "domain": "courage",
            "label": "Take the first try",
            "prerequisites": [],
        },
        {
            "id": "OBJ-courage-ask-help",
            "status": "active",
            "domain": "courage",
            "label": "Ask for help",
            "prerequisites": ["OBJ-courage-first-try"],
        },
        {
            "id": "OBJ-courage-retired",
            "status": "retired",
            "domain": "courage",
            "label": "Retired objective",
            "prerequisites": [],
        },
    ],
}

COVERAGE_ONE_BOOK = {
    "version": 1,
    "entries": [
        {
            "book_number": 1,
            "title": "Test Book",
            "primary_objective_id": "OBJ-courage-first-try",
            "secondary_objective_ids": [],
            "exposure": "depicted",
            "approved_at": "2026-09-05",
        }
    ],
}

EMPTY_COVERAGE = {"version": 1, "entries": []}


def _write_book(folder: Path, brief: dict, report: dict) -> None:
    (folder / "brief.yaml").write_text(yaml.dump(brief), encoding="utf-8")
    (folder / "book-report.yaml").write_text(yaml.dump(report), encoding="utf-8")


class CatalogValidationTests(unittest.TestCase):
    def test_empty_catalog_is_valid(self):
        self.assertEqual(validate_catalog({"version": 1, "domains": [], "objectives": []}), [])

    def test_valid_catalog(self):
        self.assertEqual(validate_catalog(CATALOG), [])

    def test_duplicate_ids(self):
        catalog = copy.deepcopy(CATALOG)
        catalog["objectives"].append(dict(catalog["objectives"][0]))
        errors = validate_catalog(catalog)
        self.assertTrue(any("Duplicate objective id" in e for e in errors))

    def test_bad_id_format(self):
        catalog = copy.deepcopy(CATALOG)
        catalog["objectives"][0]["id"] = "courage_first_try"
        errors = validate_catalog(catalog)
        self.assertTrue(any("does not match" in e for e in errors))

    def test_unknown_prerequisite(self):
        catalog = copy.deepcopy(CATALOG)
        catalog["objectives"][1]["prerequisites"] = ["OBJ-missing-thing"]
        errors = validate_catalog(catalog)
        self.assertTrue(any("unknown prerequisite" in e for e in errors))

    def test_prerequisite_cycle(self):
        catalog = copy.deepcopy(CATALOG)
        catalog["objectives"][0]["prerequisites"] = ["OBJ-courage-ask-help"]
        errors = validate_catalog(catalog)
        self.assertTrue(any("cycle" in e.lower() for e in errors))

    def test_unknown_domain(self):
        catalog = copy.deepcopy(CATALOG)
        catalog["objectives"][0]["domain"] = "nonsense"
        errors = validate_catalog(catalog)
        self.assertTrue(any("unknown domain" in e for e in errors))


class CoverageValidationTests(unittest.TestCase):
    def test_valid_coverage(self):
        self.assertEqual(validate_coverage(COVERAGE_ONE_BOOK, CATALOG), [])

    def test_unknown_objective_and_bad_exposure(self):
        coverage = copy.deepcopy(COVERAGE_ONE_BOOK)
        coverage["entries"][0]["primary_objective_id"] = "OBJ-not-real"
        coverage["entries"][0]["exposure"] = "mastered"
        errors = validate_coverage(coverage, CATALOG)
        self.assertTrue(any("unknown objective id" in e for e in errors))
        self.assertTrue(any("mastered" in e for e in errors))

    def test_duplicate_book_entries(self):
        coverage = copy.deepcopy(COVERAGE_ONE_BOOK)
        coverage["entries"].append(dict(coverage["entries"][0]))
        errors = validate_coverage(coverage, CATALOG)
        self.assertTrue(any("Duplicate coverage entry" in e for e in errors))


class ResolutionTests(unittest.TestCase):
    def test_exact_resolution(self):
        objective = resolve_objective("OBJ-courage-first-try", CATALOG)
        self.assertIsNotNone(objective)
        self.assertEqual(objective["label"], "Take the first try")

    def test_unknown_returns_none_no_fuzzy_match(self):
        self.assertIsNone(resolve_objective("OBJ-courage-first", CATALOG))
        self.assertIsNone(resolve_objective("first try", CATALOG))

    def test_slice_for_known_objective(self):
        result = objective_slice("OBJ-courage-ask-help", CATALOG, EMPTY_COVERAGE)
        self.assertTrue(result["resolved"])
        self.assertEqual(result["definition"]["label"], "Ask for help")
        self.assertFalse(result["prerequisites"][0]["already_depicted"])
        self.assertTrue(any("Prerequisite" in w for w in result["warnings"]))

    def test_slice_prereq_met_and_history(self):
        result = objective_slice("OBJ-courage-ask-help", CATALOG, COVERAGE_ONE_BOOK)
        self.assertTrue(result["prerequisites"][0]["already_depicted"])
        self.assertEqual(result["warnings"], [])
        history = objective_slice("OBJ-courage-first-try", CATALOG, COVERAGE_ONE_BOOK)
        self.assertEqual(history["coverage_history"][0]["book_number"], 1)

    def test_slice_for_unknown_objective(self):
        result = objective_slice("OBJ-nope-nope", CATALOG, EMPTY_COVERAGE)
        self.assertFalse(result["resolved"])
        self.assertTrue(result["warnings"])


class AdvisoryTests(unittest.TestCase):
    def test_empty_catalog_gives_no_candidates(self):
        self.assertEqual(advise_candidates({}, EMPTY_COVERAGE, {}), [])

    def test_never_depicted_with_met_prereqs_ranks_first(self):
        candidates = advise_candidates(CATALOG, COVERAGE_ONE_BOOK, {})
        self.assertEqual(candidates[0]["objective_id"], "OBJ-courage-ask-help")

    def test_priorities_outrank_recency(self):
        intentions = {
            "priorities": [{"objective_id": "OBJ-courage-first-try", "reason": "test"}]
        }
        candidates = advise_candidates(CATALOG, COVERAGE_ONE_BOOK, intentions)
        self.assertEqual(candidates[0]["objective_id"], "OBJ-courage-first-try")

    def test_deferrals_excluded_and_retired_excluded(self):
        intentions = {
            "deferrals": [{"objective_id": "OBJ-courage-ask-help", "reason": "wait"}]
        }
        candidates = advise_candidates(CATALOG, EMPTY_COVERAGE, intentions)
        ids = [c["objective_id"] for c in candidates]
        self.assertNotIn("OBJ-courage-ask-help", ids)
        self.assertNotIn("OBJ-courage-retired", ids)

    def test_ranking_is_deterministic(self):
        first = advise_candidates(CATALOG, COVERAGE_ONE_BOOK, {})
        second = advise_candidates(CATALOG, COVERAGE_ONE_BOOK, {})
        self.assertEqual(first, second)


class ContextInjectionTests(unittest.TestCase):
    def test_selected_objective_injected(self):
        from studio import context

        with patch.object(context, "load_catalog", return_value=CATALOG), patch.object(
            context, "load_coverage", return_value=COVERAGE_ONE_BOOK
        ), patch.object(context, "load_intentions", return_value={}):
            result = context._curriculum_slice({"primary_objective_id": "OBJ-courage-first-try"})
        self.assertTrue(result["selected_objective"]["resolved"])
        self.assertEqual(result["advisory_candidates"], [])
        self.assertEqual(result["recent_coverage"][0]["book_number"], 1)

    def test_free_text_brief_gets_advisory_only(self):
        from studio import context

        with patch.object(context, "load_catalog", return_value=CATALOG), patch.object(
            context, "load_coverage", return_value=EMPTY_COVERAGE
        ), patch.object(context, "load_intentions", return_value={}):
            result = context._curriculum_slice({"goal": "confidence when it is hard"})
        self.assertIsNone(result["selected_objective"])
        self.assertTrue(result["advisory_candidates"])


class BookLinkageTests(unittest.TestCase):
    def _linkage(self, brief: dict, report: dict) -> tuple[list[str], list[str]]:
        with tempfile.TemporaryDirectory() as tmp:
            book = Path(tmp)
            _write_book(book, brief, report)
            with patch.object(curriculum, "book_dir", return_value=book), patch.object(
                curriculum, "load_catalog", return_value=CATALOG
            ):
                return validate_book_linkage(99)

    def test_no_linkage_always_valid(self):
        failures, warnings = self._linkage(
            {"goal": "confidence", "primary_value": "confidence"}, {}
        )
        self.assertEqual(failures, [])
        self.assertEqual(warnings, [])

    def test_unknown_id_fails(self):
        failures, _ = self._linkage({"primary_objective_id": "OBJ-not-real"}, {})
        self.assertTrue(any("unknown objective id" in f for f in failures))

    def test_primary_equals_secondary_fails(self):
        failures, _ = self._linkage(
            {
                "primary_objective_id": "OBJ-courage-first-try",
                "secondary_objective_ids": ["OBJ-courage-first-try"],
            },
            {},
        )
        self.assertTrue(any("also listed as secondary" in f for f in failures))

    def test_brief_report_mismatch_fails(self):
        failures, _ = self._linkage(
            {"primary_objective_id": "OBJ-courage-first-try"},
            {"curriculum": {"primary_objective_id": "OBJ-courage-ask-help"}},
        )
        self.assertTrue(any("does not match" in f for f in failures))

    def test_retired_objective_warns(self):
        failures, warnings = self._linkage(
            {"primary_objective_id": "OBJ-courage-retired"}, {}
        )
        self.assertEqual(failures, [])
        self.assertTrue(any("retired" in w for w in warnings))

    def test_bad_exposure_fails(self):
        failures, _ = self._linkage(
            {"primary_objective_id": "OBJ-courage-first-try"},
            {
                "curriculum": {
                    "primary_objective_id": "OBJ-courage-first-try",
                    "exposure": "mastered",
                }
            },
        )
        self.assertTrue(any("mastered" in f for f in failures))


class RecordDeliveryTests(unittest.TestCase):
    BRIEF = {
        "working_title": "Test Book",
        "character_focus": "cove",
        "primary_objective_id": "OBJ-courage-first-try",
    }

    def _record(self, tmp: Path, report: dict, brief: dict | None = None):
        book = tmp / "book"
        book.mkdir(exist_ok=True)
        _write_book(book, brief or self.BRIEF, report)
        ledger = tmp / "coverage-ledger.json"
        with patch.object(curriculum, "book_dir", return_value=book), patch.object(
            curriculum, "load_catalog", return_value=CATALOG
        ):
            entry = record_delivery(7, coverage_path=ledger)
        return entry, ledger

    def test_refuses_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(PermissionError):
                self._record(Path(tmp), {"human_approval": "pending"})

    def test_records_approved_delivery(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = {
                "human_approval": "approved",
                "approved_at": "2026-09-05",
                "title": "Test Book",
                "portable_phrase": "Try one piece first.",
                "curriculum": {
                    "primary_objective_id": "OBJ-courage-first-try",
                    "exposure": "transferred",
                    "delivery_evidence": ["Spread 12: transfer beat"],
                },
            }
            entry, ledger = self._record(Path(tmp), report)
            self.assertEqual(entry["exposure"], "transferred")
            self.assertEqual(entry["portable_phrase"], "Try one piece first.")
            stored = json.loads(ledger.read_text(encoding="utf-8"))
            self.assertEqual(len(stored["entries"]), 1)
            self.assertEqual(stored["entries"][0]["book_number"], 7)
            self.assertNotIn("mastered", json.dumps(stored))

    def test_idempotent_rearchive_replaces_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = {"human_approval": "approved", "approved_at": "2026-09-05"}
            _, ledger = self._record(Path(tmp), report)
            report["curriculum"] = {
                "primary_objective_id": "OBJ-courage-first-try",
                "exposure": "rehearsed",
            }
            entry, ledger = self._record(Path(tmp), report)
            stored = json.loads(ledger.read_text(encoding="utf-8"))
            self.assertEqual(len(stored["entries"]), 1)
            self.assertEqual(stored["entries"][0]["exposure"], "rehearsed")

    def test_no_linkage_returns_none_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            entry, ledger = self._record(
                Path(tmp),
                {"human_approval": "approved"},
                brief={"working_title": "Plain Book", "goal": "confidence"},
            )
            self.assertIsNone(entry)
            self.assertFalse(ledger.exists())

    def test_invalid_linkage_blocks_recording(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                self._record(
                    Path(tmp),
                    {"human_approval": "approved"},
                    brief={"primary_objective_id": "OBJ-not-real"},
                )

    def test_never_touches_canon(self):
        """record_delivery writes only the coverage path it is given."""
        with tempfile.TemporaryDirectory() as tmp:
            before = {
                p: p.read_bytes() for p in (ROOT / "canon").rglob("*") if p.is_file()
            }
            report = {"human_approval": "approved"}
            self._record(Path(tmp), report)
            after = {
                p: p.read_bytes() for p in (ROOT / "canon").rglob("*") if p.is_file()
            }
            self.assertEqual(before, after)


class RepoStoreTests(unittest.TestCase):
    def test_curriculum_stores_exist_and_are_empty(self):
        catalog = yaml.safe_load(
            (ROOT / "curriculum" / "catalog.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(catalog.get("objectives"), [])
        self.assertEqual(validate_catalog(catalog), [])
        coverage = load_coverage(ROOT / "curriculum" / "coverage-ledger.json")
        self.assertEqual(coverage.get("entries"), [])


if __name__ == "__main__":
    raise SystemExit(unittest.main())
