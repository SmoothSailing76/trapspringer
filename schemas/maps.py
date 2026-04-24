from dataclasses import dataclass, field

@dataclass(slots=True)
class Position:
    area_id: str
    sub_area_id: str | None = None
    zone: str | None = None
    x: int | None = None
    y: int | None = None
    z: int | None = None
    hidden: bool = False
    concealed: bool = False

@dataclass(slots=True)
class MapConnection:
    connection_id: str
    from_id: str
    to_id: str
    connection_type: str
    passable: bool = True
    hidden: bool = False
    revealed: bool = False

@dataclass(slots=True)
class HiddenFeature:
    feature_id: str
    feature_type: str
    area_id: str
    zone: str | None = None
    connects_to: str | None = None
    discovered: bool = False
    discovery_conditions: list[str] = field(default_factory=list)

@dataclass(slots=True)
class HazardFootprint:
    hazard_id: str
    hazard_type: str
    area_id: str
    zone: str | None = None
    radius_ft: int | None = None
    visibility: str = "dm_private"

@dataclass(slots=True)
class VisibilityField:
    observer: str
    target: str
    result: str
    reason: str | None = None

@dataclass(slots=True)
class TrueMap:
    map_id: str
    areas: list[dict[str, object]] = field(default_factory=list)
    connections: list[MapConnection] = field(default_factory=list)
    hidden_features: list[HiddenFeature] = field(default_factory=list)
    hazards: list[HazardFootprint] = field(default_factory=list)

@dataclass(slots=True)
class PublicMap:
    map_id: str
    revealed_areas: list[str] = field(default_factory=list)
    revealed_connections: list[str] = field(default_factory=list)
    player_annotations: list[dict[str, object]] = field(default_factory=list)
    uncertain_features: list[dict[str, object]] = field(default_factory=list)

@dataclass(slots=True)
class SceneGraph:
    scene_id: str
    nodes: list[str] = field(default_factory=list)
    edges: list[dict[str, object]] = field(default_factory=list)

@dataclass(slots=True)
class RevealDiff:
    map_diff_id: str
    changes: list[dict[str, object]] = field(default_factory=list)
