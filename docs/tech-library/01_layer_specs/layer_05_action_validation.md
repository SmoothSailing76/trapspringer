# Layer 5 — Action Validation Layer

Layer 5 determines whether a declared action is legal here and now.

## Validation Axes

Procedural legality, fictional legality, rules legality, knowledge legality, capability support.

## Statuses

`valid`, `valid_with_assumptions`, `valid_with_capability_warning`, `needs_clarification`, `invalid`, `impossible`, `blocked_by_knowledge`, `blocked_by_procedure`, `requires_human_ruling`, `unsupported_by_engine`.

## Capability Warning

```json
{
  "status": "valid_with_capability_warning",
  "reason_code": "partial_spell_timing_support",
  "capability": {
    "rule_id": "spell_interruption",
    "status": "partial"
  }
}
```

## Scenario Constraint

```yaml
actions:
  strike_khisanth_with_staff:
    requires:
      - actor_has_item: blue_crystal_staff
      - target: khisanth
      - scene: DL1_AREA_70K
```

## Invariants

No action reaches resolution without validation. Hidden information cannot be exploited. Unsupported rules must not silently approximate.
