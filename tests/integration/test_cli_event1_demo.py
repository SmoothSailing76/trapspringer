from trapspringer.adapters.cli.session_runner import run_event1_demo


def test_cli_event1_demo_runs():
    demo = run_event1_demo("I attack the nearest hobgoblin")
    assert demo.opening.narration
    assert demo.round_result is not None
    assert demo.round_result.narration
    assert demo.recap is not None
