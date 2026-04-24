from __future__ import annotations

from typing import Any


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def render_save_list(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No saves found."
    lines = ["Saves:"]
    for row in rows:
        lines.append(
            f"  {row.get('save_id')} | {row.get('label')} | scene={row.get('active_scene_id')} | "
            f"events={row.get('event_count')} | snapshots={row.get('snapshot_count')}"
        )
    return "\n".join(lines)


def render_party_panel(state: dict[str, Any]) -> str:
    party = state.get("party") or {}
    chars = state.get("characters", {}) or {}
    ids = list(_get(party, "member_ids", []) or [])
    lines = ["Party"]
    lines.append(f"  Caller: {_get(party, 'caller_actor_id', 'unknown')}")
    lines.append(f"  Mapper: {_get(party, 'mapper_actor_id', 'unknown')}")
    lines.append("  Members:")
    for aid in ids:
        c = chars.get(aid)
        if c is None:
            lines.append(f"    {aid}: missing")
            continue
        lines.append(
            f"    {aid} | {_get(c, 'name', aid)} | HP {_get(c, 'current_hp', '?')}/{_get(c, 'max_hp', '?')} | "
            f"AC {_get(c, 'ac', '?')} | {_get(c, 'status', '?')}"
        )
    return "\n".join(lines)


def render_map_panel(map_service: Any | None = None, state: dict[str, Any] | None = None) -> str:
    lines = ["Map / Scene"]
    scene = (state or {}).get("scene") if state else None
    if scene:
        lines.append(f"  Active scene: {_get(scene, 'scene_id', 'unknown')} ({_get(scene, 'area_id', 'unknown')})")
    graph = None
    if map_service is not None:
        graphs = getattr(map_service, "scene_graphs", {})
        if graphs:
            graph = graphs[sorted(graphs.keys())[-1]]
    if graph is None:
        lines.append("  No active scene graph.")
    else:
        lines.append("  Zones: " + ", ".join(getattr(graph, "zones", [])))
        positions = getattr(graph, "positions", {})
        if positions:
            lines.append("  Positions:")
            for entity, zone in sorted(positions.items()):
                lines.append(f"    {entity}: {zone}")
    if map_service is not None:
        try:
            public = map_service.public_map_snapshot()
            revealed = sorted(public.get("revealed_areas", []))
            lines.append("  Revealed areas: " + (", ".join(revealed) if revealed else "none"))
            annotations = public.get("player_annotations", [])
            if annotations:
                lines.append("  Notes: " + "; ".join(map(str, annotations)))
        except Exception:
            pass
    return "\n".join(lines)


def render_replay_view(events: list[dict[str, Any]], limit: int = 25, public_only: bool = False) -> str:
    filtered = [e for e in events if (not public_only or e.get("visibility") == "public_table")]
    filtered = filtered[-limit:]
    if not filtered:
        return "No replay events."
    lines = ["Replay Events:"]
    for event in filtered:
        payload = event.get("payload", {})
        summary = payload.get("spoken_text") or payload.get("prompt") or payload.get("event_id") or payload.get("scene_id") or ""
        if not summary and isinstance(payload, dict):
            keys = ", ".join(sorted(payload.keys())[:4])
            summary = f"payload keys: {keys}"
        lines.append(f"  #{int(event.get('sequence', 0)):>3} {event.get('event_type')} [{event.get('visibility')}]: {summary}")
    return "\n".join(lines)
