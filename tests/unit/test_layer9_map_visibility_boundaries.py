from trapspringer.layers.layer9_map.service import MapVisibilityService


def test_concealed_entity_is_not_visible_until_revealed():
    svc = MapVisibilityService()
    svc.instantiate_scene_graph("AREA4", "AREA4_AMBUSH_MAP")
    before = svc.query_visibility({"scene_id": "AREA4", "observer": "PC_TANIS", "target": "AREA4_BAAZ_1"})
    assert before.payload["visible"] is False
    assert before.payload["result"] == "concealed"

    svc.reveal_entity("AREA4", "AREA4_BAAZ_1")
    after = svc.query_visibility({"scene_id": "AREA4", "observer": "PC_TANIS", "target": "AREA4_BAAZ_1"})
    assert after.payload["visible"] is True


def test_hidden_feature_reveal_adds_public_map_connection():
    svc = MapVisibilityService()
    assert "69b->70k" not in svc.public_map_snapshot()["revealed_connections"]
    diff = svc.reveal_for_trigger({"type": "hidden_feature_found", "feature_id": "HID-69B-SECRET-WAY"})
    snapshot = svc.public_map_snapshot()
    assert diff.changes
    assert "69b->70k" in snapshot["revealed_connections"]
    assert any(note["location"] == "69b" for note in snapshot["player_annotations"])


def test_area_entry_reveals_public_map_shell_only():
    svc = MapVisibilityService()
    diff = svc.reveal_for_trigger({"type": "area_entry", "area_id": "44k", "visible_connections": [("44k", "46a", "temple_north"), ("44k", "45", "great_well")]})
    snapshot = svc.public_map_snapshot()
    assert "44k" in snapshot["revealed_areas"]
    assert "44k->46a" in snapshot["revealed_connections"]
    assert "44k->45" in snapshot["revealed_connections"]
    assert diff.changes
