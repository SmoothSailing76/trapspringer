from __future__ import annotations

from dataclasses import dataclass, asdict
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

@dataclass(slots=True)
class V030SpatialRun:
    output: str
    summary: dict[str, Any]
    validation: dict[str, Any]


def run_v030_spatial_demo() -> V030SpatialRun:
    from trapspringer.layers.layer9_map.service import MapVisibilityService
    from trapspringer.adapters.cli.renderers import render_v030_spatial_summary

    layer9 = MapVisibilityService()
    summary = layer9.dl1_spatial_summary()
    validation = layer9.validate_dl1_spatial_assets()
    lines = [render_v030_spatial_summary(summary), "", "Asset validation:", f"  ok: {validation.get('ok')}"]
    missing = validation.get("missing") or []
    if missing:
        lines.append("  missing:")
        lines.extend(f"    {item}" for item in missing)
    level4 = layer9.load_xak_tsaroth_level(4)
    lines.append("")
    lines.append(f"Level 4 encounter areas indexed: {len(level4.get('encounter_areas', []))}")
    return V030SpatialRun(output="\n".join(lines), summary=summary, validation=validation)

@dataclass(slots=True)
class V040RulesRun:
    output: str
    summary: dict[str, Any]


def run_v040_rules_demo() -> V040RulesRun:
    """Demonstrate v0.4 AD&D rules facade without requiring a full campaign run."""
    from types import SimpleNamespace
    from trapspringer.rules import adnd1e_v04
    from trapspringer.rules.capabilities import default_rules_capability_registry
    from trapspringer.layers.layer6_resolution.service import ResolutionService
    from trapspringer.layers.layer6_resolution.morale import resolve_morale, resolve_reaction
    from trapspringer.layers.layer6_resolution.items import resolve_item_save
    from trapspringer.services.random_service import RandomService

    rng = RandomService(seed=4)
    tanis = SimpleNamespace(actor_id="PC_TANIS", name="Tanis", character_class="fighter", level=5, ac=4, team="party", current_hp=35, max_hp=35, conditions=[], inventory=["sword", "longbow"])
    bozak = SimpleNamespace(actor_id="BOZAK_1", name="Bozak", character_class="monster", level=4, ac=2, team="enemy", current_hp=18, max_hp=18, conditions=[], inventory=[], damage="1d8")
    checks = {
        "attack_target": asdict(adnd1e_v04.attack_target(tanis, bozak)),
        "saving_throw_spell": asdict(adnd1e_v04.roll_saving_throw(tanis, "spell", rng)),
        "initiative": {"party": asdict(adnd1e_v04.initiative(rng, "party")), "enemy": asdict(adnd1e_v04.initiative(rng, "enemy"))},
        "surprise": asdict(adnd1e_v04.surprise(rng, "party")),
        "turn_undead": asdict(adnd1e_v04.turn_undead(SimpleNamespace(actor_id="PC_GOLDMOON", character_class="cleric", level=5, team="party"), "ghoul", rng)),
        "encumbrance": asdict(adnd1e_v04.encumbrance_move(12, 900, strength=16)),
        "morale": resolve_morale({"morale_score": 8, "group_id": "bozak_guard"}, rng),
        "reaction": resolve_reaction({"npc_id": "aghar", "modifier": 1}, rng),
        "item_save": resolve_item_save({"material": "wood", "attack_form": "fire"}, rng),
    }
    state = {"characters": {"PC_TANIS": tanis, "BOZAK_1": bozak}}
    spell_result = ResolutionService(rng).resolve_spell_effect({"actor_id": "PC_TANIS", "target_id": "BOZAK_1", "spell": "magic_missile"}, state)
    checks["spell_result"] = {"status": spell_result.status, "private": spell_result.private_outcome.summary, "public": spell_result.public_outcome.narration}
    caps = default_rules_capability_registry().summary()
    lines = ["Trapspringer v0.4 AD&D rules facade demo", f"Capability summary: {caps}"]
    lines.append(f"Attack target vs AC 2: {checks['attack_target']['target']}")
    lines.append(f"Saving throw vs spell: {checks['saving_throw_spell']['result']}")
    lines.append(f"Initiative winner roll totals: party={checks['initiative']['party']['result']}, enemy={checks['initiative']['enemy']['result']}")
    lines.append(f"Surprise: {checks['surprise']['result']}")
    lines.append(f"Turn undead: {checks['turn_undead']['result']}")
    lines.append(f"Encumbrance: {checks['encumbrance']['result']} move {checks['encumbrance']['target']}")
    lines.append(f"Morale: {checks['morale']['result']}; reaction: {checks['reaction']['result']}")
    lines.append(f"Item save: {checks['item_save']['result']}")
    lines.append(str(checks["spell_result"]["public"]))
    return V040RulesRun(output="\n".join(lines), summary=checks)
