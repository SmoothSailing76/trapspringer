"""Tests for trapspringer.schemas.loaders boundary validators."""
import json
from pathlib import Path

import pytest

from trapspringer.schemas.loaders import (
    ResourceValidationError,
    load_encounter,
    load_module_manifest,
    load_npc,
    load_pregen,
    load_scene,
)


def _write(tmp_path: Path, name: str, payload) -> Path:
    p = tmp_path / name
    p.write_text(json.dumps(payload))
    return p


def test_pregen_rejects_missing_actor_id(tmp_path: Path):
    p = _write(tmp_path, "p.json", {"name": "x", "actor_type": "pc"})
    with pytest.raises(ResourceValidationError, match="actor_id"):
        load_pregen(p)


def test_pregen_accepts_minimal_valid(tmp_path: Path):
    p = _write(tmp_path, "p.json", {"actor_id": "PC_X", "name": "x", "actor_type": "pc"})
    assert load_pregen(p)["actor_id"] == "PC_X"


def test_npc_rejects_array(tmp_path: Path):
    p = tmp_path / "npc.json"
    p.write_text(json.dumps([{"actor_id": "NPC_X"}]))
    with pytest.raises(ResourceValidationError, match="must be a JSON object"):
        load_npc(p)


def test_encounter_requires_max_hp_values_list(tmp_path: Path):
    p = _write(tmp_path, "e.json", {
        "actor_id": "X", "name": "x", "actor_type": "monster", "max_hp_values": []
    })
    with pytest.raises(ResourceValidationError, match="non-empty list"):
        load_encounter(p)


def test_encounter_accepts_valid(tmp_path: Path):
    p = _write(tmp_path, "e.json", {
        "actor_id": "HG", "name": "Hobgoblin", "actor_type": "monster",
        "max_hp_values": [5, 6, 7],
    })
    assert load_encounter(p)["max_hp_values"] == [5, 6, 7]


def test_scene_requires_scene_id_and_type(tmp_path: Path):
    p = _write(tmp_path, "s.json", {"scene_id": "X"})
    with pytest.raises(ResourceValidationError, match="type"):
        load_scene(p)


def test_module_manifest_requires_scene_files_object(tmp_path: Path):
    p = _write(tmp_path, "m.json", {
        "module_id": "M", "start_scene_id": "S", "scene_files": ["wrong"]
    })
    with pytest.raises(ResourceValidationError, match="scene_files must be an object"):
        load_module_manifest(p)


def test_module_manifest_loads_real_dl1_file():
    repo = Path(__file__).resolve().parents[2]
    data = load_module_manifest(repo / "data" / "manifests" / "module_manifest_dl1.json")
    assert data["module_id"] == "DL1_DRAGONS_OF_DESPAIR"
    assert "DL1_EVENT_1_AMBUSH" in data["scene_files"]


def test_invalid_json_reports_path_and_line(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text("{ not json")
    with pytest.raises(ResourceValidationError, match=r"invalid JSON.*line"):
        load_pregen(p)


def test_missing_file_reports_useful_error(tmp_path: Path):
    with pytest.raises(ResourceValidationError, match="file not found"):
        load_pregen(tmp_path / "does_not_exist.json")
