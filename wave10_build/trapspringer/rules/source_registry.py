from dataclasses import dataclass, field

@dataclass(slots=True)
class SourceRecord:
    source_id: str
    title: str
    scopes: list[str] = field(default_factory=list)
    enabled: bool = True

class SourceRegistry:
    def __init__(self) -> None:
        self.sources: dict[str, SourceRecord] = {}

    def register(self, record: SourceRecord) -> None:
        self.sources[record.source_id] = record

    def get(self, source_id: str) -> SourceRecord | None:
        return self.sources.get(source_id)
