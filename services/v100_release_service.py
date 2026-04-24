from __future__ import annotations

from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any

from trapspringer.adapters.cli.session_runner import (
    run_v020_main_path_demo, run_v030_spatial_demo, run_v040_rules_demo,
    run_v050_open_ended_demo, run_v060_content_dsl_demo, run_v070_map_visibility_demo,
    run_v080_party_maturity_demo, run_v090_hardening_demo,
)
from trapspringer.services.persistence_service import SessionPersistenceService

EXPECTED_VERSION = "1.0.0"
EXPECTED_MAIN_PATH_FLAGS = [
    "event1_started", "event1_resolved", "goldmoon_joined", "staff_in_party_possession",
    "xak_tsaroth_reached", "area_44f_resolved", "khisanth_surface_encounter_resolved",
    "temple_mishakal_reached", "mishakal_audience_complete", "staff_recharged",
    "descent_started", "lower_city_reached", "secret_route_known", "dragon_lair_reached",
    "disks_recovered", "staff_shattered", "khisanth_defeated", "collapse_escape_started",
    "collapse_escaped", "medallion_created", "epilogue_complete",
]
EXPECTED_SPATIAL_FILES = [
    "trapspringer/data/maps/dl1/spatial_registry_v030.json",
    "trapspringer/data/maps/dl1/wilderness/wilderness_spatial_manifest.json",
    "trapspringer/data/maps/dl1/xak_tsaroth/xak_tsaroth_map_stack_manifest.json",
    "trapspringer/data/maps/dl1/xak_tsaroth/xak_tsaroth_transitions.json",
    "trapspringer/data/maps/dl1/xak_tsaroth/levels/level1_true_map.json",
    "trapspringer/data/maps/dl1/xak_tsaroth/levels/level2_true_map.json",
    "trapspringer/data/maps/dl1/xak_tsaroth/levels/level3_true_map.json",
    "trapspringer/data/maps/dl1/xak_tsaroth/levels/level4_true_map.json",
]
EXPECTED_DOCS = ["README.md", "INSTALL.md", "KNOWN_LIMITATIONS.md", "RULES_COVERAGE.md", "MAIN_PATH_WALKTHROUGH.md", "SAVE_LOAD_REPLAY.md", "V1_0_RELEASE.md"]

@dataclass(slots=True)
class ReleaseCheck:
    name: str
    status: str
    detail: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    def to_dict(self) -> dict[str, Any]: return asdict(self)

@dataclass(slots=True)
class V100ReleaseReport:
    status: str
    summary: str
    checks: list[ReleaseCheck]
    def to_dict(self) -> dict[str, Any]: return {"status": self.status, "summary": self.summary, "checks": [c.to_dict() for c in self.checks]}

def _check(name: str, ok: bool, detail: str, **data: Any) -> ReleaseCheck:
    return ReleaseCheck(name=name, status="ok" if ok else "fail", detail=detail, data=data)

