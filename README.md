# Cove and Mars — Children’s Book Studio

This repository is the operating system for a long-running, personalized, illustrated children’s series.

It is a small autonomous publishing studio. The main Cursor agent is the Showrunner. Specialist agents do narrow jobs. **The files are the source of truth.** Conversational memory is not canon.

The first books are for two brothers, Cove and Eden/Mars. The architecture also has to survive additional characters and, later, a broader published series.

Governing ethics: `bible/family-code.md` (McAulay Family Code).
Craft: `bible/story-design-principles.md` — story first, one precise objective, one portable phrase.

No book has been written yet. Do not treat remaining placeholders as finished visual or world canon.

---

## Philosophy

Optimize at the same time for:

1. stories children want to hear again
2. character consistency
3. adventure
4. humour and delight
5. emotional warmth
6. lessons that are lived, not preached — a strategy and phrase the child can use later
7. long-term growth
8. continuity across many books
9. visual consistency
10. little human intervention after a brief

Core rules:

- **One owner of prose.** The Showrunner writes and revises. Critics do not rewrite.
- **Creation and criticism are separate.** The architect does not grade its own plot as excellent.
- **Canon is explicit.** Personality, appearance, history, relationships, possessions, capabilities, fears, and facts do not drift.
- **Lessons emerge through story.** The value shapes choice, problem, escalation, climax, and resolution.
- **Children have agency.** Adults do not arrive and solve the central problem.
- **Stories are visually conceived.** Manuscripts are spread-by-spread. Pictures carry information the text should not repeat.
- **Autonomous by default.** Invent incidentals. Escalate only long-term canon, philosophy, or series decisions.

---

## Folder structure

```text
/
├── AGENTS.md                 Showrunner operating instructions
├── studio.yaml               Shared defaults and quality gates
├── .cursor/agents/           Specialist agent briefs
├── .cursor/rules/            Always-on / scoped studio rules
├── bible/                    Human-authored philosophy (not invented canon)
├── characters/               Cove, Mars, supporting, plus _template
├── canon/                    Approved machine-readable continuity
├── books/                    One numbered folder per book
├── templates/                YAML/Markdown shapes for artifacts
├── workflows/                Human-readable production procedures
├── scripts/                  new-book, build-context, validate-book, archive-book
└── tools/
    ├── image-generation/     Provider-agnostic illustration contract
    └── book-assembly/        Later layout / proofing
```

---

## Agents

| Role | Where | Job |
| --- | --- | --- |
| Showrunner / Author | `AGENTS.md` | Brief, context, prose, revision loops, gates, escalation, files |
| Story Architect | `.cursor/agents/story-architect.md` | Beat sheet before prose |
| Editorial Critic | `.cursor/agents/editorial-critic.md` | Independent evaluation; no rewrite |
| Canon Keeper | `.cursor/agents/canon-keeper.md` | Targeted packets, contradiction flags, post-approval updates |
| Art Director | `.cursor/agents/art-director.md` | Spread-level visual screenplay after manuscript lock |
| Visual QA | `.cursor/agents/visual-qa.md` | PASS/FAIL vs references, direction, continuity |
| Series Editor | `.cursor/agents/series-editor.md` | Every 8–10 approved books; future recommendations |

Writing loop:

```text
Story Architect → Showrunner draft → Editorial Critic →
Showrunner revision → Editorial Critic → Showrunner final
```

---

## How to start a new book

