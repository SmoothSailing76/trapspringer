from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .models import ContentPackManifest, ContentPackResource

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKS_ROOT = PACKAGE_ROOT / "content_packs"
DEFAULT_PACK_ID = "dl1_dragons_of_despair"

class ContentPackService:
    """Registry/loader for data-driven adventure content packs.

    Content packs keep module/adventure content out of core engine code. A pack
    can point to files bundled inside the pack or to legacy data files while the
    project migrates content incrementally.
    """

    def __init__(self, packs_root: str | Path | None = None) -> None:
        self.packs_root = Path(packs_root) if packs_root is not None else DEFAULT_PACKS_ROOT
        self._manifests: dict[str, ContentPackManifest] = {}

    def discover(self) -> list[ContentPackManifest]:
        manifests: list[ContentPackManifest] = []
        if not self.packs_root.exists():
            return manifests
        for path in sorted(self.packs_root.glob("*/manifest.json")):
            manifests.append(self.load_manifest(path))
        return manifests

    def load_manifest(self, path: str | Path) -> ContentPackManifest:
        p = Path(path)
        raw = json.loads(p.read_text())
        resources = {
            rid: ContentPackResource(
                resource_id=rid,
                kind=data.get("kind", "file"),
                path=data["path"],
                tags=list(data.get("tags", [])),
            )
            for rid, data in raw.get("resources", {}).items()
        }
        manifest = ContentPackManifest(
            pack_id=raw["pack_id"],
            title=raw.get("title", raw["pack_id"]),
            version=raw.get("version", "0.0"),
            system=raw.get("system", "UNKNOWN"),
            module_id=raw.get("module_id"),
            root=p.parent,
            resources=resources,
            entry_scene_id=raw.get("entry_scene_id"),
            main_path_registry=raw.get("main_path_registry"),
            rules_capabilities=raw.get("rules_capabilities"),
            metadata=raw.get("metadata", {}),
        )
        self._manifests[manifest.pack_id] = manifest
        return manifest

    def get(self, pack_id: str) -> ContentPackManifest:
        if pack_id not in self._manifests:
            candidate = self.packs_root / pack_id / "manifest.json"
            if candidate.exists():
                return self.load_manifest(candidate)
            raise KeyError(f"Unknown content pack: {pack_id}")
        return self._manifests[pack_id]

    def load_json_resource(self, pack_id: str, resource_id: str) -> Any:
        manifest = self.get(pack_id)
        path = manifest.resource_path(resource_id)
        return json.loads(path.read_text())

    def list_resources(self, pack_id: str, kind: str | None = None) -> list[ContentPackResource]:
        manifest = self.get(pack_id)
        resources = list(manifest.resources.values())
        if kind is not None:
            resources = [r for r in resources if r.kind == kind]
        return resources


@lru_cache(maxsize=1)
def default_pack() -> ContentPackManifest:
    """Manifest for the active content pack.

    Used by service-layer code that needs to resolve data paths through the
    pack rather than hardcoding relative file locations. Cached for the
    process lifetime; tests that swap packs should call .cache_clear().
    """
    return ContentPackService().get(DEFAULT_PACK_ID)
