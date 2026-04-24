from dataclasses import dataclass, field

@dataclass(slots=True)
class IdService:
    counters: dict[str, int] = field(default_factory=dict)

    def next(self, prefix: str) -> str:
        self.counters[prefix] = self.counters.get(prefix, 0) + 1
        return f"{prefix}-{self.counters[prefix]:06d}"
