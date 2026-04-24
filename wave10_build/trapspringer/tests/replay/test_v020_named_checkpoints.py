from trapspringer.adapters.cli.session_runner import run_v020_main_path_demo

EXPECTED = [
    "start_of_event_1", "after_event_1", "goldmoon_joined", "arrival_xak_tsaroth", "after_44f",
    "after_44k_surface", "temple_mishakal", "staff_recharged", "descent_started", "lower_city",
    "secret_route_known", "before_70k", "staff_shattered", "collapse_escape", "epilogue_complete",
]


def test_v020_named_checkpoints_exist():
    demo = run_v020_main_path_demo()
    checkpoints = demo.orchestrator.layer10.checkpoint_ids()
    for name in EXPECTED:
        assert name in checkpoints
        snap = demo.orchestrator.layer10.get_snapshot(name)
        assert snap["save_schema_version"] == "0.2"
        assert snap["engine_version"] == "0.2.0"
        assert snap["state_hash"]
