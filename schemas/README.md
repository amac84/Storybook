# Schemas

Machine-readable contracts live in two places:

- `studio.yaml` — studio defaults and quality gates
- `scripts/studio/` — loaders, validators, and packet builders

YAML templates in `templates/` are the human-facing shapes. Scripts validate the subset that must be mechanically true (book folders, manuscript headings, editorial scores, approval flags).

JSON in `canon/` is authoritative for approved continuity. There is no separate JSON Schema pack yet; add one only if validation pain appears.

## Curriculum stores

`curriculum/` is persistent studio planning memory, not canon:

- `curriculum/catalog.yaml` — objective catalog. Entry shape: `templates/curriculum-objective.yaml`. IDs are stable (`OBJ-<domain>-<slug>`), unique, never reused; `status` is `active | retired`.
- `curriculum/coverage-ledger.json` — one entry per approved book that declared objective IDs, keyed by `book_number` (idempotent). `exposure` is `depicted | rehearsed | transferred` — never `mastered`.
- `curriculum/intentions.yaml` — advisory priorities/deferrals/spacing notes.

Mechanical validation: `python3 scripts/validate-curriculum.py` (store integrity) and the curriculum checks inside `scripts/studio/quality_gates.py` (per-book linkage). Coverage is written only by `scripts/archive-book.py` after human approval.
