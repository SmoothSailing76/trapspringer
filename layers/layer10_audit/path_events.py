from __future__ import annotations

from trapspringer.schemas.paths import PathRecord


def path_plotted_event(path: PathRecord | dict, visibility: str = "dm_private") -> dict[str, object]:
    payload = path.as_dict() if hasattr(path, "as_dict") else dict(path)
    return {
        "event_type": "path_plotted",
        "source_layer": "layer9",
        "visibility": visibility,
        "payload": payload,
    }


def movement_along_path_event(actor_id: str, path: PathRecord | dict, visibility: str = "public_table") -> dict[str, object]:
    payload = path.as_dict() if hasattr(path, "as_dict") else dict(path)
    payload = {"actor_id": actor_id, "path": payload}
    return {
        "event_type": "movement_along_path",
        "source_layer": "layer6",
        "visibility": visibility,
        "payload": payload,
    }
