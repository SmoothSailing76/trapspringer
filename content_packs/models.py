from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

@dataclass(frozen=True, slots=True)
class ContentPackResource:
    resource_id: str
    kind: str
    path: str
    tags: list[str] = field(default_factory=list)

@dataclass(frozen=True, slots=True)
class ContentPackManifest:
    pack_id: str
    title: str
    version: str
    system: str
    module_id: str | None = None
    root: Path | None = None
    resources: dict[str, ContentPackResource] = field(default_factory=dict)
    entry_scene_id: str | None = None
    main_path_registry: str | None = None
    rules_capabilities: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def resource_path(self, resource_id: str) -> Path:
        if resource_id not in self.resources:
            raise KeyError(f"Unknown content-pack resource: {resource_id}")
        base = self.root or Path(".")
        return (base / self.resources[resource_id].path).resolve()
