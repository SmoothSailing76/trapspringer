# DL1 Structured Keyed-Room and Encounter Data

Generated for Trapspringer v1.x full DL1 content coverage.

## Contents

- `dl1_keyed_areas_complete.json` — consolidated keyed areas from wilderness, Xak Tsaroth surface, Temple/descent, and cavern city.
- `wilderness_structured.json` — areas 1–43.
- `xak_surface_structured.json` — areas 44a–44k.
- `temple_descent_structured.json` — areas 45–52.
- `cavern_city_structured.json` — areas 53–70k.
- `dl1_timed_events_structured.json` — Events 1–7.
- `dl1_random_encounters_structured.json` — random encounter sections and tables.
- `dl1_monsters_npcs_structured.json` — monster/NPC sections and extracted stat tables.
- `dl1_treasure_items_structured.json` — treasure/item sections.
- `dl1_encounter_index.json` — areas with extracted creature/NPC stat rows.
- `dl1_treasure_index.json` — areas with treasure/item references.
- `dl1_hidden_facts_index.json` — hidden/DM-private facts requiring Layer 2 reveal control.
- `dl1_transition_candidates.json` — extracted area references plus curated high-value transitions.
- `dl1_area_summary.csv` — compact spreadsheet-style summary.
- `dl1_source_asset_provenance.json` — uploaded map/source asset hashes.
- `dl1_structured_data_validation_report.json` — generation counts and review notes.

## Counts

```json
{
  "keyed_area_entries": 147,
  "events": 7,
  "random_encounter_sections": 36,
  "monster_npc_sections": 25,
  "treasure_item_sections": 25,
  "encounter_area_records": 55,
  "treasure_records": 43,
  "hidden_fact_records": 33,
  "transition_candidate_records": 37,
  "source_assets": 8
}
```

## Notes

This is a data-completion pass, not a replacement for source authority. The `description` fields preserve the source text, while tables, hidden facts, treasures, rolls, and occupants are extracted for engine indexing.

Hidden facts must continue to route through Layer 2 before public narration. Area graph candidates should be reconciled with map-derived geometry in Layer 9.
