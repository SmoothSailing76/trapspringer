from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class LightSource:
    source_id: str
    carrier_id: str | None
    zone: str
    bright_radius_ft: int = 20
    dim_radius_ft: int = 40
    remaining_turns: int | None = None


@dataclass(frozen=True, slots=True)
class VisibilityTrace:
    observer: str
    target: str
    result: str
    visible: bool
    range_band: str
    light: str
    blockers: list[str]
    reason: str


def distance_band(distance_ft: int | float | None) -> str:
    if distance_ft is None:
        return "unknown"
    if distance_ft <= 10:
        return "adjacent"
    if distance_ft <= 40:
        return "near"
    if distance_ft <= 120:
        return "medium"
    return "far"


def light_at_zone(zone: str, light_sources: list[LightSource]) -> str:
    for src in light_sources:
        if src.zone == zone:
            return "bright"
    # The current v0.7 implementation is zone-based; adjacent-zone light bleed is
    # handled by scene graph LOS and narration, not exact geometry.
    return "dim_or_dark"


def trace_visibility(graph: Any, observer: str, target: str, light_sources: list[LightSource] | None = None, include_concealed: bool = False) -> VisibilityTrace:
    if graph is None:
        return VisibilityTrace(observer, target, "not_visible", False, "unknown", "unknown", [], "no_scene_graph")
    detail = graph.visibility_detail(observer, target, include_concealed=include_concealed)
    oz = graph.zone_of(observer)
    tz = graph.zone_of(target)
    dist = None
    for conn in getattr(graph, "connections", []):
        if {conn.get("from"), conn.get("to")} == {oz, tz}:
            dist = conn.get("distance_ft")
            break
    band = "same_zone" if oz == tz and oz is not None else distance_band(dist)
    light = light_at_zone(tz or "", light_sources or []) if tz else "unknown"
    blockers: list[str] = []
    if detail.get("reason") in {"hidden", "concealed", "blocked_los"}:
        blockers.append(str(detail.get("reason")))
    return VisibilityTrace(
        observer=observer,
        target=target,
        result=str(detail.get("result", "not_visible")),
        visible=bool(detail.get("visible", False)),
        range_band=band,
        light=light,
        blockers=blockers,
        reason=str(detail.get("reason", "unknown")),
    )
