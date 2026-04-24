from trapspringer.engine.orchestrator import Orchestrator
from trapspringer.layers.layer4_procedure.open_ended import classify_open_ended_intent, open_ended_policy_response


def test_v050_intent_classifier_supported_cases():
    assert classify_open_ended_intent("We retreat from the dungeon").intent_type == "retreat"
    assert classify_open_ended_intent("Split the party and scout ahead").intent_type == "split_party"
    assert classify_open_ended_intent("Take a hobgoblin prisoner").intent_type == "take_prisoner"
    assert classify_open_ended_intent("Interrogate the prisoner").intent_type == "interrogate_prisoner"
    assert classify_open_ended_intent("Drop the staff into the river").intent_type == "key_item_risk"
    assert classify_open_ended_intent("Search for another route").intent_type == "search_alternate_route"
    assert classify_open_ended_intent("Camp and set watches").intent_type == "rest_or_delay"


def test_v050_unknown_action_requires_ruling():
    intent = classify_open_ended_intent("Build a siege engine from the wagon axles")
    policy = open_ended_policy_response(intent)
    assert intent.requires_ruling is True
    assert policy["status"] == "requires_human_ruling"


def test_v050_open_ended_resolutions_mutate_state():
    orch = Orchestrator()
    session = orch.start_campaign("TEST-V050")
    orch.step(session)
    result = orch.handle_open_ended_action("We retreat and regroup")
    state = orch.layer3.read_state()
    assert "withdraws" in (result.narration or "") or "retreat" in (result.narration or "").lower()
    assert state["module"].world_flags["party_retreating"] is True
    assert "v050_retreat" in orch.layer10.checkpoint_ids()


def test_v050_key_item_risk_is_not_silent_loss():
    orch = Orchestrator()
    session = orch.start_campaign("TEST-V050-STAFF")
    orch.step(session)
    orch.handle_open_ended_action("Goldmoon throws away the blue crystal staff")
    state = orch.layer3.read_state()
    assert state["module"].world_flags["key_item_risk_pending"] is True
    assert state["module"].world_flags["key_item_risk_item"] == "blue_crystal_staff"
    assert state["module"].world_flags["human_ruling_required"] is False  # key-item risk has a specific pending state, not a blind mutation


def test_v050_demo_runs():
    orch = Orchestrator()
    session = orch.start_campaign("TEST-V050-DEMO")
    outputs = orch.run_v050_open_ended_demo(session)
    assert len(outputs) >= 6
    state = orch.layer3.read_state()
    assert state["module"].world_flags["party_split_active"] is True
    assert state["module"].world_flags["key_item_risk_pending"] is True
    assert state["module"].world_flags["human_ruling_required"] is True
