from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any


def _plain(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


class SerializationService:
    def dumps(self, obj) -> str:
        return json.dumps(_plain(obj), indent=2, sort_keys=True, default=str)

    def loads(self, payload: str):
        return json.loads(payload)
