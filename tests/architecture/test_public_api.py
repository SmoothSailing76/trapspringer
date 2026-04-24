from trapspringer.api import create_api


def test_public_api_start_step_and_state():
    api = create_api()
    session = api.start_campaign("dl1", campaign_id="API-TEST")
    assert session.module_id == "DL1_DRAGONS_OF_DESPAIR"
    opening = api.step()
    assert opening.prompt
    round_one = api.step("I attack the nearest hobgoblin")
    assert round_one.narration
    view = api.public_state()
    assert view.campaign_id == "API-TEST"
    assert view.party


def test_public_api_main_path_demo_reaches_epilogue():
    api = create_api()
    outputs = api.run_main_path_demo()
    assert outputs
    assert api.status()["milestone_id"] == "epilogue_complete"
