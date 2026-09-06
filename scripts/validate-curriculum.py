#!/usr/bin/env python3
"""Validate curriculum store integrity: catalog, coverage ledger, intentions.

Empty stores are valid. This checks planning data only — it never reads or
writes canon/.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from studio.curriculum import (  # noqa: E402
    catalog_objectives,
    load_catalog,
    load_coverage,
    load_intentions,
    validate_catalog,
    validate_coverage,
    validate_intentions,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate curriculum/ stores.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result")
    args = parser.parse_args()

    catalog = load_catalog()
    coverage = load_coverage()
    intentions = load_intentions()

    errors = (
        validate_catalog(catalog)
        + validate_coverage(coverage, catalog)
        + validate_intentions(intentions, catalog)
    )
    result = {
        "passed": not errors,
        "errors": errors,
        "objectives": len(catalog_objectives(catalog)),
        "coverage_entries": len(coverage.get("entries") or []),
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "PASS" if result["passed"] else "FAIL"
        print(
            f"Curriculum {status}  objectives={result['objectives']}  "
            f"coverage_entries={result['coverage_entries']}"
        )
        for error in errors:
            print(f"  fail: {error}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
