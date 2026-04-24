# Layer 10 — Audit and Replay Layer

Layer 10 records what happened, why, what was known, and how to reconstruct it later.

## Responsibilities

Event log, snapshots, replay, integrity checks, leak detection, recaps, save compatibility.

## v0.2.1 Event Types

`content_pack_loaded`, `capability_registry_loaded`, `scenario_script_executed`, `api_call`, `save_compatibility_check`, `capability_warning_emitted`.

## Snapshot Metadata

```json
{
  "engine_version": "0.2.1",
  "save_schema_version": "0.2",
  "content_pack_id": "dl1_dragons_of_despair",
  "content_pack_version": "0.2.1",
  "content_pack_hash": "...",
  "rules_capability_snapshot": {
    "initiative_segments": "partial",
    "turn_undead": "implemented"
  }
}
```

## Invariants

Every meaningful change leaves a trace. Replay includes same content-pack/capability context. Public replay filters script-generated hidden facts.
