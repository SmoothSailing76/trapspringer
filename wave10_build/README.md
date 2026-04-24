# Trapspringer

Trapspringer is an AD&D 1st Edition / DL1 *Dragons of Despair* tabletop simulator prototype.

This v0.2 Complete build provides a playable canonical DL1 main path from Event 1 through the Epilogue, with save/load, named checkpoints, audit logging, and deterministic replay verification for the main path.

## Quick start

```bash
python -S -m trapspringer.adapters.cli.main --campaign dl1 --demo-main-path --status --no-recap
```

## Useful commands

Run the complete DL1 main-path demo:

```bash
python -S -m trapspringer.adapters.cli.main --campaign dl1 --demo-main-path
```

Run with compact output and status:

```bash
python -S -m trapspringer.adapters.cli.main --campaign dl1 --demo-main-path --compact --status --no-recap
```

Save a run:

```bash
python -S -m trapspringer.adapters.cli.main --campaign dl1 --demo-main-path --save --save-dir ./saves --save-label main_path_complete --no-recap
```

List saves:

```bash
python -S -m trapspringer.adapters.cli.main --list-saves --save-dir ./saves
```

Load and inspect a save:

```bash
python -S -m trapspringer.adapters.cli.main --load-save <save_id_or_path> --save-dir ./saves --show-party --show-log
```

Verify release health:

```bash
python -S tools/verify_release.py
python -S tools/verify_replay_spine.py
```

## Current scope

Implemented for v0.2 Complete:

- Event 1 ambush
- Goldmoon/Riverwind join path
- Xak Tsaroth main-path scenes
- Temple of Mishakal
- staff recharge
- descent spine
- lower-city route discovery
- dragon lair finale
- Disks recovery
- Crystal Staff shatter
- collapse escape
- Epilogue / Medallion of Faith
- named checkpoints and save bundles
- deterministic replay spine verification

See `KNOWN_LIMITATIONS.md` and `RULES_COVERAGE.md` for current limits.

## Project structure

- `trapspringer/engine` — orchestrator and runtime
- `trapspringer/layers` — Layers 1–10
- `trapspringer/data` — DL1 scenes, maps, manifests, pregens
- `trapspringer/adapters/cli` — command-line runner
- `tools` — release/replay verification helpers
- `trapspringer/tests` — unit/integration/scenario/replay checks

## Version

Current version: `0.2.0` main-path-complete prototype.
