from trapspringer.layers.layer4_procedure.transitions import load_main_path_registry


def test_v020_main_path_registry_loads():
    registry = load_main_path_registry()
    assert "start_of_event_1" in registry
    assert "epilogue_complete" in registry
    for milestone in registry.values():
        assert milestone.id
        assert milestone.label
        for nxt in milestone.next:
            assert nxt in registry


def test_v020_main_path_order_reaches_epilogue():
    registry = load_main_path_registry()
    current = "start_of_event_1"
    seen = {current}
    while registry[current].next:
        current = registry[current].next[0]
        assert current not in seen
        seen.add(current)
    assert current == "epilogue_complete"
