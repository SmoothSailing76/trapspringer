from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass(slots=True)
class FogCell:
    area_id: str
    state: str = "hidden"  # hidden | seen | explored
    last_seen_turn: int | None = None
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class FogOfWarMap:
    """Runtime public-knowledge overlay for generated maps.

    It intentionally stores reveal state rather than true geometry. True-map data
    stays in Layer 9 true maps; this object is safe to expose in API/public UI
    after optional Layer 2 filtering.
    """

    map_id: str
    cells: dict[str, FogCell] = field(default_factory=dict)

    def reveal(self, area_id: str, state: str = "seen", turn: int | None = None, note: str | None = None) -> FogCell:
        if state not in {"hidden", "seen", "explored"}:
            raise ValueError(f"Invalid fog state: {state}")
        cell = self.cells.get(area_id) or FogCell(area_id=area_id)
        order = {"hidden": 0, "seen": 1, "explored": 2}
        if order[state] >= order.get(cell.state, 0):
            cell.state = state
        cell.last_seen_turn = turn if turn is not None else cell.last_seen_turn
        if note and note not in cell.notes:
            cell.notes.append(note)
        self.cells[area_id] = cell
        return cell

    def hide(self, area_id: str) -> None:
        self.cells[area_id] = FogCell(area_id=area_id, state="hidden")

    def visible_areas(self) -> list[str]:
        return sorted(k for k, v in self.cells.items() if v.state in {"seen", "explored"})

    def explored_areas(self) -> list[str]:
        return sorted(k for k, v in self.cells.items() if v.state == "explored")

    def public_snapshot(self) -> dict[str, Any]:
        return {
            "map_id": self.map_id,
            "visible_areas": self.visible_areas(),
            "explored_areas": self.explored_areas(),
            "cells": {k: asdict(v) for k, v in sorted(self.cells.items()) if v.state != "hidden"},
        }


class FogOfWarStore:
    def __init__(self) -> None:
        self.maps: dict[str, FogOfWarMap] = {}

    def get(self, map_id: str) -> FogOfWarMap:
        if map_id not in self.maps:
            self.maps[map_id] = FogOfWarMap(map_id=map_id)
        return self.maps[map_id]

    def reveal(self, map_id: str, area_id: str, state: str = "seen", turn: int | None = None, note: str | None = None) -> dict[str, Any]:
        cell = self.get(map_id).reveal(area_id, state=state, turn=turn, note=note)
        return {"type": "fog_reveal", "map_id": map_id, "area_id": area_id, "state": cell.state, "notes": list(cell.notes)}
