# Approve a book

Human approval is the only event that promotes proposed canon.

## Review package

The Showrunner presents the concise package from `AGENTS.md`, not the entire editorial history.

Alex may:

- **approve**
- **approve with canon notes** (promote only a subset)
- **return** for revision (manuscript, art, or both)

## On approval

1. Set `book-report.yaml` `human_approval: approved` and `approved_at`.
2. Confirm which proposed-canon items promote. Default: the list in the review package unless Alex strikes items.
3. Run `python3 scripts/archive-book.py NNN --approved`. Besides canon, this writes the book's curriculum delivery record to `curriculum/coverage-ledger.json` when objective IDs were declared (idempotent per book; separate from canon; exposure only, never mastery).
4. Canon Keeper performs `workflows/update-canon.md` (the archive script does the mechanical writes; the keeper reviews diffs). Confirm no curriculum data leaked into `canon/`.
5. Move or confirm images in `art/approved/`.
6. Expire `art/visual-state.yaml` temporary facts that were not promoted.
7. Mark the book approved on `canon/series-ledger.json`.
8. If `books_approved` is a multiple of the series review interval, schedule the Series Editor.

## On return

1. Set `human_approval: returned` and write `return_notes`.
2. Do not touch `canon/`.
3. Create the next manuscript or art version. Do not overwrite the returned files.
4. Record generalizable taste in `bible/creator-taste.md` if the notes warrant it.

## Never

- Promote canon because scores were high
- Delete draft history after approval
- Update developmental arcs from an unapproved ending
