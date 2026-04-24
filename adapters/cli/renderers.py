from __future__ import annotations

from trapspringer.engine.orchestrator import EngineTurnResult


def render_turn_result(result: EngineTurnResult) -> str:
    parts: list[str] = []
    if result.discussion:
        parts.append("Table talk:")
        parts.extend(f"  {line}" for line in result.discussion)
    if result.narration:
        parts.append(result.narration)
    if result.prompt:
        parts.append(result.prompt)
    return "\n".join(parts)


def render_status(status: dict[str, object]) -> str:
    lines = [
        "Trapspringer DL1 Status",
        f"Milestone: {status.get('milestone_label')} ({status.get('milestone_id')})",
        f"Scene: {status.get('scene_id')}",
        f"Staff: {status.get('staff')}",
        f"Disks recovered: {status.get('disks_recovered')}",
        f"Khisanth: {status.get('khisanth')}",
        f"Checkpoint: {status.get('checkpoint')}",
        f"Party active: {status.get('party_active')}",
    ]
    snapshots = status.get("snapshots") or {}
    if isinstance(snapshots, dict) and snapshots:
        lines.append("Checkpoints:")
        for label in sorted(snapshots):
            lines.append(f"  {label}: {snapshots[label]}")
    return "\n".join(lines)
