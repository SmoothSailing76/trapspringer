# Engine Manifest — Modules and Files

## Packages

- `engine/` — orchestrator, runtime, lifecycle, message bus, IDs.
- `layers/layer1_authority/` through `layers/layer10_audit/`.
- `domain/` — enums, errors, messages.
- `schemas/` — shared data models.
- `rules/` — source registry, rule queries, overrides.
- `data/` — content packs, manifests, maps, scenes, actors.
- `services/` — clock, random, hash, serialization, replay support.
- `adapters/cli/` — command-line runner.
- `tests/` — unit, integration, scenario, replay.

## Rule

All cross-layer access goes through `service.py` facades.
