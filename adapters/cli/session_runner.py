from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from trapspringer.engine.orchestrator import EngineTurnResult, Orchestrator
from trapspringer.services.persistence_service import SessionPersistenceService


@dataclass(slots=True)
class DemoRun:
    opening: EngineTurnResult
    round_result: EngineTurnResult | None = None
    recap: str | None = None
    integrity: dict | None = None
    save_record: dict[str, Any] | None = None
    state: dict[str, Any] | None = None
    orchestrator: Orchestrator | None = None


def run_event1_demo(
    user_input: str = "I attack the nearest hobgoblin",
    user_character_id: str = "PC_TANIS",
    save_dir: str | Path | None = None,
    save_label: str | None = None,
) -> DemoRun:
    orchestrator = Orchestrator()
    session = orchestrator.start_campaign("CLI-DEMO", user_character_id=user_character_id)
    opening = orchestrator.step(session)
    round_result = orchestrator.step(session, user_input)
    save_record = None
    if save_dir is not None:
        store = SessionPersistenceService(save_dir)
        save_record = store.save_session(session, orchestrator.layer3.read_state(), orchestrator.layer10, label=save_label or "event1_demo")
    return DemoRun(
        opening=opening,
        round_result=round_result,
        recap=orchestrator.layer10.recap(limit=20),
        integrity=orchestrator.layer10.check_integrity(),
        save_record=save_record,
        state=orchestrator.layer3.read_state(),
        orchestrator=orchestrator,
    )


@dataclass(slots=True)
class Wave6DemoRun:
    outputs: list[EngineTurnResult]
    recap: str | None = None
    integrity: dict | None = None
    save_record: dict[str, Any] | None = None
    state: dict[str, Any] | None = None
    orchestrator: Orchestrator | None = None


def run_wave6_story_demo(
    user_character_id: str = "PC_TANIS",
    save_dir: str | Path | None = None,
    save_label: str | None = None,
) -> Wave6DemoRun:
    orchestrator = Orchestrator()
    session = orchestrator.start_campaign("CLI-WAVE6-DEMO", user_character_id=user_character_id)
    opening = orchestrator.step(session)
    round_result = orchestrator.step(session, "I attack the nearest hobgoblin")
    story_outputs = orchestrator.run_wave6_story_demo(session)
    save_record = None
    if save_dir is not None:
        store = SessionPersistenceService(save_dir)
        save_record = store.save_session(session, orchestrator.layer3.read_state(), orchestrator.layer10, label=save_label or "wave6_demo")
    return Wave6DemoRun(
        outputs=[opening, round_result] + story_outputs,
        recap=orchestrator.layer10.recap(limit=40),
        integrity=orchestrator.layer10.check_integrity(),
        save_record=save_record,
        state=orchestrator.layer3.read_state(),
        orchestrator=orchestrator,
    )


@dataclass(slots=True)
class Wave9DemoRun:
    outputs: list[str]
    recap: str | None = None
    integrity: dict | None = None
    save_record: dict[str, Any] | None = None
    state: dict[str, Any] | None = None
    orchestrator: Orchestrator | None = None


def run_wave9_party_demo(
    user_character_id: str = "PC_TANIS",
    save_dir: str | Path | None = None,
    save_label: str | None = None,
) -> Wave9DemoRun:
    """Demonstrate Wave 9 deep party simulation without requiring a full playthrough."""
    orchestrator = Orchestrator()
    session = orchestrator.start_campaign("CLI-WAVE9-DEMO", user_character_id=user_character_id)
    orchestrator.step(session)
    outputs: list[str] = []
    scenes = [
        ("DL1_AREA_44F", ["camp_visible", "dragon_shape_visible"]),
        ("DL1_AREA_44K", ["temple_visible_north", "well_visible_center", "open_plaza"]),
    ]
    for scene_id, public_info in scenes:
        bundle = orchestrator.layer8.simulate_discussion({"scene_id": scene_id, "available_public_information": public_info})
        lines = [f"[{scene_id}] tone={bundle.emotional_tone}"]
        for line in bundle.discussion:
            lines.append(f"{line.speaker} ({line.channel}): {line.text}")
        if bundle.dissent:
            lines.append("Dissent: " + "; ".join(bundle.dissent))
        if bundle.mapper_notes:
            lines.append("Mapper: " + "; ".join(note["note"] for note in bundle.mapper_notes))
        lines.append(bundle.caller_summary or "No caller summary.")
        outputs.append("\n".join(lines))
    reaction = orchestrator.layer8.react_to_user_action("I charge the closest enemy", "DL1_AREA_44K")
    outputs.append("\n".join(["[User action reaction]"] + [f"{l.speaker}: {l.text}" for l in reaction.discussion] + (reaction.dissent or [])))
    save_record = None
    if save_dir is not None:
        store = SessionPersistenceService(save_dir)
        save_record = store.save_session(session, orchestrator.layer3.read_state(), orchestrator.layer10, label=save_label or "wave9_party_demo")
    return Wave9DemoRun(outputs=outputs, recap=orchestrator.layer10.recap(limit=20), integrity=orchestrator.layer10.check_integrity(), save_record=save_record, state=orchestrator.layer3.read_state(), orchestrator=orchestrator)


@dataclass(slots=True)
class Wave11DemoRun:
    output: str
    report: dict[str, Any]
    status: str


def run_wave11_quality_demo() -> Wave11DemoRun:
    from trapspringer.adapters.test_harness.regression_suite import run_wave11_regression_suite

    result = run_wave11_regression_suite()
    lines = [f"Wave 11 regression suite: {result.status.upper()}"]
    for scenario in result.scenarios:
        lines.append(f"- {scenario.name}: {scenario.status.upper()} — {scenario.detail}")
    return Wave11DemoRun(output="\n".join(lines), report=result.to_dict(), status=result.status)


@dataclass(slots=True)
class V020MainPathRun:
    outputs: list[EngineTurnResult]
    recap: str | None = None
    integrity: dict | None = None
    save_record: dict[str, Any] | None = None
    state: dict[str, Any] | None = None
    orchestrator: Orchestrator | None = None


def run_v020_main_path_demo(
    user_character_id: str = "PC_TANIS",
    save_dir: str | Path | None = None,
    save_label: str | None = None,
) -> V020MainPathRun:
    orchestrator = Orchestrator()
    session = orchestrator.start_campaign("CLI-V020-MAIN-PATH", user_character_id=user_character_id)
    opening = orchestrator.step(session)
    round_result = orchestrator.step(session, "I attack the nearest hobgoblin")
    story_outputs = orchestrator.run_v020_main_path_demo(session)
    save_record = None
    if save_dir is not None:
        store = SessionPersistenceService(save_dir)
        save_record = store.save_session(session, orchestrator.layer3.read_state(), orchestrator.layer10, label=save_label or "v020_main_path")
    return V020MainPathRun(
        outputs=[opening, round_result] + story_outputs,
        recap=orchestrator.layer10.recap(limit=80),
        integrity=orchestrator.layer10.check_integrity(),
        save_record=save_record,
        state=orchestrator.layer3.read_state(),
        orchestrator=orchestrator,
    )
