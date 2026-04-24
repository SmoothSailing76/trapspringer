from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DL1_MAP_ROOT = PACKAGE_ROOT / "data" / "maps" / "dl1"


@dataclass(frozen=True, slots=True)
class SpatialAssetRef:
    asset_id: str
    path: str
    status: str = "available"


class DL1SpatialRegistry:
    """Loader for v0.3 DL1 spatial assets.

    This class intentionally treats uploaded DM maps as true-map sources and
    leaves public map generation to Layer 9 runtime reveal logic.
    """

    def __init__(self, registry_path: str | Path | None = None) -> None:
        self.registry_path = Path(registry_path) if registry_path else DL1_MAP_ROOT / "spatial_registry_v030.json"
        self.registry = self._load_json(self.registry_path)

    def _load_json(self, path: str | Path) -> dict[str, Any]:
        return json.loads(Path(path).read_text())

    def asset_path(self, key: str) -> Path:
        rel = self.registry["assets"][key]
        return DL1_MAP_ROOT / rel

    def load_wilderness_manifest(self) -> dict[str, Any]:
        return self._load_json(self.asset_path("wilderness"))

    def load_xak_stack_manifest(self) -> dict[str, Any]:
        return self._load_json(self.asset_path("xak_tsaroth"))

    def load_xak_transitions(self) -> dict[str, Any]:
        return self._load_json(self.asset_path("xak_tsaroth_transitions"))

    def load_xak_level(self, level: int) -> dict[str, Any]:
        if level not in {1, 2, 3, 4}:
            raise ValueError(f"Xak Tsaroth level must be 1-4, got {level!r}")
        return self._load_json(DL1_MAP_ROOT / "xak_tsaroth" / "levels" / f"level{level}_true_map.json")

    def level_summary(self) -> list[dict[str, Any]]:
        stack = self.load_xak_stack_manifest()
        return list(stack.get("levels", []))

    def spatial_summary(self) -> dict[str, Any]:
        wilderness = self.load_wilderness_manifest()
        stack = self.load_xak_stack_manifest()
        transitions = self.load_xak_transitions()
        return {
            "registry_id": self.registry.get("registry_id"),
            "version": self.registry.get("version"),
            "content_pack_id": self.registry.get("content_pack_id"),
            "wilderness_sources": list(wilderness.get("source_images", {}).keys()),
            "xak_levels": [entry["level"] for entry in stack.get("levels", [])],
            "transition_count": len(transitions.get("known_transitions", [])),
            "policies": self.registry.get("runtime_policy", {}),
        }

    def level4_area_index(self) -> dict[str, dict[str, Any]]:
        level4 = self.load_xak_level(4)
        return {
            str(area["area_id"]): area
            for area in level4.get("encounter_areas", [])
            if area.get("area_id")
        }

    def validate_assets_present(self) -> dict[str, Any]:
        missing: list[str] = []
        checked: list[str] = []
        for key, rel in self.registry.get("assets", {}).items():
            path = DL1_MAP_ROOT / rel
            checked.append(str(path.relative_to(PACKAGE_ROOT)))
            if not path.exists():
                missing.append(str(path.relative_to(PACKAGE_ROOT)))
        for level in [1, 2, 3, 4]:
            path = DL1_MAP_ROOT / "xak_tsaroth" / "levels" / f"level{level}_true_map.json"
            checked.append(str(path.relative_to(PACKAGE_ROOT)))
            if not path.exists():
                missing.append(str(path.relative_to(PACKAGE_ROOT)))
        return {"ok": not missing, "checked": checked, "missing": missing}
