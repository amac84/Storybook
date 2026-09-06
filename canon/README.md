# Canon

Approved continuity lives here. Drafts may only **propose** facts.

| file | holds |
| --- | --- |
| `series-ledger.json` | book index, rich recent summaries, compressed older history |
| `timeline.json` | ordered approved events |
| `relationships.json` | approved relationships |
| `character-state.json` | persistent character facts and growth |
| `recurring-elements.json` | objects, phrases, rituals, returning jokes |
| `open-story-threads.json` | unpaid setups |
| `locations.json` | approved places |
| `canon-decisions.json` | explicit series decisions |

## Classes of fact

- **Canon** — here, and in filled character files
- **Temporary story state** — `books/NNN/art/visual-state.yaml` and the book report
- **Visual incidental** — in art direction / images only
- **Proposed canon** — `books/NNN/proposed-canon.yaml`
- **Curriculum record** — `curriculum/` (NOT here). Canon holds story continuity only. A book's `primary_value` in the ledger is a human-readable summary; objective coverage authority is `curriculum/coverage-ledger.json`, and coverage is never a story fact or character mastery.

## Updates

Only after human approval, via `workflows/update-canon.md` and `python3 scripts/archive-book.py NNN --approved`.

## Memory shape for each approved book

```yaml
book_number:
title:
primary_character:
primary_value:
secondary_values:
adventure:
major_events:
character_growth:
new_canon:
temporary_state:
new_locations:
new_characters:
recurring_elements:
unresolved_threads:
important_visual_details:
summary_rich:  # previous six
summary_compressed:  # older
```
