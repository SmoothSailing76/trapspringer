from __future__ import annotations

from typing import Any


def render_public_map_snapshot(snapshot: dict[str, Any]) -> str:
    lines = [f"Public Map: {snapshot.get('map_id', 'unknown')}"]
    visible = snapshot.get("visible_areas", [])
    explored = snapshot.get("explored_areas", [])
    lines.append("Visible: " + (", ".join(visible) if visible else "none"))
    lines.append("Explored: " + (", ".join(explored) if explored else "none"))
    cells = snapshot.get("cells", {})
    for area_id, cell in sorted(cells.items()):
        notes = "; ".join(cell.get("notes", []))
        suffix = f" — {notes}" if notes else ""
        lines.append(f"- {area_id}: {cell.get('state')}{suffix}")
    return "\n".join(lines)


def render_visibility_trace(trace: dict[str, Any]) -> str:
    return (
        f"{trace.get('observer')} -> {trace.get('target')}: "
        f"{trace.get('result')} | range={trace.get('range_band')} | "
        f"light={trace.get('light')} | reason={trace.get('reason')}"
    )
