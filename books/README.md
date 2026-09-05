# Books

Each book gets a numbered directory: `books/001/`, `books/002/`, …

Create the next folder with:

```bash
python3 scripts/new-book.py
python3 scripts/new-book.py --brief path/to/notes.yaml
```

Do not write Book 1 until Alex asks. This folder starts empty of book directories on purpose.

## Directory shape

```text
books/NNN/
  brief.yaml
  context-packet.yaml
  outline-v1.yaml
  outline-final.yaml
  manuscript-v1.md
  editorial-v1.yaml
  manuscript-v2.md
  editorial-v2.yaml
  manuscript-final.md
  proposed-canon.yaml
  book-report.yaml
  art/
    direction.yaml
    visual-state.yaml
    qa.yaml
    references/
    generated/
    approved/
  production/
    layout.json
    final/
```

Additional outline or manuscript versions (`outline-v2.yaml`, `manuscript-v3.md`) are expected when the loop needs them. Never overwrite v1.

## Lifecycle

`draft → outlined → manuscript → manuscript_locked → illustrating → ready_for_review → approved`

Canon updates only at `approved`.
