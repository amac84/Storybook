# Update canon

Run only after approval, or when Alex makes an explicit series decision outside a book.

## Mechanical update

`python3 scripts/archive-book.py NNN --approved` writes:

- a rich summary onto `canon/series-ledger.json`
- compressed summary for the book that just fell out of the recent window
- timeline events from approved major events
- new locations, characters, recurring elements, threads
- character-state patches listed in the book report
- canon decisions for promoted world rules

The same script separately records curriculum delivery to `curriculum/coverage-ledger.json` when the book declared objective IDs. That write is **not** a canon update — curriculum is studio planning memory (see `curriculum/README.md`).

## Keeper review

The Canon Keeper then checks:

- no temporary mud/wet-hair/one-book prop leaked into persistent possessions
- relationships changed only if approved
- open threads closed or created correctly
- character development files got a growth-log row
- visual incidental details were not promoted by accident
- no curriculum coverage data was written into `canon/` (it belongs in `curriculum/`), and no coverage entry was treated as character mastery

## Explicit series decisions

If Alex states a bible-level fact (“Cove is older”, “no talking animals”, “confidence means X”), write it into the relevant bible/character file **and** add a `canon-decisions.json` entry.

Do not hide a major decision only in a chat.

## Forbidden

- Editing canon to make a draft easier
- Deleting decisions because they are inconvenient
- Inventing facts to make the JSON look populated
