# Layer Enforcement

Layers are enforced by orchestrator call order, service interfaces, centralized state commits, knowledge filtering, authority queries, audit checks, and regression tests.

## Strongest Rules

- Only Layer 3 commits mutable campaign state.
- All player-facing information passes through Layer 2.
- Rules/canon queries go through Layer 1.
- All meaningful events are logged by Layer 10.
- Cross-layer access uses `service.py`.

State is what happened. Layers are how things happen. RuntimeSession connects them.
