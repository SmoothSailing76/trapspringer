"""Tests for the save-bundle migration framework.

Future format bumps register migrators in persistence_service._MIGRATIONS.
These tests cover the framework itself so it works the day it's needed.
"""
import json
from pathlib import Path

import pytest

from trapspringer.services import persistence_service
from trapspringer.services.persistence_service import (
    SAVE_SCHEMA_VERSION,
    SaveLoadError,
    SessionPersistenceService,
    _migrate_bundle,
)


def _minimal_bundle(version: str) -> dict:
    return {
        "save_schema_version": version,
        "state": {},
        "events": [],
    }


def test_current_version_passes_through_unchanged():
    bundle = _minimal_bundle(SAVE_SCHEMA_VERSION)
    assert _migrate_bundle(bundle) is bundle


def test_unknown_version_raises():
    bundle = _minimal_bundle("0.1")
    with pytest.raises(SaveLoadError, match="no migration registered"):
        _migrate_bundle(bundle)


def test_registered_migrator_advances_version(monkeypatch):
    def upgrade_0_1(b: dict) -> dict:
        b = dict(b)
        b["save_schema_version"] = SAVE_SCHEMA_VERSION
        b["migrated_from"] = "0.1"
        return b

    monkeypatch.setitem(persistence_service._MIGRATIONS, "0.1", upgrade_0_1)
    bundle = _minimal_bundle("0.1")
    out = _migrate_bundle(bundle)
    assert out["save_schema_version"] == SAVE_SCHEMA_VERSION
    assert out["migrated_from"] == "0.1"


def test_migrator_that_doesnt_advance_raises(monkeypatch):
    monkeypatch.setitem(persistence_service._MIGRATIONS, "0.1", lambda b: b)
    with pytest.raises(SaveLoadError, match="did not advance"):
        _migrate_bundle(_minimal_bundle("0.1"))


def test_load_bundle_runs_migration(tmp_path: Path, monkeypatch):
    def upgrade_old(b: dict) -> dict:
        b = dict(b)
        b["save_schema_version"] = SAVE_SCHEMA_VERSION
        b["upgraded"] = True
        return b

    monkeypatch.setitem(persistence_service._MIGRATIONS, "0.0", upgrade_old)
    store = SessionPersistenceService(tmp_path)
    save_id = "legacy"
    path = tmp_path / f"{save_id}.json"
    path.write_text(json.dumps({
        "save_schema_version": "0.0",
        "state": {"campaign": {}},
        "events": [],
    }))
    out = store.load_bundle(save_id)
    assert out["save_schema_version"] == SAVE_SCHEMA_VERSION
    assert out["upgraded"] is True
