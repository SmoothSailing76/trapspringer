# Rules Coverage

This release focuses on the DL1 main path rather than total AD&D 1e completeness.

## Implemented for the main path

- Campaign startup and Event 1 ambush flow
- Basic melee and missile attack handling
- Compact attack/damage helpers
- Initiative helper support
- Saving throw helper support where used by the main path
- Basic spell handling for main-path spells: magic missile, sleep, web, cure light wounds
- Staff recharge and artifact-scripted finale handling
- Dragon breath and collapse finale scripting at main-path level
- Main-path hidden information and public/private audit separation
- Save/load snapshots and deterministic checkpoint verification

## Partially implemented

- AD&D 1e combat timing and initiative segments
- Morale and reaction behavior
- Encumbrance and movement nuance
- Treasure/XP helpers
- Monster special abilities beyond the DL1 main-path needs
- Secret and trap detection beyond main-path triggers

## Not complete in this version

- Full AD&D 1e spell list
- Full Monster Manual special-case coverage
- Complete hireling/henchman systems
- Training, downtime, and full XP economy
- Item saving throws and all DMG edge cases
- Complete optional DL1 wilderness branching

## Source trace status

The simulator is source-structured around PHB, DMG, Monster Manual, and DL1 reference material, but many rule procedures remain compact MVP implementations. Those shortcuts are documented here and in `KNOWN_LIMITATIONS.md`.
