# Layer 1 — Canon and Authority Layer

Layer 1 is the authority kernel. It selects controlling sources, classifies authority domains, resolves precedence, detects conflicts, and returns auditable authority traces. It does not narrate, resolve actions, mutate state, or reveal hidden content.

## Responsibilities

- Source registry.
- Domain classification.
- Precedence resolution.
- Conflict detection.
- Ruling escalation.
- Authority trace emission.
- Content-pack source registration.
- Rules capability lookup and warning generation.

## Source Stack

1. Simulator Constitution.
2. Active Content Pack Manifest.
3. Adventure Module Canon.
4. PHB / DMG / MM by scope.
5. Rules Capability Registry.
6. House Policy.
7. Session Ruling Ledger.
8. Inference.

## Domains

`module_content`, `module_event_timing`, `module_geography`, `module_npc_intent`, `module_treasure`, `core_player_rules`, `combat_procedure`, `monster_resolution`, `world_specific_rules`, `knowledge_access`, `table_conduct`, `adjudication`, `continuity`.

## v0.2.1 Additions

Content-pack registration:

```json
{
  "content_pack_id": "dl1_dragons_of_despair",
  "version": "0.2.1",
  "system": "ADND_1E",
  "rules_required": ["melee_combat", "saving_throws", "dragon_breath"]
}
```

Capability-aware authority answer:

```json
{
  "status": "binding",
  "answer": "Initiative is supported with simplified order; segment timing is partial.",
  "capability": {
    "rule_id": "initiative_segments",
    "status": "partial",
    "warning": "Segment-level edge cases may require a ruling."
  }
}
```

## Invariants

No binding answer without authority trace. No unsupported rule treated as implemented. DL1 overrides beat generic assumptions. Rulings must be explicit and logged.
