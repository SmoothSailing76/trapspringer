# Layer 3 — Session State Layer

Layer 3 stores mutable campaign state: what currently exists in play. Services/layers are behavior; Layer 3 is state.

## Responsibilities

- Campaign, time, party, character, scene, encounter, module, resource state.
- State mutation commit.
- Module flags and current milestone.
- Engine/content-pack/save metadata.
- Scenario script execution state.
- State diffs.

## State Metadata

```json
{
  "engine_version": "0.2.1",
  "save_schema_version": "0.2",
  "active_content_pack_id": "dl1_dragons_of_despair",
  "active_content_pack_version": "0.2.1",
  "current_milestone_id": "temple_mishakal",
  "rules_capability_snapshot_id": "CAP-SNAP-001"
}
```

## Scenario Script State

```json
{
  "DL1_AREA_46B.on_enter.mishakal_audience": {
    "fired": true,
    "turn": 144,
    "result": "staff_recharged"
  }
}
```

## Invariants

Only Layer 3 commits mutable runtime state. Save files include engine, schema, and content-pack versions. Current milestone is explicit.
