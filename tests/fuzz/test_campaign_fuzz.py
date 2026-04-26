"""Campaign fuzz tests: run N random playthroughs and verify no crashes, state corruption, or knowledge leaks."""
from __future__ import annotations

import random

from trapspringer.adapters.cli.session_runner import run_event1_demo, run_v020_main_path_demo
from trapspringer.services.quality_service import QualityGateService

_CHARACTERS = ["PC_TANIS", "PC_CARAMON", "PC_RAISTLIN", "PC_GOLDMOON", "PC_STURM", "PC_FLINT", "PC_TASSLEHOFF"]
_ACTIONS = [
    "I attack the nearest hobgoblin",
    "I cast magic missile at the nearest enemy",
    "I defend and wait",
    "I retreat to the treeline",
    "I fire my bow at the hobgoblin leader",
    "I try to take a prisoner",
    "I cast sleep on the group",
]


def _run_one_event1(seed: int) -> dict:
    rng = random.Random(seed)
    character = rng.choice(_CHARACTERS)
    action = rng.choice(_ACTIONS)
    demo = run_event1_demo(user_input=action, user_character_id=character)
    state = demo.state or {}
    chars = state.get("characters", {}) if isinstance(state, dict) else {}
    active_party = [cid for cid, c in chars.items() if getattr(c, "team", None) == "party" and getattr(c, "is_active", False)]
    return {
        "seed": seed,
        "character": character,
        "action": action,
        "narration_length": len(demo.opening.narration or ""),
        "integrity": demo.integrity,
        "active_party_count": len(active_party),
        "crash": False,
    }


def test_fuzz_event1_ten_random_seeds():
    """10 random Event 1 runs with different characters and actions — none should crash."""
    quality = QualityGateService()
    failures = []
    for seed in range(42, 52):
        try:
            result = _run_one_event1(seed)
            assert result["narration_length"] > 0, f"Empty narration at seed {seed}"
            integrity = result["integrity"]
            integrity_status = integrity.get("status") if isinstance(integrity, dict) else integrity
            assert integrity_status in ("ok", "warning"), f"Bad integrity at seed {seed}: {integrity}"
        except Exception as exc:
            failures.append({"seed": seed, "error": str(exc)})
    assert not failures, f"Fuzz failures: {failures}"


def test_fuzz_main_path_three_characters():
    """Full DL1 main path run for 3 different starting characters — should reach epilogue without crash."""
    quality = QualityGateService()
    for character in ["PC_TANIS", "PC_CARAMON", "PC_GOLDMOON"]:
        demo = run_v020_main_path_demo(user_character_id=character)
        state = demo.state or {}
        module = state.get("module") if isinstance(state, dict) else None
        quest_flags = getattr(module, "quest_flags", {}) if module else {}
        world_flags = getattr(module, "world_flags", {}) if module else {}
        assert quest_flags.get("medallion_created") or world_flags.get("medallion_created"), \
            f"Epilogue not reached for {character}"
        report = quality.run(demo.orchestrator)
        assert report.status in ("ok", "warning"), f"Quality gate failed for {character}: {report.status}"


def test_fuzz_no_knowledge_leaks_across_runs():
    """Verify no DM-private facts leak into public narration across multiple runs."""
    private_markers = ["dm_private", "actor_private", "secret_route_known_early"]
    for seed in range(100, 106):
        rng = random.Random(seed)
        character = rng.choice(_CHARACTERS)
        action = rng.choice(_ACTIONS)
        demo = run_event1_demo(user_input=action, user_character_id=character)
        narration = (demo.opening.narration or "") + (getattr(demo.round_result, "narration", None) or "")
        for marker in private_markers:
            assert marker not in narration.lower(), \
                f"Private marker '{marker}' leaked into narration at seed {seed}"


def test_fuzz_state_never_corrupts_hp():
    """HP values across 5 runs must always be non-negative integers."""
    for seed in range(200, 205):
        rng = random.Random(seed)
        character = rng.choice(_CHARACTERS)
        action = rng.choice(_ACTIONS)
        demo = run_event1_demo(user_input=action, user_character_id=character)
        state = demo.state or {}
        chars = state.get("characters", {}) if isinstance(state, dict) else {}
        for cid, c in chars.items():
            hp = getattr(c, "current_hp", None)
            if hp is not None:
                assert isinstance(hp, (int, float)) and hp >= 0, \
                    f"Corrupted HP for {cid} at seed {seed}: {hp}"
