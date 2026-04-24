from dataclasses import dataclass, field

@dataclass(slots=True)
class KnowledgeResult:
    status: str
    facts: list[dict[str, object]] = field(default_factory=list)

@dataclass(slots=True)
class KnowledgeDiff:
    status: str
    changes: list[dict[str, object]] = field(default_factory=list)
