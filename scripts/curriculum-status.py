#!/usr/bin/env python3
"""Human-readable curriculum status: coverage, intentions, advisory candidates.

Advisory only. Coverage is exposure (depicted/rehearsed/transferred), never mastery.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from studio.curriculum import (  # noqa: E402
    advise_candidates,
    catalog_objectives,
    load_catalog,
    load_coverage,
    load_intentions,
    recent_coverage,
)


def build_status(limit: int) -> dict:
    catalog = load_catalog()
    coverage = load_coverage()
    intentions = load_intentions()

    objectives = catalog_objectives(catalog)
    entries = coverage.get("entries") or []
    counts: dict[str, int] = {}
    last_depicted: dict[str, int] = {}
    for entry in sorted(entries, key=lambda e: e.get("book_number") or 0):
        for oid in [
            entry.get("primary_objective_id"),
            *(entry.get("secondary_objective_ids") or []),
        ]:
            if oid:
                counts[oid] = counts.get(oid, 0) + 1
                last_depicted[oid] = entry.get("book_number") or 0

    return {
        "objectives_in_catalog": len(objectives),
        "coverage_entries": len(entries),
        "coverage_by_objective": [
            {
                "objective_id": str(o.get("id")),
                "label": o.get("label"),
                "status": o.get("status", "active"),
                "times_covered": counts.get(str(o.get("id")), 0),
                "last_book": last_depicted.get(str(o.get("id"))),
            }
            for o in objectives
        ],
        "recent_coverage": recent_coverage(coverage),
        "priorities": intentions.get("priorities") or [],
        "deferrals": intentions.get("deferrals") or [],
        "suggested_candidates": advise_candidates(catalog, coverage, intentions, limit=limit),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Show curriculum coverage and advice.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable status")
    parser.add_argument("--limit", type=int, default=5, help="Max advisory candidates")
    args = parser.parse_args()

    status = build_status(args.limit)
    if args.json:
        print(json.dumps(status, indent=2))
        return 0

    print(
        f"Curriculum status: {status['objectives_in_catalog']} objectives, "
        f"{status['coverage_entries']} coverage entries"
    )
    if not status["coverage_by_objective"]:
        print("Catalog is empty. Populate curriculum/catalog.yaml with creator-approved objectives.")
    for row in status["coverage_by_objective"]:
        last = f"last book {row['last_book']}" if row["last_book"] else "never depicted"
        retired = " (retired)" if row["status"] == "retired" else ""
        print(f"  {row['objective_id']}{retired}: {row['times_covered']}x, {last}")
    if status["priorities"]:
        print("Priorities:")
        for item in status["priorities"]:
            print(f"  {item.get('objective_id')}: {item.get('reason')}")
    if status["deferrals"]:
        print("Deferrals:")
        for item in status["deferrals"]:
            print(f"  {item.get('objective_id')}: {item.get('reason')}")
    if status["suggested_candidates"]:
        print("Suggested candidates for a next brief (advisory only):")
        for candidate in status["suggested_candidates"]:
            print(f"  {candidate['objective_id']} — {'; '.join(candidate['reasons'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
