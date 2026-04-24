# Save, Load, and Replay

## Save a complete main-path run

```bash
python -S -m trapspringer.adapters.cli.main --campaign dl1 --demo-main-path --save --save-dir ./saves --save-label main_path_complete --no-recap
```

## List saves

```bash
python -S -m trapspringer.adapters.cli.main --list-saves --save-dir ./saves
```

## Load a save

```bash
python -S -m trapspringer.adapters.cli.main --load-save <save_id_or_path> --save-dir ./saves --show-party --show-log
```

## Verify replay spine

```bash
python -S tools/verify_replay_spine.py
```

The v0.2 complete build creates named checkpoints for every main-path milestone. Save bundles use schema version `0.2`.
