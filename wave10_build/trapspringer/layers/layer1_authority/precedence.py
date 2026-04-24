def choose_source_for_domain(domain: str) -> str:
    if domain.startswith("module"):
        return "DL1"
    if domain in {"monster_resolution", "monster_stats"}:
        return "MM"
    if domain in {"combat_procedure", "saving_throws"}:
        return "DMG"
    if domain in {"core_rules", "classes", "spells", "equipment"}:
        return "PHB"
    return "SIM_CONSTITUTION"
