from trapspringer.content_packs import ContentPackService


def test_dl1_content_pack_loads_event_scene():
    service = ContentPackService()
    manifest = service.get("dl1_dragons_of_despair")
    assert manifest.module_id == "DL1_DRAGONS_OF_DESPAIR"
    assert manifest.entry_scene_id == "DL1_EVENT_1_AMBUSH"
    scene = service.load_json_resource("dl1_dragons_of_despair", "event_1_scene")
    assert scene["scene_id"] == "DL1_EVENT_1_AMBUSH"


def test_content_pack_lists_resources():
    service = ContentPackService()
    resources = service.list_resources("dl1_dragons_of_despair")
    ids = {r.resource_id for r in resources}
    assert "dl1_main_path_registry" in ids
    assert "rules_capabilities" in ids
