# Illustration pipeline

Do not start this pipeline until the manuscript is locked and manuscript-stage gates have passed (or a documented override exists).

## Preconditions

- `manuscript-final.md`
- `art/direction.yaml`
- `art/visual-state.yaml` (may be filled as you go)
- character reference images if they exist
- no vendor SDK added unless Alex approved it

## Per-spread loop

1. Build an `IllustrationRequest` from `tools/image-generation/` using:
   - spread art direction
   - canonical reference images
   - written visual descriptions
   - current wardrobe
   - temporary story state
   - previous relevant illustration
   - negative constraints
   - output requirements (text-safe region, aspect ratio)
2. `generateIllustration()` via the configured provider adapter (none is configured yet).
3. Save to `art/generated/spread-NN-vK.png` (or the adapter’s format). Never overwrite v1.
4. Visual QA against references, direction, previous spreads, and state.
5. `FAIL` → `editIllustration()` or regenerate with QA guidance. Increment version.
6. `PASS` → copy or promote to `art/approved/spread-NN.png` only when the book is ready for review (or earlier if you need a stable continuity reference — still not visual canon for later books).

## Continuity system

Pass images, not just adjectives.

Update `visual-state.yaml` after each spread so later frames know who is wet, what is carried, and which knee is muddy.

Temporary state expires after approval unless promoted.

## If no provider is connected

Stop after art direction. Do not fake illustrations. The book can still be reviewed as a manuscript + storyboard.

## Assembly

When images exist, `tools/book-assembly/` builds `production/layout.json` and, later, a printable/readable final.

## Taste

If Alex says “this picture is exactly right,” record a generalizable note in `bible/creator-taste.md` and keep that image in references if it locks a look.
