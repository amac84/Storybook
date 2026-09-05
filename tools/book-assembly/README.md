# Book assembly

Turns a locked manuscript + approved images into a reviewable / printable package.

Nothing here generates vendor lock-in. A later adapter may emit PDF, EPUB, or a simple HTML proof.

## Expected inputs

- `books/NNN/manuscript-final.md`
- `books/NNN/art/direction.yaml`
- `books/NNN/art/approved/spread-NN.png` when images exist
- `books/NNN/production/layout.json`

## layout.json

See `layout.schema.yaml`. Each spread maps text, image, and text-safe box.

## Status

Not implemented beyond the schema. Assembly waits until there is at least one locked manuscript worth proving.

Do not invent a design system that fights `bible/visual-style.md`.
