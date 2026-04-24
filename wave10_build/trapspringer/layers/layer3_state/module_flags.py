from __future__ import annotations

V020_MAIN_PATH_FLAGS = {
    "event1_started": False,
    "event1_resolved": False,
    "goldmoon_joined": False,
    "riverwind_joined": False,
    "staff_in_party_possession": False,
    "xak_tsaroth_reached": False,
    "area_44f_resolved": False,
    "wicker_dragon_discovered": False,
    "khisanth_surface_seen": False,
    "khisanth_surface_encounter_resolved": False,
    "temple_mishakal_reached": False,
    "mishakal_audience_complete": False,
    "staff_recharged": False,
    "staff_recharged_at_mishakal": False,
    "descent_started": False,
    "great_well_descended": False,
    "lower_city_reached": False,
    "secret_route_known": False,
    "dragon_lair_reached": False,
    "dragon_lair_entered": False,
    "disks_recovered": False,
    "staff_shattered": False,
    "khisanth_defeated": False,
    "collapse_escape_started": False,
    "collapse_escaped": False,
    "medallion_created": False,
    "clerical_magic_restored": False,
    "epilogue_complete": False,
    "dragonarmy_march_started": False,
    "xak_tsaroth_surface_entered": False,
    "cavern_collapse_active": False,
    "toede_fled": False,
    "current_route": "ROAD_EAST_OF_SOLACE",
    "current_milestone": "start_of_event_1",
}


def initialize_v020_flags() -> dict[str, object]:
    return dict(V020_MAIN_PATH_FLAGS)


def _set_flag(module_state, flag: str, value: bool = True) -> None:
    # Preserve older quest_flags aliases where existing code already uses them.
    if hasattr(module_state, "world_flags"):
        module_state.world_flags[flag] = value
    if flag in {"staff_in_party_possession", "staff_recharged_at_mishakal", "disks_recovered", "khisanth_defeated", "staff_shattered", "medallion_created", "clerical_magic_restored"}:
        module_state.quest_flags[flag] = value


def set_module_flags(module_state, flags: list[str]) -> None:
    for flag in flags:
        _set_flag(module_state, flag, True)


def has_required_flags(module_state, flags: list[str]) -> bool:
    return all(bool(module_state.world_flags.get(flag) or module_state.quest_flags.get(flag)) for flag in flags)


def initial_dl1_module_state():
    from trapspringer.schemas.state import ModuleState
    flags = initialize_v020_flags()
    quest = {
        "staff_in_party_possession": False,
        "staff_recharged_at_mishakal": False,
        "disks_recovered": False,
        "khisanth_defeated": False,
        "staff_shattered": False,
        "medallion_created": False,
        "clerical_magic_restored": False,
    }
    return ModuleState(
        module_state_id="MODULE-DL1-0001",
        entered_areas=[],
        resolved_encounters=[],
        triggered_events={
            "EVENT_1": False,
            "EVENT_2": False,
            "EVENT_3": False,
            "EVENT_4": False,
            "EVENT_5": False,
            "EVENT_6": False,
            "EVENT_7": False,
        },
        quest_flags=quest,
        world_flags=flags,
    )
