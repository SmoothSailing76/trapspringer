from trapspringer.rules.capabilities import default_rules_capability_registry
from trapspringer.layers.layer1_authority.service import AuthorityService


def test_rules_capabilities_registry_summary():
    registry = default_rules_capability_registry()
    assert registry.status("dl1_main_path") == "implemented"
    assert registry.status("psionics") == "unsupported"
    assert registry.summary()["implemented"] >= 1


def test_authority_service_exposes_capabilities():
    service = AuthorityService()
    assert service.capability_status("melee_attacks") == "implemented"
    cap = service.require_capability("spell_casting")
    assert cap.status == "partial"
