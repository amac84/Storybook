# Characters

Major characters have a directory of structured files. The files are canon-in-progress. Approved persistent facts should also be reflected in `canon/`.

Do not invent detailed personalities or appearances to fill placeholders.

## Major characters

| id | name | status |
| --- | --- | --- |
| `cove` | Cove | personality-partial — cautious-smart-mischievous-sweet older brother; sings; athletic |
| `mars` | Eden / Mars | personality-partial — baby Hercules; most loving; stunt devil; artistic and physical |

Family tree: `characters/family.md`.

## How to add a major character

1. Copy `characters/_template/` to `characters/<id>/`.
2. Fill identity first, then personality, voice, development, and visual rules.
3. Add relationship rows in `canon/relationships.json`.
4. Add a state block in `canon/character-state.json`.
5. Place reference images in `characters/<id>/reference/`.
6. If they will recur as a protagonist, escalate — that is a series decision.

## How to add a supporting character

Use `characters/supporting/<id>.md` plus a short entry in `canon/character-state.json` if they persist. Do not give every extra a full six-file dossier.

## Reference images

Put approved stills in `reference/`:

- `01-hero.png` — first locked look
- later: turnaround, expressions, poses, wardrobe

The illustration pipeline must pass these files, not only text descriptions.

## Placeholder marker

Anything still unknown must remain `[CREATOR INPUT REQUIRED]` until the Series Bible pass or a later approved book.
