from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

SAVE_SCHEMA_VERSION = "0.2"
ENGINE_VERSION = "0.2.0"

# Save bundles are versioned so older formats can be migrated forward at load
# time. Each migrator takes a bundle at version N and returns a bundle at the
# next version. Add new entries keyed by the *source* version when introducing
# 0.3, 0.4, etc.
_MIGRATIONS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {}


def _migrate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    version = str(bundle.get("save_schema_version", "0.0"))
    while version != SAVE_SCHEMA_VERSION:
        migrator = _MIGRATIONS.get(version)
        if migrator is None:
            raise SaveLoadError(
                f"Cannot migrate save bundle from version {version!r} to {SAVE_SCHEMA_VERSION!r}: "
                f"no migration registered"
            )
        bundle = migrator(bundle)
        new_version = str(bundle.get("save_schema_version", ""))
        if new_version == version:
            raise SaveLoadError(
                f"Migration for {version!r} did not advance save_schema_version"
            )
        version = new_version
    return bundle


def to_plain(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {str(k): to_plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_plain(v) for v in value]
    return value


class SaveLoadError(RuntimeError):
    pass


class SessionPersistenceService:
    """File-backed save/load/export service for v0.2 complete builds."""

    def __init__(self, save_dir: str | Path = "./saves") -> None:
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

    @property
    def index_path(self) -> Path:
        return self.save_dir / "index.json"

    def _load_index(self) -> list[dict[str, Any]]:
        if not self.index_path.exists():
            return []
        try:
            data = json.loads(self.index_path.read_text())
        except Exception as exc:  # pragma: no cover - defensive user-facing path
            raise SaveLoadError(f"Could not read save index: {exc}") from exc
        return data if isinstance(data, list) else []

    def _write_index(self, rows: list[dict[str, Any]]) -> None:
        self.index_path.write_text(json.dumps(rows, indent=2, sort_keys=True))

    def _bundle_path(self, save_id: str) -> Path:
        return self.save_dir / f"{save_id}.json"

    def make_save_id(self, campaign_id: str) -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        safe_campaign = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in campaign_id)
        return f"{safe_campaign}_{stamp}"

    def save_session(self, session: Any, state: dict[str, Any], audit_service: Any, label: str | None = None) -> dict[str, Any]:
        campaign_id = getattr(getattr(session, "context", None), "campaign_id", "campaign")
        save_id = self.make_save_id(str(campaign_id))
        created_at = datetime.now(timezone.utc).isoformat()
        latest_snapshot = audit_service.snapshots.latest() if hasattr(audit_service, "snapshots") else None
        bundle = {
            "format": "trapspringer.session.v2",
            "save_schema_version": SAVE_SCHEMA_VERSION,
            "engine_version": ENGINE_VERSION,
            "save_id": save_id,
            "label": label or "manual_save",
            "created_at": created_at,
            "campaign_id": campaign_id,
            "module_id": getattr(getattr(session, "context", None), "module_id", None),
            "active_scene_id": getattr(getattr(session, "context", None), "active_scene_id", None),
            "current_frame_id": getattr(getattr(session, "context", None), "current_frame_id", None),
            "current_snapshot_id": getattr(getattr(session, "context", None), "current_snapshot_id", None),
            "state": to_plain(state),
            "events": to_plain(getattr(audit_service.event_log, "events", [])),
            "snapshots": to_plain(getattr(audit_service.snapshots, "snapshots", {})),
            "checkpoint_index": to_plain(getattr(audit_service.snapshots, "named", {})),
            "latest_snapshot": to_plain(latest_snapshot),
        }
        path = self._bundle_path(save_id)
        path.write_text(json.dumps(bundle, indent=2, sort_keys=True))
        rows = [r for r in self._load_index() if r.get("save_id") != save_id]
        rows.append({
            "save_id": save_id,
            "label": bundle["label"],
            "created_at": created_at,
            "campaign_id": campaign_id,
            "module_id": bundle["module_id"],
            "active_scene_id": bundle["active_scene_id"],
            "path": str(path),
            "event_count": len(bundle["events"]),
            "snapshot_count": len(bundle["snapshots"]),
            "save_schema_version": SAVE_SCHEMA_VERSION,
            "engine_version": ENGINE_VERSION,
        })
        rows.sort(key=lambda r: str(r.get("created_at", "")), reverse=True)
        self._write_index(rows)
        return rows[0]

    def list_saves(self) -> list[dict[str, Any]]:
        return self._load_index()

    def load_bundle(self, save_id: str) -> dict[str, Any]:
        path = self._bundle_path(save_id)
        if not path.exists():
            raw = Path(save_id)
            if raw.exists():
                path = raw
            else:
                raise FileNotFoundError(save_id)
        try:
            bundle = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            raise SaveLoadError(f"Save file is not valid JSON: {path}") from exc
        except Exception as exc:
            raise SaveLoadError(f"Could not load save file {path}: {exc}") from exc
        if "state" not in bundle or "events" not in bundle:
            raise SaveLoadError(f"Save file is missing required session fields: {path}")
        return _migrate_bundle(bundle)

    def export_session(self, save_id: str, target_path: str | Path) -> Path:
        bundle = self.load_bundle(save_id)
        target = Path(target_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(bundle, indent=2, sort_keys=True))
        return target
