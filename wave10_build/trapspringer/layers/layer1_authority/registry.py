from trapspringer.rules.source_registry import SourceRegistry, SourceRecord

def build_default_registry() -> SourceRegistry:
    registry = SourceRegistry()
    registry.register(SourceRecord("SIM_CONSTITUTION", "Simulator Constitution", ["secrecy", "authority_trace"]))
    registry.register(SourceRecord("DL1", "DL1 Dragons of Despair", ["module_content", "module_events", "module_map"]))
    registry.register(SourceRecord("PHB", "AD&D 1e Player's Handbook", ["classes", "spells", "equipment"]))
    registry.register(SourceRecord("DMG", "AD&D 1e Dungeon Master's Guide", ["combat_procedure", "morale", "saving_throws"]))
    registry.register(SourceRecord("MM", "AD&D 1e Monster Manual", ["monster_stats", "special_attacks", "special_defenses"]))
    return registry
