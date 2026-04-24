from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any

from trapspringer.adapters.cli.session_runner import run_event1_demo, run_wave6_story_demo, run_wave9_party_demo
from trapspringer.services.quality_service import QualityGateService


@dataclass(slots=True)
class ScenarioResult:
    name: str
    status: str
    detail: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RegressionSuiteResult:
    status: str
    scenarios: list[ScenarioResult]

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "scenarios": [s.to_dict() for s in self.scenarios]}


def run_wave11_regression_suite() -> RegressionSuiteResult:
    scenarios: list[ScenarioResult] = []
    quality = QualityGateService()

    event1 = run_event1_demo(user_input="I attack the nearest hobgoblin", user_character_id="PC_TANIS")
    event1_report = quality.run(event1.orchestrator)
    state = event1.state or {}
    toede_status = getattr(state.get("characters", {}).get("NPC_TOEDE"), "status", None)
    if toede_status == "fled" and event1_report.status in {"ok", "warning"}:
        scenarios.append(ScenarioResult("event1_round", "ok", "Event 1 round executes; Toede flees; quality gates run.", event1_report.to_dict()))
    else:
        scenarios.append(ScenarioResult("event1_round", "fail", "Event 1 regression failed.", {"toede_status": toede_status, "quality": event1_report.to_dict()}))

    wave6 = run_wave6_story_demo(user_character_id="PC_TANIS")
    wave6_report = quality.run(wave6.orchestrator)
    flags = (wave6.state or {}).get("module").world_flags if wave6.state else {}
    if flags.get("khisanth_surface_seen") and flags.get("wicker_dragon_discovered"):
        scenarios.append(ScenarioResult("wave6_story_path", "ok" if wave6_report.status in {"ok", "warning"} else "fail", "Wave 6 story flags survive regression checks.", {"flags": flags, "quality": wave6_report.to_dict()}))
    else:
        scenarios.append(ScenarioResult("wave6_story_path", "fail", "Wave 6 story flags missing.", {"flags": flags, "quality": wave6_report.to_dict()}))

    wave9 = run_wave9_party_demo(user_character_id="PC_TANIS")
    distinct_lines = sum(1 for output in wave9.outputs for line in output.splitlines() if ":" in line)
    scenarios.append(ScenarioResult("wave9_party_simulation", "ok" if distinct_lines >= 6 else "warning", "Party simulation produces multi-seat discussion output.", {"line_count": distinct_lines}))

    status = "ok"
    if any(s.status == "fail" for s in scenarios):
        status = "fail"
    elif any(s.status == "warning" for s in scenarios):
        status = "warning"
    return RegressionSuiteResult(status=status, scenarios=scenarios)
