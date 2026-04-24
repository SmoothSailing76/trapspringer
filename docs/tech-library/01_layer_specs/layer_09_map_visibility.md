# Layer 9 — Map and Visibility Layer

Layer 9 manages true map, public map, scene graph, line of sight, light, audibility, hidden features, tactical positioning, and map diffs.

## Map Separation

TrueMap contains all geometry. PublicMap contains only explored or revealed geometry.

## v0.2.1 Additions

- Content-pack map registry.
- Scenario-driven map reveals.
- Declarative hidden-feature metadata.
- API-safe public map view.

## Map Registry

```json
{
  "content_pack_id": "dl1_dragons_of_despair",
  "maps": {
    "true_map": "maps/dl1_true_map.json",
    "public_seed": "maps/dl1_public_seed.json",
    "scene_templates": "maps/scene_templates/"
  }
}
```

## Invariants

TrueMap and PublicMap remain distinct. Scenario map reveals cannot bypass discovery rules. API public map never exposes true-map-only data.
