from trapspringer.engine.orchestrator import Orchestrator
from trapspringer.layers.layer8_party.service import PartySimulationService


def test_wave9_distinct_scene_discussion_and_dissent():
    svc = PartySimulationService()
    svc.initialize_seats("PC_TANIS", ["PC_TANIS", "PC_TASSLEHOFF", "PC_STURM", "PC_CARAMON", "PC_RAISTLIN", "PC_FLINT", "PC_GOLDMOON", "NPC_RIVERWIND"])
    bundle = svc.simulate_discussion({"scene_id": "DL1_AREA_44F", "available_public_information": ["camp_visible", "dragon_shape_visible"]})
    texts = [line.text for line in bundle.discussion]
    assert any("dragon" in t.lower() for t in texts)
    assert any("shields" in t.lower() or "slow" in t.lower() for t in texts)
    assert bundle.proposals
    assert bundle.caller_summary
    assert bundle.dissent
    assert bundle.mapper_notes


def test_wave9_user_action_reaction_preserves_user_agency():
    svc = PartySimulationService()
    svc.initialize_seats("PC_TANIS", ["PC_TANIS", "PC_TASSLEHOFF", "PC_STURM", "PC_CARAMON", "PC_RAISTLIN", "PC_FLINT"])
    bundle = svc.react_to_user_action("I charge the nearest enemy", "DL1_AREA_44K")
    assert bundle.discussion
    assert any("rear" in text.lower() or "cover" in text.lower() or "go in" in text.lower() for text in [*(line.text for line in bundle.discussion), *bundle.dissent])
    # The user action is reacted to, not replaced by a simulated declaration.
    assert "charge" not in (bundle.caller_summary or "").lower() or "caller" in (bundle.caller_summary or "").lower()


def test_wave9_scene_declarations_are_personality_driven():
    svc = PartySimulationService()
    svc.initialize_seats("PC_TANIS", ["PC_TANIS", "PC_TASSLEHOFF", "PC_STURM", "PC_CARAMON", "PC_RAISTLIN", "PC_FLINT"])
    svc.simulate_discussion({"scene_id": "DL1_AREA_44F", "available_public_information": ["camp_visible", "dragon_shape_visible"]})
    declarations = svc.generate_declarations({"scene_id": "DL1_AREA_44F", "mode": "exploration"})
    spoken = "\n".join(d.spoken_text for d in declarations.declarations)
    assert "breathing" in spoken or "Shields" in spoken or "Raistlin" in spoken


def test_wave9_cli_demo_function_runs():
    from trapspringer.adapters.cli.session_runner import run_wave9_party_demo
    demo = run_wave9_party_demo()
    assert len(demo.outputs) == 3
    assert "Party Simulation" not in demo.outputs[0]
    assert "Caller summary" in demo.outputs[0]
