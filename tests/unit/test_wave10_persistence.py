from pathlib import Path

from trapspringer.adapters.cli.product_views import render_party_panel, render_replay_view, render_save_list
from trapspringer.adapters.cli.session_runner import run_event1_demo
from trapspringer.services.persistence_service import SessionPersistenceService


def test_save_list_load_and_export(tmp_path: Path):
    demo = run_event1_demo(save_dir=tmp_path, save_label="test_save")
    assert demo.save_record is not None
    store = SessionPersistenceService(tmp_path)
    rows = store.list_saves()
    assert len(rows) == 1
    assert rows[0]["label"] == "test_save"
    bundle = store.load_bundle(rows[0]["save_id"])
    assert bundle["format"] == "trapspringer.session.v2"
    assert bundle["events"]
    out = store.export_session(rows[0]["save_id"], tmp_path / "exported.json")
    assert out.exists()


def test_product_views_render_from_bundle(tmp_path: Path):
    demo = run_event1_demo(save_dir=tmp_path)
    store = SessionPersistenceService(tmp_path)
    row = store.list_saves()[0]
    bundle = store.load_bundle(row["save_id"])
    assert "Saves:" in render_save_list([row])
    assert "Party" in render_party_panel(bundle["state"])
    assert "Replay Events" in render_replay_view(bundle["events"], public_only=True)
