from __future__ import annotations

from collections import deque
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from trapspringer.schemas.paths import PathPlotRequest, PathPlotResult, PathRecord


class PathPlanner:
    """Layer 9 path planner.

    Enforces the Hourglass movement procedure: every declared destination is
    plotted against current geometry/runtime state before movement happens.
    """

    def __init__(self) -> None:
        self._counter = 0
        self.records: dict[str, PathRecord] = {}

    def _next_id(self, scene_id: str) -> str:
        self._counter += 1
        prefix = str(scene_id).replace("DL1_", "").replace(" ", "_").upper()[:12] or "PATH"
        return f"{prefix}_PATH_{self._counter:04d}"

    def _neighbors(self, graph, zone: str, rules: dict[str, Any]) -> list[str]:
        out: list[str] = []
        secret_ok = bool(rules.get("secret_doors_discovered") or rules.get("allow_secret_doors"))
        doors_blocked = set(rules.get("blocked_doors", []))
        blocked_zones = set(rules.get("blocked_zones", []))
        for conn in getattr(graph, "connections", []):
            a = conn.get("from")
            b = conn.get("to")
            if zone not in {a, b}:
                continue
            if conn.get("blocked", False) or conn.get("passable", True) is False:
                continue
            if conn.get("door_id") in doors_blocked or conn.get("connection_id") in doors_blocked:
                continue
            if conn.get("connection_type") == "secret_door" and not (conn.get("revealed") or conn.get("open") or secret_ok):
                continue
            other = str(b if a == zone else a)
            if other in blocked_zones:
                continue
            out.append(other)
        return out

    def plot_path(self, graph, request: PathPlotRequest | dict[str, Any]) -> PathPlotResult:
        if isinstance(request, dict):
            request = PathPlotRequest(
                actor_id=str(request.get("actor_id") or request.get("actor") or ""),
                scene_id=str(request.get("scene_id") or ""),
                destination_square=request.get("destination_square") or request.get("goal_square") or request.get("destination") or request.get("target_zone"),
                destination_area=request.get("destination_area") or request.get("target_area"),
                allow_diagonal=bool(request.get("allow_diagonal", False)),
                rules=dict(request.get("rules", {})),
            )
        if graph is None:
            return PathPlotResult(False, reason="no_scene_graph")
        start = graph.zone_of(request.actor_id)
        if not start:
            return PathPlotResult(False, reason="missing_origin_square")
        goal = request.destination_square or request.destination_area
        if not goal:
            return PathPlotResult(False, reason="missing_destination")
        goal = str(goal)
        zones = set(getattr(graph, "zones", []))
        if goal not in zones:
            return PathPlotResult(False, reason="unknown_destination", alternatives=sorted(zones))
        if start == goal:
            path_id = self._next_id(request.scene_id)
            rec = PathRecord(
                path_id=path_id,
                path_name=f"From {start.replace('_', ' ').title()} to {goal.replace('_', ' ').title()}",
                start_square=start,
                goal_square=request.destination_square,
                target_area=request.destination_area,
                waypoints=[start],
                rules={"allow_diagonal": request.allow_diagonal, **request.rules},
                created_utc=datetime.now(timezone.utc).isoformat(),
                scene_id=request.scene_id,
                actor_id=request.actor_id,
            )
            self.records[path_id] = rec
            return PathPlotResult(True, rec)

        q: deque[str] = deque([start])
        prev: dict[str, str | None] = {start: None}
        while q:
            cur = q.popleft()
            for nxt in self._neighbors(graph, cur, request.rules):
                if nxt in prev:
                    continue
                prev[nxt] = cur
                if nxt == goal:
                    q.clear()
                    break
                q.append(nxt)
        if goal not in prev:
            return PathPlotResult(False, reason="no_valid_path", alternatives=sorted(self._neighbors(graph, start, request.rules)))
        rev = [goal]
        cur = goal
        while prev[cur] is not None:
            cur = str(prev[cur])
            rev.append(cur)
        waypoints = list(reversed(rev))
        path_id = self._next_id(request.scene_id)
        rec = PathRecord(
            path_id=path_id,
            path_name=f"From {start.replace('_', ' ').title()} to {goal.replace('_', ' ').title()}",
            start_square=start,
            goal_square=request.destination_square,
            target_area=request.destination_area,
            waypoints=waypoints,
            rules={
                "allow_diagonal": request.allow_diagonal,
                "doors_traversable_unless_blocked": True,
                "secret_doors_require_discovery_or_open": True,
                **request.rules,
            },
            created_utc=datetime.now(timezone.utc).isoformat(),
            scene_id=request.scene_id,
            actor_id=request.actor_id,
        )
        self.records[path_id] = rec
        return PathPlotResult(True, rec)

    def get(self, path_id: str) -> PathRecord | None:
        return self.records.get(path_id)

    def movement_audit_payload(self, path: PathRecord) -> dict[str, Any]:
        return path.as_dict()
