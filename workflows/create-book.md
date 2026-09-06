# Create a book

Showrunner workflow. Do not write Book 1 unless Alex asked for a book.

## Sequence

1. **Receive book direction from Alex.** It may be as short as a goal, an adventure seed, a character focus, and a tone.
2. **Create a structured book brief.** Run `python3 scripts/new-book.py` (optionally `--brief path.yaml`). Write `books/NNN/brief.yaml` using only fields that matter.
3. **Sharpen the developmental objective.** If the goal is still broad (“be confident”), the Showrunner writes Situation / Feeling / Belief / Strategy into the brief *before* outlining. Bind it to one Family Code value. Optionally set `primary_objective_id` from `curriculum/catalog.yaml` — the ID must resolve exactly; free-text goals remain fully valid. Do not ask Alex to complete the template unless a new series definition would be locked.
4. **Ask the Canon Keeper for a context packet.** Prefer `python3 scripts/build-context.py NNN`, then trim or enrich. Save `context-packet.yaml`. Include the sharpened objective and `bible/story-design-principles.md`. The packet's `curriculum` block carries the selected objective slice (or advisory candidates); it informs the target, never the plot. Confirm `house_style`, `creator_preferences_relevant`, `visual_style_relevant`, and `engagement_notes` survived any trim.
5. **Ask the Story Architect for story architecture.** Save `outline-v1.yaml`. The architect starts from the boys’ want, not from the curriculum, and must obey packet taste (house style, north stars, engagement notes), not a generic picture-book shape. Must include portable phrase, see→try→own, setback, transfer, reader-ahead beat.
6. **Showrunner evaluates the architecture** against `bible/story-design-principles.md`: would it still be a story with the lesson label peeled off? Precise objective? Child-sayable phrase? Setback? Invisible machinery? Family Code?
7. **If architecture is weak, revise it automatically.** Save `outline-v2.yaml` or later. Copy the accepted sheet to `outline-final.yaml`.
8. **Showrunner writes `manuscript-v1.md`** in spread format. Story first. No moral captions.
9. **Editorial Critic independently evaluates v1** with the Standard table. Save `editorial-v1.yaml`. No replacement prose.
10. **Showrunner revises** to `manuscript-v2.md`.
11. **Editorial Critic evaluates again.** Save `editorial-v2.yaml`.
12. **Showrunner performs a final revision** to `manuscript-final.md` if required. Do not overwrite v1 or v2.
13. **Validate quality gates.** Canon Keeper lists proposed canon and contradictions. Run `python3 scripts/validate-book.py NNN --stage manuscript`.
14. **Lock the manuscript** if gates pass or a documented override exists in `book-report.yaml`. Walk the Standard table first.
15. **Art Director creates spread-level visual direction.** Write `art/direction.yaml` and `art/visual-state.yaml`. Plant reread clues and at least one “reader sees it first” detail.
16. **Illustration pipeline** generates images when tools are connected. See `workflows/illustration-pipeline.md`.
17. **Visual QA** checks each image.
18. **Failed images regenerate.** Automatic, unless a fail is actually a brief/direction error.
19. **Assemble the book** into `production/` when assembly tools exist.
20. **Create the final report.** Include portable phrase and one outside-the-book probe for Alex.
21. **Present the completed book for human approval.** Do not dump intermediate thinking.
22. **Only after approval:** update canon, timeline, developmental state, recurring elements, and recent-book memory. See `workflows/approve-book.md`.

## File creation

Never overwrite significant drafts. If a third editorial pass is needed, use `manuscript-v3.md` and `editorial-v3.yaml`, then replace `manuscript-final.md`.

## Escalation during this workflow

Stop and ask one question only if a step would lock long-term canon, philosophy, or safety. Otherwise invent the incidental and list it as local or proposed.

## If looks or home details are still placeholder

You may still write a book if Alex asks. Do not invent permanent appearance or a named town. Mark proposed visual canon. Prefer a reference image before illustration lock.
