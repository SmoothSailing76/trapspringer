from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CAPABILITY_PATH = PACKAGE_ROOT / "data/manifests/rules_capabilities.json"

VALID_STATUSES = {"implemented", "partial", "stubbed", "unsupported"}

@dataclass(frozen=True, slots=True)
class RuleCapability:
    capability_id: str
    status: str
    public_name: str
    layer: str | None = None
    notes: str | None = None

    @property
    def is_available(self) -> bool:
        return self.status in {"implemented", "partial"}

    @property
    def is_complete(self) -> bool:
        return self.status == "implemented"

@dataclass(slots=True)
class RulesCapabilityRegistry:
    registry_id: str
    engine_version: str
    capabilities: dict[str, RuleCapability]

    def get(self, capability_id: str) -> RuleCapability:
        try:
            return self.capabilities[capability_id]
        except KeyError as exc:
            raise KeyError(f"Unknown rules capability: {capability_id}") from exc

    def status(self, capability_id: str) -> str:
        return self.get(capability_id).status

    def require(self, capability_id: str, *, allow_partial: bool = True) -> RuleCapability:
        cap = self.get(capability_id)
        allowed = {"implemented", "partial"} if allow_partial else {"implemented"}
        if cap.status not in allowed:
            raise RuntimeError(f"Rule capability '{capability_id}' is {cap.status}: {cap.notes or 'no notes'}")
        return cap

    def by_status(self, status: str) -> dict[str, RuleCapability]:
        if status not in VALID_STATUSES:
            raise ValueError(f"Unknown capability status: {status}")
        return {k: v for k, v in self.capabilities.items() if v.status == status}

    def summary(self) -> dict[str, int]:
        return {status: len(self.by_status(status)) for status in sorted(VALID_STATUSES)}

    def to_dict(self) -> dict[str, Any]:
        return {
            "registry_id": self.registry_id,
            "engine_version": self.engine_version,
            "capabilities": {
                key: {
                    "status": cap.status,
                    "public_name": cap.public_name,
                    "layer": cap.layer,
                    "notes": cap.notes,
                    "is_available": cap.is_available,
                    "is_complete": cap.is_complete,
                }
                for key, cap in self.capabilities.items()
            },
        }


def load_rules_capability_registry(path: str | Path | None = None) -> RulesCapabilityRegistry:
    p = Path(path) if path is not None else DEFAULT_CAPABILITY_PATH
    raw = json.loads(p.read_text())
    caps = {}
    for capability_id, data in raw.get("capabilities", {}).items():
        status = data.get("status", "unsupported")
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid rules capability status for {capability_id}: {status}")
        caps[capability_id] = RuleCapability(
            capability_id=capability_id,
            status=status,
            public_name=data.get("public_name", capability_id.replace("_", " ").title()),
            layer=data.get("layer"),
            notes=data.get("notes"),
        )
    return RulesCapabilityRegistry(
        registry_id=raw.get("registry_id", "UNKNOWN"),
        engine_version=raw.get("engine_version", "unknown"),
        capabilities=caps,
    )


@lru_cache(maxsize=1)
def default_rules_capability_registry() -> RulesCapabilityRegistry:
    return load_rules_capability_registry()


def capability_status(capability_id: str) -> str:
    return default_rules_capability_registry().status(capability_id)
