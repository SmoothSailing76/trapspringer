from trapspringer.adapters.test_harness.regression_suite import run_wave11_regression_suite


def test_wave11_regression_suite_runs():
    result = run_wave11_regression_suite()
    assert result.status in {"ok", "warning"}
    scenario_names = {scenario.name for scenario in result.scenarios}
    assert "event1_round" in scenario_names
    assert "wave6_story_path" in scenario_names
    assert "wave9_party_simulation" in scenario_names
