from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any

from trapspringer.layers.layer10_audit.leak_detection import public_event_count, scan_public_narration_for_leaks
from trapspringer.services.hash_service import stable_hash


@dataclass(slots=True)
class QualityCheck:
    name: str
    status: str
    detail: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class QualityReport:
    status: str
    checks: list[QualityCheck]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "summary": self.summary, "checks": [c.to_dict() for c in self.checks]}


def _ok(name: str, detail: str = "", **data: Any) -> QualityCheck:
    return QualityCheck(name=name, status="ok", detail=detail, data=data)


def _warn(name: str, detail: str = "", **data: Any) -> QualityCheck:
    return QualityCheck(name=name, status="warning", detail=detail, data=data)


def _fail(name: str, detail: str = "", **data: Any) -> QualityCheck:
    return QualityCheck(name=name, status="fail", detail=detail, data=data)


class QualityGateService:
    """Wave 11 campaign-quality gate.

    This service does not run the game. It inspects a live orchestrator/session
    after a scenario and reports regressions that would reduce trust in the
    simulator: hidden-info leaks, bad state, missing snapshots, replay/hash drift,
    and insufficient audit coverage.
    """

    def run(self, orchestrator: Any) -> QualityReport:
        state = orchestrator.layer3.read_state()
        events = orchestrator.layer10.event_log.events
        checks: list[QualityCheck] = []

        integrity = orchestrator.layer10.check_integrity()
        if integrity.get("status") == "ok":
            checks.append(_ok("audit_integrity", "Audit integrity checker reports ok."))
        else:
            checks.append(_warn("audit_integrity", "Integrity warnings present.", issues=integrity.get("issues", [])))

        leaks = scan_public_narration_for_leaks(events)
        checks.append(_ok("public_leak_scan", "No suspicious public narration leaks found.") if not leaks else _fail("public_leak_scan", "Potential hidden-info leak(s) in public narration.", leaks=leaks))

        snapshots = getattr(orchestrator.layer10.snapshots, "snapshots", {})
        checks.append(_ok("snapshot_presence", f"{len(snapshots)} snapshot(s) available.") if snapshots else _fail("snapshot_presence", "No snapshots available."))

        state_hash = stable_hash(state)
        checks.append(_ok("state_hash", "Current state has a stable hash.", state_hash=state_hash))

        characters = state.get("characters", {})
        bad_hp = []
        for actor_id, actor in characters.items():
            hp = getattr(actor, "current_hp", 0)
            max_hp = getattr(actor, "max_hp", 0)
            status = getattr(actor, "status", "")
            if hp > max_hp or (hp <= 0 and status not in {"defeated", "dead", "unconscious", "fled"}):
                bad_hp.append({"actor_id": actor_id, "current_hp": hp, "max_hp": max_hp, "status": status})
        checks.append(_ok("character_state_consistency", "HP/status consistency checks passed.") if not bad_hp else _fail("character_state_consistency", "HP/status inconsistency detected.", actors=bad_hp))

        public_count = public_event_count(events)
        checks.append(_ok("public_event_coverage", f"{public_count} public/actor-private event(s) recorded.", count=public_count) if public_count >= 2 else _warn("public_event_coverage", "Very few public events recorded.", count=public_count))

        event_types = {event.get("event_type") for event in events}
        required_types = {"narration_event", "snapshot_event"}
        missing = sorted(required_types - event_types)
        checks.append(_ok("required_event_types", "Required event types present.") if not missing else _warn("required_event_types", "Some required event types are missing.", missing=missing))

        status = "ok"
        if any(c.status == "fail" for c in checks):
            status = "fail"
        elif any(c.status == "warning" for c in checks):
            status = "warning"
        summary = f"Wave 11 quality gates: {status.upper()} ({sum(c.status == 'ok' for c in checks)}/{len(checks)} ok)."
        return QualityReport(status=status, checks=checks, summary=summary)
