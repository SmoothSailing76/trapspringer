from pathlib import Path

from trapspringer.layers.layer3_state.service import StateService
from trapspringer.scenario_dsl import ScenarioScriptExecutor, load_scenario_script


def test_mishakal_scenario_script_sets_flags_when_staff_present():
    state_service = StateService()
    state_service.create_initial_state({"campaign_id": "DSL-TEST"})
    state = state_service.read_state()
    state["module"].world_flags["staff_in_party_possession"] = True
    script = load_scenario_script(Path("trapspringer/data/scenario_scripts/dl1_area_46b_mishakal.json"))
    result = ScenarioScriptExecutor().execute_on_enter(script, state)
    assert result.ok
    assert state["module"].world_flags["mishakal_audience_complete"] is True
    assert state["module"].world_flags["staff_recharged"] is True
    assert "staff_recharged" in result.checkpoints
