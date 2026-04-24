from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True)
class LayerQuery:
    from_layer: str
    to_layer: str
    query_id: str
    payload: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class LayerCommand:
    from_layer: str
    to_layer: str
    command_id: str
    payload: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class LayerResult:
    from_layer: str
    to_layer: str
    result_id: str
    status: str
    payload: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class LayerEvent:
    from_layer: str
    to_layer: str
    event_id: str
    payload: dict[str, Any] = field(default_factory=dict)
