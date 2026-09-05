# Schemas

Machine-readable contracts live in two places:

- `studio.yaml` — studio defaults and quality gates
- `scripts/studio/` — loaders, validators, and packet builders

YAML templates in `templates/` are the human-facing shapes. Scripts validate the subset that must be mechanically true (book folders, manuscript headings, editorial scores, approval flags).

JSON in `canon/` is authoritative for approved continuity. There is no separate JSON Schema pack yet; add one only if validation pain appears.