class V100ReleaseService:
    """v1.0 release gate for the Trapspringer DL1 simulator."""
    def __init__(self, project_root: str | Path | None = None) -> None:
        self.project_root = Path(project_root) if project_root else Path(__file__).resolve().parents[2]

    def run(self) -> V100ReleaseReport:
        checks: list[ReleaseCheck] = []
        try:
            import trapspringer
            version = getattr(trapspringer, "__version__", "")
        except Exception as exc:
            version = f"error: {exc}"
        checks.append(_check("version_metadata", version == EXPECTED_VERSION, "Package reports version 1.0.0.", version=version))

        main_path = run_v020_main_path_demo()
        state = main_path.state or {}
        module = state.get("module")
        flags = getattr(module, "world_flags", {}) if module else {}
        missing_flags = [flag for flag in EXPECTED_MAIN_PATH_FLAGS if not flags.get(flag)]
        checks.append(_check("dl1_main_path_complete", not missing_flags, "DL1 main path reaches epilogue with expected flags.", missing_flags=missing_flags))

        checkpoints = main_path.orchestrator.layer10.checkpoint_ids() if main_path.orchestrator else {}
        expected_checkpoints = ["start_of_event_1", "after_event_1", "goldmoon_joined", "arrival_xak_tsaroth", "after_44f", "after_44k_surface", "temple_mishakal", "staff_recharged", "descent_started", "lower_city", "secret_route_known", "before_70k", "staff_shattered", "collapse_escape", "epilogue_complete"]
        missing_checkpoints = [cp for cp in expected_checkpoints if cp not in checkpoints]
        checks.append(_check("checkpoint_spine", not missing_checkpoints, "All named main-path checkpoints exist.", missing=missing_checkpoints, count=len(checkpoints)))

        try:
            save_dir = self.project_root / ".v100_verify_saves"
            store = SessionPersistenceService(save_dir)
            rec = store.save_session(type("Session", (), {"context": type("Context", (), {"campaign_id": "V100-SAVE", "module_id": "DL1_DRAGONS_OF_DESPAIR", "active_scene_id": "DL1_EPILOGUE", "current_frame_id": None, "current_snapshot_id": None})()})(), state, main_path.orchestrator.layer10, label="v100_release_gate") if main_path.orchestrator else None
            loaded = store.load_bundle(rec["save_id"]) if rec else None
            ok = bool(loaded and loaded.get("save_schema_version") == "0.2" and (loaded.get("state_hash") or (loaded.get("latest_snapshot") or {}).get("state_hash")))
            detail = "Save bundle writes and reloads with schema/hash metadata."
        except Exception as exc:
            ok = False; loaded = None; detail = f"Save/load failed: {exc}"
        checks.append(_check("save_load_bundle", ok, detail, save_id=(loaded or {}).get("save_id"), schema=(loaded or {}).get("save_schema_version")))

        integrity = main_path.orchestrator.layer10.check_integrity() if main_path.orchestrator else {}
        checks.append(_check("audit_integrity", integrity.get("status") in {"ok", "warning"}, "Audit integrity gate has no hard failure.", integrity=integrity))

        try:
            from trapspringer.public_api.service import TrapspringerAPI
            api = TrapspringerAPI(); handle = api.start_campaign("dl1", campaign_id="V100-API"); view = api.public_state()
            ok = bool(getattr(handle, "campaign_id", None)) and bool(getattr(view, "campaign_id", None))
            detail = "Public API facade can start a campaign and return public state."
        except Exception as exc:
            ok = False; detail = f"Public API failed: {exc}"
        checks.append(_check("public_api_facade", ok, detail))

        hardening = run_v090_hardening_demo()
        checks.append(_check("v090_hardening_gate", hardening.status == "ok", "v0.9 hardening gate still passes.", report=hardening.report))

        spatial = run_v030_spatial_demo()
        missing_spatial_files = [f for f in EXPECTED_SPATIAL_FILES if not (self.project_root / f).exists()]
        checks.append(_check("spatial_assets", bool(spatial.validation.get("ok")) and not missing_spatial_files, "Spatial manifests and map stack validate.", missing_files=missing_spatial_files, validation=spatial.validation))

        rules = run_v040_rules_demo()
        checks.append(_check("rules_facade", "Capability summary" in rules.output and bool(rules.summary), "AD&D rules facade executes and reports capabilities."))
        opened = run_v050_open_ended_demo()
        checks.append(_check("open_ended_fallbacks", bool(opened.outputs), "Open-ended branch/failure fallback demo executes."))
        dsl = run_v060_content_dsl_demo()
        checks.append(_check("content_pack_scenario_dsl", bool(dsl.report.get("ok")), "Content-pack validator and scenario DSL executor pass.", report=dsl.report))
        mapvis = run_v070_map_visibility_demo()
        checks.append(_check("map_visibility", bool(mapvis.report.get("revealed_trace", {}).get("visible")), "Map visibility reveal flow succeeds."))
        party = run_v080_party_maturity_demo()
        checks.append(_check("party_simulation", bool(party.report.get("caller")) and len(party.report.get("mapper_notes", [])) >= 3, "Party simulation maturity state is present."))

        docs_missing = [doc for doc in EXPECTED_DOCS if not (self.project_root / doc).exists()]
        checks.append(_check("release_documentation", not docs_missing, "Release documentation exists.", missing=docs_missing))
        source_assets = self.project_root / "trapspringer/data/source_assets/source_assets_manifest.json"
        checks.append(_check("source_asset_manifest", source_assets.exists(), "Source asset manifest is present for map/source provenance."))

        status = "ok" if all(c.status == "ok" for c in checks) else "fail"
        summary = f"Trapspringer v1.0 release gate: {status.upper()} ({sum(c.status == 'ok' for c in checks)}/{len(checks)} checks passed)."
        return V100ReleaseReport(status=status, summary=summary, checks=checks)
