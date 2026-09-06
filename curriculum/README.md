# Curriculum

Persistent **studio planning memory**. This folder is NOT canon.

It answers: *what developmental objectives exist, which books have depicted them, and
what should the studio consider next* — without ever becoming story-world fact,
bible philosophy, or a claim about what a child (real or fictional) has mastered.

| file | holds |
| --- | --- |
| `catalog.yaml` | the objective catalog: stable IDs, definitions, prerequisites, story affordances |
| `coverage-ledger.json` | approval-only delivery records: which approved book depicted which objective |
| `intentions.yaml` | creator / Series Editor priorities, deferrals, and spacing hints for future briefs |

## Classification

This is a sixth class of fact alongside the ones in `.cursor/rules/continuity-rules.mdc`:

- **Curriculum record** — persistent, operational, non-canonical. It shapes *future briefs*;
  it never asserts anything about the story world.

## Boundaries

- **Not bible.** Value *meaning* stays in `bible/family-code.md` and
  `bible/values-and-principles.md`. Catalog objectives reference those definitions by name;
  they do not redefine them.
- **Not canon.** Nothing here is a story fact. Coverage never flows into `canon/`
  and canon archival never reads this folder for story continuity.
- **Not character mastery.** A book *depicting* an objective does not mean Cove or Mars
  (in-story or in real life) has learned it. Coverage terms are `depicted`, `rehearsed`,
  `transferred` — never `mastered`.
- **Not proposed canon.** Curriculum linkage does not go through
  `books/NNN/proposed-canon.yaml`.

## Lifecycle

1. Objectives are added to `catalog.yaml` only by Alex or with his approval
   (they constrain the whole series, like bible content).
2. A brief may *optionally* name a `primary_objective_id`. Context building injects only
   that objective's slice plus relevant coverage history.
3. On **human approval** of a book, `scripts/archive-book.py NNN --approved` writes one
   delivery record to `coverage-ledger.json` (idempotent per book number).
4. The Series Editor and `scripts/curriculum-status.py` read coverage + intentions to
   advise future briefs. Advice is advisory — story-first always wins.

## Current state

The catalog and stores are intentionally **empty**. No curriculum content has been
imported. Populate `catalog.yaml` only with creator-approved objectives, using
`templates/curriculum-objective.yaml` as the contract.
