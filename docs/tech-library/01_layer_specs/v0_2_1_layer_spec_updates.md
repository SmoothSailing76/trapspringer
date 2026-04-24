# v0.2.1 Layer Spec Updates

v0.2.1 adds four cross-cutting architectural systems:

1. Content-pack architecture.
2. Machine-readable rules capability registry.
3. Scenario scripting DSL.
4. Stable public API facade.

## Impact Summary

- Layer 1: content-pack source registration and capability-aware authority.
- Layer 2: content-pack hidden facts and scenario reveal effects.
- Layer 3: content-pack/version metadata, current milestone, script state.
- Layer 4: scenario hook timing and milestone validation.
- Layer 5: capability-aware validation and unsupported-rule statuses.
- Layer 6: scenario DSL executor.
- Layer 7: scripted narration and capability warnings.
- Layer 8: scenario tags and rule uncertainty reactions.
- Layer 9: content-pack maps and scenario reveals.
- Layer 10: content-pack hashes, capability snapshots, script/API audit events.

## Cross-Layer Invariants

Content-pack state appears in Layers 1, 3, 9, and 10. Rules capability informs Layers 5 and 6. Scenario scripts route effects through owning layers. API output is filtered by Layer 2.
