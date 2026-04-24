from trapspringer.engine.orchestrator import Orchestrator

def test_orchestrator_smoke():
    orch = Orchestrator()
    session = orch.start_campaign("DL1-CAMPAIGN-001")
    result = orch.step(session)
    assert result.prompt is not None
