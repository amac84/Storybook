# Image generation interface

No vendor is connected.

Do not add a paid API, SDK, or MCP image server unless Alex approves it.

This folder defines a provider-agnostic contract so later we can attach an API, MCP server, CLI, or local model without rewriting the studio.

## Functions

```text
generateIllustration(request) -> IllustrationResult
editIllustration(request, source_image, edit_instructions) -> IllustrationResult
evaluateIllustration(image, request, references) -> VisualQAResult
```

`evaluateIllustration` may call the Visual QA agent rather than a model-side scorer.

## Request must support

- `spread`
- `character_reference_images`
- `art_style_reference`
- `previous_spread_reference`
- `location_reference`
- `continuity_state`
- `art_direction`
- `negative_constraints`
- `output_requirements`

See `protocol.py` and `schema.yaml`.

## Consistency rule

Visual consistency is a system. Every generate/edit call should pass references + written visual rules + wardrobe + temporary state + previous frame + direction. Do not rely on prompt wording alone.

## Adding a provider later

1. Get Alex’s approval for the vendor.
2. Implement `Provider` in a new module (`providers/<name>.py`).
3. Point `config.yaml` `provider` at it.
4. Keep requests in the studio schema; translate vendor-specific fields only inside the adapter.
