from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any

from trapspringer.adapters.cli.session_runner import (
    run_event1_demo,
    run_v020_main_path_demo,
    run_v030_spatial_demo,
    run_v040_rules_demo,
    run_v050_open_ended_demo,
    run_v060_content_dsl_demo,
    run_v070_map_visibility_demo,
    run_v080_party_maturity_demo,
)
from trapspringer.services.quality_service import QualityGateService

EXPECTED_MAIN_PATH_CHECKPOINTS = [
    "start_of_event_1", "after_event_1", "goldmoon_joined", "arrival_xak_tsaroth", "after_44f",
    "after_44k_surface", "temple_mishakal", "staff_recharged", "descent_started", "lower_city",
    "secret_route_known", "before_70k", "staff_shattered", "collapse_escape", "epilogue_complete",
]

@dataclass(slots=True)
class HardeningCheck:
    name: str
    status: str
    detail: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(slots=True)
class HardeningReport:
    status: str
    checks: list[HardeningCheck]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "summary": self.summary, "checks": [c.to_dict() for c in self.checks]}


def _check(name: str, ok: bool, detail: str, **data: Any) -> HardeningCheck:
    return HardeningCheck(name=name, status="ok" if ok else "fail", detail=detail, data=data)


class V090HardeningService:
    """v0.9 hardening and release-confidence checks.

    This service intentionally runs cross-version smoke paths through the public
    demo/session-runner interfaces. It is a lightweight release gate rather than
    a replacement for pytest.
    """

    def run(self) -> HardeningReport:
        checks: list[HardeningCheck] = []

        event1 = run_event1_demo(user_input="I attack the nearest hobgoblin")
        event1_state = event1.state or {}
        toede = event1_state.get("characters", {}).get("NPC_TOEDE")
        checks.append(_check("event1_round", getattr(toede, "status", None) == "fled", "Event 1 executes and Toede flees.", toede_status=getattr(toede, "status", None)))

        main_path = run_v020_main_path_demo()
        flags = getattr((main_path.state or {}).get("module"), "world_flags", {}) if main_path.state else {}
        checks.append(_check("main_path_epilogue", bool(flags.get("epilogue_complete")), "DL1 main path reaches epilogue.", flags={k: flags.get(k) for k in ("disks_recovered", "staff_shattered", "medallion_created", "epilogue_complete")}))

        checkpoints = main_path.orchestrator.layer10.checkpoint_ids() if main_path.orchestrator else {}
        missing = [m for m in EXPECTED_MAIN_PATH_CHECKPOINTS if m not in checkpoints]
        checks.append(_check("checkpoint_spine", not missing, "All named main-path checkpoints exist.", missing=missing, count=len(checkpoints)))

        bad_snapshots = []
        if main_path.orchestrator:
            for milestone in EXPECTED_MAIN_PATH_CHECKPOINTS:
                snap = main_path.orchestrator.layer10.get_snapshot(milestone)
                if not snap or not snap.get("state_hash") or snap.get("save_schema_version") != "0.2":
                    bad_snapshots.append(milestone)
        checks.append(_check("snapshot_metadata", not bad_snapshots, "Named checkpoints include hashes and save schema metadata.", bad=bad_snapshots))

        quality = QualityGateService().run(main_path.orchestrator) if main_path.orchestrator else None
        checks.append(_check("quality_gates", quality is not None and quality.status in {"ok", "warning"}, "Quality gates run against main path without hard failure.", quality=quality.to_dict() if quality else {}))

        spatial = run_v030_spatial_demo()
        checks.append(_check("spatial_assets", bool(spatial.validation.get("ok")), "v0.3 spatial assets validate.", validation=spatial.validation))

        rules = run_v040_rules_demo()
        checks.append(_check("rules_facade", "Capability summary" in rules.output and bool(rules.summary), "v0.4 rules facade demo executes."))

        opened = run_v050_open_ended_demo()
        checks.append(_check("open_ended_branches", bool(opened.outputs), "v0.5 open-ended handling returns branch outputs.", output_count=len(opened.outputs)))

        dsl = run_v060_content_dsl_demo()
        checks.append(_check("content_dsl", bool(dsl.report.get("ok")), "v0.6 content-pack and scenario DSL validate.", report=dsl.report))

        mapvis = run_v070_map_visibility_demo()
        checks.append(_check("map_visibility", bool(mapvis.report.get("revealed_trace", {}).get("visible")), "v0.7 visibility reveal flow succeeds."))

        party = run_v080_party_maturity_demo()
        checks.append(_check("party_simulation", bool(party.report.get("caller")) and len(party.report.get("mapper_notes", [])) >= 3, "v0.8 party simulation maturity state is present.", report=party.report))

        status = "ok" if all(c.status == "ok" for c in checks) else "fail"
        summary = f"v0.9 hardening gate: {status.upper()} ({sum(c.status == 'ok' for c in checks)}/{len(checks)} checks passed)."
        return HardeningReport(status=status, checks=checks, summary=summary)
