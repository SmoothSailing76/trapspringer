import hashlib
import json
from dataclasses import asdict, is_dataclass


def _plain(value):
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_plain(v) for v in value]
    return value


def stable_hash(value) -> str:
    data = json.dumps(_plain(value), sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()
