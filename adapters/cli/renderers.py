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


def render_v030_spatial_summary(summary: dict[str, object]) -> str:
    lines = [
        "Trapspringer v0.3 Spatial Summary",
        f"Registry: {summary.get('registry_id')}",
        f"Version: {summary.get('version')}",
        f"Content pack: {summary.get('content_pack_id')}",
        "Wilderness sources: " + ", ".join(summary.get("wilderness_sources", [])),
        "Xak Tsaroth levels: " + ", ".join(str(x) for x in summary.get("xak_levels", [])),
        f"Vertical transitions: {summary.get('transition_count')}",
    ]
    policies = summary.get("policies") or {}
    if isinstance(policies, dict):
        lines.append("Runtime policies:")
        for key, value in sorted(policies.items()):
            lines.append(f"  {key}: {value}")
    return "\n".join(lines)
