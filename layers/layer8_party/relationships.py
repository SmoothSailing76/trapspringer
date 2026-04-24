from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RelationshipVector:
    trust: float = 0.5
    irritation: float = 0.0
    protectiveness: float = 0.0
    deference: float = 0.0
    rivalry: float = 0.0


class RelationshipStore:
    """Small deterministic relationship graph for Wave 9 table dynamics."""

    def __init__(self) -> None:
        self.relationships: dict[tuple[str, str], RelationshipVector] = {}
        self._seed_defaults()

    def _seed_defaults(self) -> None:
        self.set("PC_CARAMON", "PC_RAISTLIN", protectiveness=0.95, trust=0.82, deference=0.35)
        self.set("PC_RAISTLIN", "PC_CARAMON", trust=0.70, irritation=0.20)
        self.set("PC_FLINT", "PC_TASSLEHOFF", irritation=0.62, protectiveness=0.44, trust=0.60)
        self.set("PC_STURM", "PC_TANIS", trust=0.72, deference=0.28, rivalry=0.18)
        self.set("PC_GOLDMOON", "NPC_RIVERWIND", trust=0.96, protectiveness=0.70)
        self.set("NPC_RIVERWIND", "PC_GOLDMOON", trust=0.98, protectiveness=0.96)

    def set(self, source: str, target: str, **values: float) -> None:
        current = self.relationships.get((source, target), RelationshipVector())
        for key, value in values.items():
            if hasattr(current, key):
                setattr(current, key, value)
        self.relationships[(source, target)] = current

    def get(self, source: str, target: str) -> RelationshipVector:
        return self.relationships.get((source, target), RelationshipVector())

    def nudge_after_event(self, event_tag: str) -> None:
        if event_tag == "khisanth_surface":
            for pair, rel in list(self.relationships.items()):
                rel.trust = min(1.0, rel.trust + 0.03)
        if event_tag == "tasslehoff_risk":
            self.set("PC_FLINT", "PC_TASSLEHOFF", irritation=min(1.0, self.get("PC_FLINT", "PC_TASSLEHOFF").irritation + 0.12))

    def summary_for(self, actor_id: str) -> list[str]:
        notes: list[str] = []
        for (src, dst), rel in self.relationships.items():
            if src != actor_id:
                continue
            if rel.protectiveness > 0.75:
                notes.append(f"protective_of:{dst}")
            if rel.irritation > 0.55:
                notes.append(f"irritated_by:{dst}")
            if rel.deference > 0.5:
                notes.append(f"defers_to:{dst}")
        return notes
