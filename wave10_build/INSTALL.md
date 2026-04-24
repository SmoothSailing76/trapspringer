# Installation

Trapspringer v0.2 Complete is a dependency-light Python package. It can be run directly from an unpacked archive.

## Requirements

- Python 3.11+
- No third-party runtime dependencies are required for the CLI demos.

## Run without installing

From the archive root:

```bash
python -S -m trapspringer.adapters.cli.main --campaign dl1 --demo-main-path --no-recap
```

## Save/load smoke test

```bash
python -S -m trapspringer.adapters.cli.main --campaign dl1 --demo-main-path --save --save-dir ./saves --save-label complete_main_path --no-recap
python -S -m trapspringer.adapters.cli.main --list-saves --save-dir ./saves
```

## Release verification

```bash
python -S tools/verify_release.py
python -S tools/verify_replay_spine.py
```

## Notes

The `-S` flag is used in examples to avoid importing unrelated site packages in constrained environments. It is not required in a normal virtual environment.