From the repo root, after Python deps:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/new-book.py
python3 scripts/new-book.py --goal "..." --adventure "..." --character-focus Cove --tone "exciting, funny, warm"
```

A short brief is enough:

```yaml
goal: Confidence when you don't initially know how to do something.
adventure: An old lighthouse during a storm.
character_focus: Cove
supporting_character_role: Mars unexpectedly solves an important piece of the problem.
tone: Exciting, mysterious, funny, warm.
special_elements: Use the lighthouse lens somehow.
```

Then:

```bash
python3 scripts/build-context.py 1
# Showrunner + agents follow workflows/create-book.md
python3 scripts/validate-book.py 1 --stage manuscript
```

Do not begin Book 1 until the Series Bible is populated enough that Cove, Mars, values, and world rules are no longer blank.

---

## Where artifacts appear

| Thing | Path |
| --- | --- |
| Brief, packet, outlines, manuscripts, editorial | `books/NNN/` |
| Versioned drafts | `manuscript-v1.md`, `v2`, `final` — never overwrite |
| Art direction + temporary visual state | `books/NNN/art/` |
| Generated frames | `books/NNN/art/generated/` |
| QA-passed frames | `books/NNN/art/approved/` |
| Layout / proof | `books/NNN/production/` |
| Human review scores | `books/NNN/book-report.yaml` |
| Proposed facts | `books/NNN/proposed-canon.yaml` |

---

## How to define values

The McAulay Family Code is locked in `bible/family-code.md`.
Operational schemas (what each value is and is **not**) live in `bible/values-and-principles.md`.

Do not let an agent redefine confidence as “believe you are the best,” or strength as dominance.

A book brief names **one** primary code value. The story must dramatize it. It must not teach all thirteen principles at once.

---

## How to define character canon

1. Fill `characters/cove/` and `characters/mars/` (identity, personality, voice, development, visual rules).
2. Put approved reference images in each `reference/` folder. One hero still is enough to start; later add turnarounds, expressions, poses, wardrobe.
3. Mirror persistent facts into `canon/character-state.json` and `canon/relationships.json`.
4. Leave `[CREATOR INPUT REQUIRED]` until you actually know the fact.

Copy `characters/_template/` for a new major character. Use `characters/supporting/<id>.md` for extras. A new recurring protagonist needs a human escalation.

---

## How canon is updated

Drafts only **propose** facts.

After you approve a book:

```bash
# book-report.yaml must say human_approval: approved
python3 scripts/archive-book.py 1 --approved
```

That updates the ledger, timeline, locations, elements, threads, character state, and decisions. Temporary mud, wet hair, and one-book props expire unless you promote them.

The previous six approved books keep richer summaries. Older books compress into persistent canon so the series can scale.

---

## How to add character reference images

Drop files in:

- `characters/cove/reference/`
- `characters/mars/reference/`

Suggested names: `01-hero.png`, `02-turnaround.png`, `03-expressions.png`.

The illustration pipeline must pass these files into `generateIllustration()`, together with written visual rules, current wardrobe, temporary state, and the previous spread.

---

## How to connect image generation later

Nothing is wired to a paid vendor.

The contract is in `tools/image-generation/`:

- `generateIllustration()`
- `editIllustration()`
- `evaluateIllustration()`

When you approve a vendor, add an adapter under `tools/image-generation/providers/` and point `config.yaml` at it. Keep keys in environment variables, not in git.

Until then, a book can still be reviewed as manuscript + art direction.

---

## Quality gates

From `studio.yaml`. Illustration does not start automatically unless:

- engagement ≥ 85
- story ≥ 85
- character ≥ 90
- values ≥ 90
- zero canon / character violations
- zero unresolved major plot issues
- meaningful protagonist choice
- climax driven by character action
- lesson demonstrated through story

Scores are editorial aids. The Showrunner may override a gate only with a written reason in `book-report.yaml`. Do not chase numbers at the expense of originality.

---

## Scripts

| Script | Purpose |
| --- | --- |
| `scripts/new-book.py` | Next numbered folder + templates |
| `scripts/build-context.py` | Targeted context packet |
| `scripts/validate-book.py` | Gates + manuscript shape |
| `scripts/archive-book.py` | Post-approval canon write |

Python 3, dependency: PyYAML only.

---

## What you still need to supply

Anything marked `[CREATOR INPUT REQUIRED]`, especially:

- who Cove and Mars are (ages, voices, looks, fears, humour)
- family / parent role
- value definitions
- world rules (magic, dragons, danger, supervision)
- fear and content dials
- visual style and first reference images
- writing-style north stars

See the recommended Series Bible prompt at the end of the studio bootstrap report, or start from `bible/series-purpose.md`.
