from dataclasses import dataclass, field

@dataclass(slots=True)
class RuntimeSceneGraph:
    scene_id: str
    template_id: str
    zones: list[str]
    connections: list[dict[str, object]]
    line_of_sight: dict[str, list[str]]
    positions: dict[str, str] = field(default_factory=dict)
    hidden_entities: set[str] = field(default_factory=set)
    concealed_entities: set[str] = field(default_factory=set)
    revealed_entities: set[str] = field(default_factory=set)
    discovered_zones: set[str] = field(default_factory=set)

    def place(self, entity_id: str, zone: str, hidden: bool = False, concealed: bool = False) -> None:
        if zone not in self.zones:
            raise ValueError(f"Unknown zone: {zone}")
        self.positions[entity_id] = zone
        if hidden:
            self.hidden_entities.add(entity_id)
        else:
            self.hidden_entities.discard(entity_id)
        if concealed:
            self.concealed_entities.add(entity_id)
        else:
            self.concealed_entities.discard(entity_id)

    def zone_of(self, entity_id: str) -> str | None:
        return self.positions.get(entity_id)

    def reveal_entity(self, entity_id: str) -> None:
        self.hidden_entities.discard(entity_id)
        self.concealed_entities.discard(entity_id)
        self.revealed_entities.add(entity_id)

    def conceal_entity(self, entity_id: str) -> None:
        self.concealed_entities.add(entity_id)

    def hide_entity(self, entity_id: str) -> None:
        self.hidden_entities.add(entity_id)

    def is_hidden_from_public(self, entity_id: str) -> bool:
        return entity_id in self.hidden_entities or entity_id in self.concealed_entities

    def can_see(self, observer: str, target: str, include_concealed: bool = False) -> bool:
        oz = self.zone_of(observer)
        tz = self.zone_of(target)
        if oz is None or tz is None:
            return False
        if target in self.hidden_entities:
            return False
        if target in self.concealed_entities and not include_concealed:
            return False
        return oz == tz or tz in self.line_of_sight.get(oz, [])

    def visibility_detail(self, observer: str, target: str, include_concealed: bool = False) -> dict[str, object]:
        oz = self.zone_of(observer)
        tz = self.zone_of(target)
        if oz is None or tz is None:
            return {"visible": False, "result": "not_visible", "reason": "missing_position"}
        if target in self.hidden_entities:
            return {"visible": False, "result": "not_visible", "reason": "hidden"}
        if target in self.concealed_entities and not include_concealed:
            return {"visible": False, "result": "concealed", "reason": "concealed"}
        if oz == tz or tz in self.line_of_sight.get(oz, []):
            return {"visible": True, "result": "fully_visible", "reason": "line_of_sight"}
        return {"visible": False, "result": "not_visible", "reason": "blocked_los"}

    def reachable(self, actor: str, target_zone: str) -> bool:
        az = self.zone_of(actor)
        if az is None:
            return False
        if az == target_zone:
            return True
        return any(
            c.get("passable", True) and ((c.get("from") == az and c.get("to") == target_zone) or (c.get("to") == az and c.get("from") == target_zone))
            for c in self.connections
        )

    def reveal_zone(self, zone: str) -> None:
        if zone in self.zones:
            self.discovered_zones.add(zone)

# v1.0.2 Hourglass movement helpers. Bound as methods below so older
# serialized scene graph objects remain compatible.
def _move_along_path(self, entity_id: str, waypoints: list[str]) -> None:
    if not waypoints:
        raise ValueError("Path has no waypoints")
    for zone in waypoints:
        if zone not in self.zones:
            raise ValueError(f"Unknown path waypoint: {zone}")
    self.positions[entity_id] = waypoints[-1]


def _connected_neighbors(self, zone: str, include_secret: bool = False) -> list[str]:
    out: list[str] = []
    for conn in self.connections:
        if conn.get("passable", True) is False or conn.get("blocked", False):
            continue
        if conn.get("connection_type") == "secret_door" and not (include_secret or conn.get("revealed") or conn.get("open")):
            continue
        if conn.get("from") == zone:
            out.append(str(conn.get("to")))
        elif conn.get("to") == zone:
            out.append(str(conn.get("from")))
    return out

RuntimeSceneGraph.move_along_path = _move_along_path
RuntimeSceneGraph.connected_neighbors = _connected_neighbors
