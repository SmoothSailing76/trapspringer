# Layer 6 — Resolution Engine Layer

Layer 6 turns validated actions into actual outcomes: mutations, knowledge effects, map effects, resource changes, follow-up checks, and public/private outcomes.

## Resolution Families

Movement, exploration, combat, spells, items, detection, hazards, social, morale/reaction, travel, rest, escape, module scripts.

## Scenario DSL Executor Effects

`set_flag`, `clear_flag`, `reveal_fact`, `move_actor`, `add_item`, `remove_item`, `damage_actor`, `heal_actor`, `create_checkpoint`, `trigger_scene`, `start_escape_mode`, `run_named_script`, `emit_narration_block`.

## Example

```yaml
on_resolution:
  - if: staff_hits_khisanth
    then:
      - set_flag: staff_shattered
      - set_flag: khisanth_defeated
      - reveal_fact: disks_recovered
      - create_checkpoint: staff_shattered
      - start_escape_mode: collapse_escape
```

## Invariants

Resolution only processes validated actions. Scripts propose effects; Layer 3 commits state. Knowledge effects route through Layer 2. Map effects route through Layer 9.
