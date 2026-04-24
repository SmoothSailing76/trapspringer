from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from trapspringer.engine.orchestrator import Orchestrator
from trapspringer.engine.runtime import RuntimeSession
from trapspringer.public_api.models import PublicSession, PublicStateView, PublicTurnResult
from trapspringer.services.persistence_service import SessionPersistenceService


def _plain(obj: Any) -> Any:
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, dict):
        return {k: _plain(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_plain(v) for v in obj]
    return obj


class TrapspringerAPI:
    """Stable API facade for CLI, web UI, bots, and tests.

    This boundary intentionally hides layer internals behind a small set of
    operations: start, step, run a demo path, save/load, public state, and audit.
    """

    def __init__(self, save_dir: str | Path = "./saves") -> None:
        self.orchestrator = Orchestrator()
        self.session: RuntimeSession | None = None
        self.save_store = SessionPersistenceService(save_dir)

    def start_campaign(self, campaign: str = "dl1", *, campaign_id: str = "API-DL1", user_character_id: str = "PC_TANIS") -> PublicSession:
        if campaign.lower() != "dl1":
            raise ValueError(f"Unsupported campaign: {campaign}")
        self.session = self.orchestrator.start_campaign(campaign_id, user_character_id=user_character_id)
        return self._public_session()

    def step(self, declaration: str | None = None) -> PublicTurnResult:
        if self.session is None:
            self.start_campaign()
        result = self.orchestrator.step(self.session, declaration)
        return PublicTurnResult(
            narration=result.narration,
            prompt=result.prompt,
            public_events=self.audit_log(public_only=True),
            status=self.status(),
        )

    def run_main_path_demo(self) -> list[PublicTurnResult]:
        if self.session is None:
            self.start_campaign(campaign_id="API-DL1-MAIN-PATH")
        opening = self.orchestrator.step(self.session)
        round_one = self.orchestrator.step(self.session, "I attack the nearest hobgoblin")
        outputs = [opening, round_one] + self.orchestrator.run_v020_main_path_demo(self.session)
        return [PublicTurnResult(o.narration, o.prompt, self.audit_log(public_only=True), self.status()) for o in outputs]

    def status(self) -> dict[str, Any]:
        return self.orchestrator.main_path_status()

    def public_state(self) -> PublicStateView:
        state = self.orchestrator.layer3.read_state()
        status = self.status()
        party = []
        for actor_id in state["party"].member_ids:
            actor = state["characters"].get(actor_id)
            if actor is None:
                continue
            party.append({
                "actor_id": actor.actor_id,
                "name": actor.name,
                "current_hp": actor.current_hp,
                "max_hp": actor.max_hp,
                "status": actor.status,
                "team": actor.team,
            })
        public_flags = {
            key: value for key, value in state["module"].world_flags.items()
            if key in {"current_milestone", "event1_resolved", "goldmoon_joined", "staff_recharged", "secret_route_known", "disks_recovered", "staff_shattered", "epilogue_complete"}
        }
        return PublicStateView(
            campaign_id=state["campaign"].campaign_id,
            active_scene_id=state["campaign"].active_scene_id,
            milestone_id=status.get("milestone_id"),
            milestone_label=status.get("milestone_label"),
            party=party,
            public_flags=public_flags,
        )

    def save(self, label: str = "api_save") -> dict[str, Any]:
        if self.session is None:
            raise RuntimeError("No active session to save")
        return self.save_store.save_session(self.session, self.orchestrator.layer3.read_state(), self.orchestrator.layer10, label=label)

    def load(self, save_id_or_path: str) -> dict[str, Any]:
        return self.save_store.load_bundle(save_id_or_path)

    def audit_log(self, *, public_only: bool = False) -> list[dict[str, Any]]:
        events = [_plain(event) for event in self.orchestrator.layer10.event_log.events]
        if public_only:
            events = [event for event in events if event.get("visibility") == "public_table"]
        return events

    def replay(self, snapshot_id: str | None = None, to_event_sequence: int | None = None) -> dict[str, Any]:
        checkpoints = self.orchestrator.layer10.checkpoint_ids()
        if snapshot_id is None:
            snapshot_id = checkpoints.get("start_of_event_1") or next(iter(checkpoints.values()), "")
        return self.orchestrator.layer10.replay({"from_snapshot": snapshot_id, "to_event_sequence": to_event_sequence})

    def _public_session(self) -> PublicSession:
        if self.session is None:
            raise RuntimeError("No active session")
        status = self.status()
        return PublicSession(
            session_id=self.session.context.campaign_id,
            campaign_id=self.session.context.campaign_id,
            module_id=self.session.context.module_id,
            active_scene_id=self.session.context.active_scene_id,
            current_milestone=str(status.get("milestone_id")),
        )


def create_api(save_dir: str | Path = "./saves") -> TrapspringerAPI:
    return TrapspringerAPI(save_dir=save_dir)
