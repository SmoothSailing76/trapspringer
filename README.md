# Trapspringer

A deterministic AD&D 1st Edition session simulator for the DL1 *Dragons of Despair* module.

## What it does

Trapspringer runs a fully scripted playthrough of the DL1 campaign — from the Event 1 road ambush through the Khisanth dragon lair finale — using authentic 1st Edition rules. Every dice roll, attack matrix lookup, saving throw, and spell resolution is auditable and replayable.

## Architecture

Ten service layers, each with a strict boundary:

| Layer | Responsibility |
|---|---|
| 1 Authority | Canon rules enforcement |
| 2 Knowledge | Information discovery and visibility |
| 3 State | Session and world-state persistence |
| 4 Procedure | Turn/combat flow control |
| 5 Validation | Action legality checking |
| 6 Resolution | Outcome application (combat, spells, items) |
| 7 Narration | Story text generation |
| 8 Party | NPC decision-making and party simulation |
| 9 Map | Line-of-sight and spatial queries |
| 10 Audit | Event logging and deterministic replay |

External consumers import from `api.py` only — never from layer internals.

## Rules coverage

Key AD&D 1e mechanics implemented (`rules/adnd1e_v04.py`):

- **Attacks**: THAC0-based melee and missile, range bands, cover modifiers
- **Saving throws**: All five categories (death, wand, paralysis, breath, spell) for all class groups
- **Spells**: magic missile, sleep, web, bless, protection from evil, hold person, fireball, lightning bolt, cure light/serious wounds, dispel magic, darkness
- **Dragon fear & breath**: save vs spell for fear (flee on fail); breath = dragon's current HP, save vs breath for half (MM canonical)
- **Turn undead**: compact matrix for skeleton through wight
- **Morale & reaction**: 2d6 morale, 2d10 reaction bands
- **Initiative**: 1d6 per side with DEX-score tiebreaker
- **Surprise**: d6 with segments-lost metadata
- **XP & training**: PHB cumulative XP thresholds by class; 1500 gp/level training cost (DMG)
- **Encumbrance**: GP-weight movement reduction bands
- **Item saves**: material/attack-form table (acid, fire, crushing, lightning)

See `data/manifests/rules_capabilities.json` for the full capability registry.

## Quickstart

```bash
pip install -e .
python -m trapspringer.adapters.cli.main
```

## Running tests

```bash
pytest
```

## Module coverage

The DL1 main path spine is fully implemented (21 world flags, 15 named checkpoints). Optional branches and hireling/henchman rules are not yet implemented.

## Docs

Full layer specs and implementation plans are in `docs/tech-library/`.
