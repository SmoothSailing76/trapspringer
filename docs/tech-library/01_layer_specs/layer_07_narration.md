# Layer 7 — Narration Layer

Layer 7 renders DM communication: fiction, prompts, rules notes, NPC dialogue, private whispers, map update language, and recaps.

## Channels

Fictional narration, procedural prompt, rules clarification, table meta guidance, private whisper, recap.

## v0.2.1 Additions

- Content-pack tone/style metadata.
- Scripted narration blocks.
- Capability warning phrasing.
- API-safe narration bundles.

## Tone Metadata

```json
{
  "xak_tsaroth": "ancient_ominous",
  "mishakal_temple": "sacred_wondrous",
  "collapse_escape": "urgent_heroic"
}
```

## Invariants

Narration may not create new truth or leak blocked facts. Scripted narration still passes Layer 2 filtering.
