from trapspringer.layers.layer9_map.service import MapVisibilityService

def test_map_service_smoke():
    svc = MapVisibilityService()
    result = svc.query_visibility({})
    assert result.status == "ok"
