from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class MemoryRecord:
    fact_id: str
    text: str
    learned_at_scene: str
    confidence: float = 1.0
    tags: list[str] = field(default_factory=list)
    last_recalled_scene: str | None = None


class PartyMemoryStore:
    """Deterministic long-term table memory for simulated players."""

    def __init__(self) -> None:
        self.memories: dict[str, list[MemoryRecord]] = {}

    def remember(self, actor_id: str, fact_id: str, text: str, scene_id: str, confidence: float = 1.0, tags: list[str] | None = None) -> MemoryRecord:
        record = MemoryRecord(fact_id=fact_id, text=text, learned_at_scene=scene_id, confidence=confidence, tags=list(tags or []))
        existing = self.memories.setdefault(actor_id, [])
        for idx, old in enumerate(existing):
            if old.fact_id == fact_id:
                existing[idx] = record
                return record
        existing.append(record)
        return record

    def remember_for_party(self, actor_ids: list[str], fact_id: str, text: str, scene_id: str, confidence: float = 1.0, tags: list[str] | None = None) -> list[MemoryRecord]:
        return [self.remember(actor_id, fact_id, text, scene_id, confidence, tags) for actor_id in actor_ids]

    def recall(self, actor_id: str, scene_id: str, tags: list[str] | None = None, memory_reliability: float = 0.75, limit: int = 3) -> list[MemoryRecord]:
        wanted = set(tags or [])
        recalled: list[MemoryRecord] = []
        for record in self.memories.get(actor_id, []):
            if wanted and not wanted.intersection(record.tags):
                continue
            if record.confidence <= memory_reliability + 0.20:
                record.last_recalled_scene = scene_id
                recalled.append(record)
            if len(recalled) >= limit:
                break
        return recalled

    def imperfect_recall_line(self, actor_id: str, scene_id: str, tags: list[str] | None = None, memory_reliability: float = 0.75) -> str | None:
        recalled = self.recall(actor_id, scene_id, tags=tags, memory_reliability=memory_reliability, limit=1)
        if recalled:
            return recalled[0].text
        if memory_reliability < 0.55:
            return "I remember something about this, but not the exact detail."
        return None

    def to_dict(self) -> dict[str, list[dict[str, object]]]:
        return {actor_id: [asdict(record) for record in records] for actor_id, records in self.memories.items()}
