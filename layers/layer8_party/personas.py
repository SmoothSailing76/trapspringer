from __future__ import annotations

from trapspringer.schemas.party import CharacterPersona, PlayerPersona

# Wave 9: richer table personas. Values are deliberately lightweight and
# deterministic; they drive table voice without needing an LLM or hidden state.
PLAYER_PERSONAS: dict[str, dict[str, object]] = {
    "PC_TANIS": dict(archetype="firm_consensus_builder", talkativeness=0.62, assertiveness=0.74, rules_mastery=0.68, risk_tolerance=0.46, tactical_focus=0.72, roleplay_focus=0.65, memory_reliability=0.82, cooperativeness=0.86, meta_restraint=0.78, conflict_tolerance=0.50, deference_to_caller=0.85, attachment_to_mission=0.86),
    "PC_TASSLEHOFF": dict(archetype="curious_instigator", talkativeness=0.90, assertiveness=0.56, rules_mastery=0.42, risk_tolerance=0.92, tactical_focus=0.34, roleplay_focus=0.86, memory_reliability=0.62, cooperativeness=0.68, meta_restraint=0.45, humor_level=0.72, conflict_tolerance=0.28, spotlight_seeking=0.82, attachment_to_loot=0.65),
    "PC_STURM": dict(archetype="honorable_tactician", talkativeness=0.50, assertiveness=0.78, rules_mastery=0.66, risk_tolerance=0.58, tactical_focus=0.82, roleplay_focus=0.70, memory_reliability=0.80, cooperativeness=0.72, meta_restraint=0.82, conflict_tolerance=0.56, attachment_to_mission=0.78),
    "PC_CARAMON": dict(archetype="protective_frontliner", talkativeness=0.58, assertiveness=0.60, rules_mastery=0.44, risk_tolerance=0.70, tactical_focus=0.58, roleplay_focus=0.45, memory_reliability=0.70, cooperativeness=0.84, meta_restraint=0.68, attachment_to_character_safety=0.72, attachment_to_mission=0.70),
    "PC_RAISTLIN": dict(archetype="sharp_rules_skeptic", talkativeness=0.36, assertiveness=0.70, rules_mastery=0.88, risk_tolerance=0.30, tactical_focus=0.78, roleplay_focus=0.62, memory_reliability=0.88, cooperativeness=0.45, meta_restraint=0.80, conflict_tolerance=0.72, attachment_to_character_safety=0.80),
    "PC_FLINT": dict(archetype="gruff_cautious_mapper", talkativeness=0.68, assertiveness=0.72, rules_mastery=0.56, risk_tolerance=0.34, tactical_focus=0.70, roleplay_focus=0.55, memory_reliability=0.78, cooperativeness=0.70, meta_restraint=0.74, humor_level=0.34, conflict_tolerance=0.62, attachment_to_loot=0.42),
    "PC_GOLDMOON": dict(archetype="mission_focused_mediator", talkativeness=0.58, assertiveness=0.62, rules_mastery=0.50, risk_tolerance=0.48, tactical_focus=0.45, roleplay_focus=0.82, memory_reliability=0.84, cooperativeness=0.88, meta_restraint=0.86, attachment_to_mission=0.92),
    "NPC_RIVERWIND": dict(archetype="watchful_guardian", talkativeness=0.38, assertiveness=0.66, rules_mastery=0.55, risk_tolerance=0.52, tactical_focus=0.76, roleplay_focus=0.55, memory_reliability=0.82, cooperativeness=0.64, meta_restraint=0.88, attachment_to_character_safety=0.75),
}

CHARACTER_PERSONAS: dict[str, dict[str, object]] = {
    "PC_TANIS": dict(temperament=["measured", "responsible", "wry"], core_goals=["keep_party_together", "choose_survivable_path", "protect_staff_bearer"], preferred_actions=["coordinate", "missile_or_melee", "negotiate"], social_style="dry_leader", courage=0.70, caution=0.60, discipline=0.75, protectiveness=0.72),
    "PC_TASSLEHOFF": dict(temperament=["curious", "fearless", "cheerful"], core_goals=["see_interesting_things", "help_friends", "open_possibilities"], preferred_actions=["scout", "inspect", "taunt", "improvise"], social_style="bright_mischief", courage=0.95, caution=0.12, curiosity=0.98, discipline=0.24, willingness_to_retreat=0.10),
    "PC_STURM": dict(temperament=["honorable", "formal", "brave"], core_goals=["hold_line", "protect_weak", "act_with_honor"], preferred_actions=["frontline_melee", "guard_ally", "challenge_enemy"], social_style="formal", courage=0.88, caution=0.42, discipline=0.88, protectiveness=0.80, willingness_to_retreat=0.22),
    "PC_CARAMON": dict(temperament=["warm", "loyal", "direct"], core_goals=["protect_raistlin", "stand_between_friends_and_danger"], preferred_actions=["melee", "guard_raistlin", "carry_heavy_load"], social_style="plain_loyal", courage=0.78, caution=0.38, protectiveness=0.92),
    "PC_RAISTLIN": dict(temperament=["cold", "precise", "frail"], core_goals=["preserve_power", "understand_magic", "avoid_needless_risk"], preferred_actions=["stay_back", "cast_spell", "analyze"], social_style="cutting", courage=0.50, caution=0.86, curiosity=0.72, discipline=0.80, willingness_to_retreat=0.68),
    "PC_FLINT": dict(temperament=["gruff", "practical", "loyal"], core_goals=["keep_fools_alive", "avoid_obvious_traps", "hold_line"], preferred_actions=["hold_line", "inspect_stonework", "melee"], social_style="grumbling", courage=0.68, caution=0.72, discipline=0.70, protectiveness=0.70),
    "PC_GOLDMOON": dict(temperament=["compassionate", "resolved", "spiritual"], core_goals=["protect_staff", "seek_truth_of_gods", "keep_riverwind_alive"], preferred_actions=["heal_with_staff", "mediate", "advance_quest"], social_style="gentle_authority", courage=0.72, caution=0.55, mercy=0.88),
    "NPC_RIVERWIND": dict(temperament=["silent", "protective", "suspicious"], core_goals=["protect_goldmoon", "verify_xak_tsaroth_memory", "avoid_traps"], preferred_actions=["guard_goldmoon", "track", "frontline_melee"], social_style="laconic", courage=0.82, caution=0.70, protectiveness=0.96),
}


def _build_player(persona_id: str, data: dict[str, object]) -> PlayerPersona:
    return PlayerPersona(persona_id=persona_id, **data)  # type: ignore[arg-type]


def _build_character(persona_id: str, data: dict[str, object]) -> CharacterPersona:
    return CharacterPersona(persona_id=persona_id, **data)  # type: ignore[arg-type]


def build_default_persona_for_actor(actor_id: str) -> PlayerPersona:
    return _build_player(f"PP-{actor_id}", PLAYER_PERSONAS.get(actor_id, {}))


def build_default_character_persona(actor_id: str) -> CharacterPersona:
    return _build_character(f"CP-{actor_id}", CHARACTER_PERSONAS.get(actor_id, {"preferred_actions": ["cooperate"]}))


def display_name_for_actor(actor_id: str) -> str:
    return actor_id.replace("PC_", "").replace("NPC_", "").title()
