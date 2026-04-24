from trapspringer.layers.layer9_map.service import MapVisibilityService


def test_v030_spatial_registry_loads():
    layer9 = MapVisibilityService()
    summary = layer9.dl1_spatial_summary()
    assert summary["registry_id"] == "DL1_FULL_SPATIAL_REGISTRY_V030"
    assert summary["xak_levels"] == [1, 2, 3, 4]
    assert "overland_encounter_zones" in summary["wilderness_sources"]


def test_v030_spatial_assets_present():
    layer9 = MapVisibilityService()
    report = layer9.validate_dl1_spatial_assets()
    assert report["ok"], report.get("missing")


def test_level4_area_index_contains_finale():
    layer9 = MapVisibilityService()
    level4 = layer9.load_xak_tsaroth_level(4)
    area_ids = {area["area_id"] for area in level4.get("encounter_areas", [])}
    assert "70k" in area_ids
    assert "69b" in area_ids
