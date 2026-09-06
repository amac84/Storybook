# Series review

The Series Editor is not part of every book.

## When

After every 8–10 approved books (`studio.yaml` `series_review_interval`, default 8), or when Alex asks.

## Who

`.cursor/agents/series-editor.md`

## What

Evaluate repetition, role balance, adult overuse, location diversity, emotional evolution, overdue mysteries, formula risk, and beloved elements.

For value/objective coverage, read `curriculum/coverage-ledger.json` and `python3 scripts/curriculum-status.py` instead of inferring from ledger strings. Write coverage recommendations (priorities, deferrals, spacing notes) into `curriculum/intentions.yaml` — they are advisory hints for future briefs, not canon.

Produce recommendations for **future** briefs. Do not rewrite old books unless Alex asks.

## Output

Create `canon/series-reviews/after-book-NNN.md` (folder may be created at first review) and set `last_series_review_after_book` on the ledger.

The Showrunner should use the recommendations when interpreting the next briefs, not mechanically invert every pattern.
