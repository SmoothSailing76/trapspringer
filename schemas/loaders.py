"""Shared load-time validation for JSON resources.

Loaders across the codebase historically did `json.loads(...).get(...)` and
trusted callers to handle missing keys. That pushed errors deep into the
orchestrator. This module gives loader entry points a single helper to
validate shape at the boundary so a typo fails at startup with a useful
file-path + reason.

Validation is intentionally narrow: required-key presence + scalar type
checks. Schemas are not exhaustive — only fields the engine actually reads.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


class ResourceValidationError(ValueError):
    """Raised when a JSON resource is missing required structure."""


def _format_error(path: Path | None, msg: str) -> str:
    if path is not None:
        return f"{path}: {msg}"
    return msg


def require_keys(
    data: Any,
    required: Iterable[str],
    *,
    path: Path | None = None,
    context: str = "resource",
) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ResourceValidationError(
            _format_error(path, f"{context} must be a JSON object, got {type(data).__name__}")
        )
    missing = [k for k in required if k not in data]
    if missing:
        raise ResourceValidationError(
            _format_error(path, f"{context} is missing required field(s): {', '.join(missing)}")
        )
    return data


def require_type(
    data: Any,
    field: str,
    expected: type | tuple[type, ...],
    *,
    path: Path | None = None,
    context: str = "resource",
) -> Any:
    value = data.get(field) if isinstance(data, dict) else None
    if not isinstance(value, expected):
        names = expected.__name__ if isinstance(expected, type) else " or ".join(t.__name__ for t in expected)
        raise ResourceValidationError(
            _format_error(path, f"{context}.{field} must be {names}, got {type(value).__name__}")
        )
    return value


def load_json_object(path: str | Path, *, context: str = "resource") -> dict[str, Any]:
    """Read a JSON file and require it to be an object (not a list/scalar)."""
    p = Path(path)
    try:
        raw = p.read_text()
    except FileNotFoundError as exc:
        raise ResourceValidationError(_format_error(p, "file not found")) from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ResourceValidationError(_format_error(p, f"invalid JSON: {exc.msg} at line {exc.lineno}")) from exc
    if not isinstance(data, dict):
        raise ResourceValidationError(_format_error(p, f"{context} must be a JSON object"))
    return data


_PREGEN_REQUIRED = ("actor_id", "name", "actor_type")
_NPC_REQUIRED = ("actor_id", "name", "actor_type")
_ENCOUNTER_REQUIRED = ("actor_id", "name", "actor_type", "max_hp_values")
_SCENE_REQUIRED = ("scene_id", "type")
_MODULE_MANIFEST_REQUIRED = ("module_id", "start_scene_id", "scene_files")


def load_pregen(path: str | Path) -> dict[str, Any]:
    data = load_json_object(path, context="pregen")
    require_keys(data, _PREGEN_REQUIRED, path=Path(path), context="pregen")
    return data


def load_npc(path: str | Path) -> dict[str, Any]:
    data = load_json_object(path, context="npc")
    require_keys(data, _NPC_REQUIRED, path=Path(path), context="npc")
    return data


def load_encounter(path: str | Path) -> dict[str, Any]:
    data = load_json_object(path, context="encounter")
    require_keys(data, _ENCOUNTER_REQUIRED, path=Path(path), context="encounter")
    if not isinstance(data["max_hp_values"], list) or not data["max_hp_values"]:
        raise ResourceValidationError(
            _format_error(Path(path), "encounter.max_hp_values must be a non-empty list")
        )
    return data


def load_scene(path: str | Path) -> dict[str, Any]:
    data = load_json_object(path, context="scene")
    require_keys(data, _SCENE_REQUIRED, path=Path(path), context="scene")
    return data


def load_module_manifest(path: str | Path) -> dict[str, Any]:
    data = load_json_object(path, context="module_manifest")
    require_keys(data, _MODULE_MANIFEST_REQUIRED, path=Path(path), context="module_manifest")
    if not isinstance(data["scene_files"], dict):
        raise ResourceValidationError(
            _format_error(Path(path), "module_manifest.scene_files must be an object")
        )
    return data
