from dataclasses import dataclass, field
from .maps import Position

@dataclass(slots=True)
class CampaignState:
    campaign_id: str
    system: str
    module: str
    status: str = "setup"
    active_scene_id: str | None = None

@dataclass(slots=True)
class TimeState:
    day: int = 1
    hour: int = 20
    turn: int = 0
    round: int = 0
    segment: int = 0
    mode: str = "setup"
    timers: list[dict[str, object]] = field(default_factory=list)

@dataclass(slots=True)
class CharacterState:
    actor_id: str
    name: str
    actor_type: str
    current_hp: int = 0
    max_hp: int = 0
    ac: int = 10
    level: int = 0
    character_class: str | None = None
    alignment: str | None = None
    movement: int = 12
    location: Position | None = None
    conditions: list[str] = field(default_factory=list)
    inventory: list[str] = field(default_factory=list)
    spells: list[str] = field(default_factory=list)
    damage: str = "1d6"
    status: str = "active"
    team: str = "party"

    @property
    def is_active(self) -> bool:
        return self.status == "active" and self.current_hp > 0

@dataclass(slots=True)
class PartyState:
    party_id: str
    member_ids: list[str] = field(default_factory=list)
    caller_actor_id: str | None = None
    mapper_actor_id: str | None = None
    marching_order: list[str] = field(default_factory=list)
    light_sources: list[dict[str, object]] = field(default_factory=list)

@dataclass(slots=True)
class SceneState:
    scene_id: str
    scene_type: str
    area_id: str
    sub_area_id: str | None = None
    participants: list[str] = field(default_factory=list)
    hazards: list[str] = field(default_factory=list)
    content: dict[str, object] = field(default_factory=dict)

@dataclass(slots=True)
class EncounterState:
    encounter_id: str
    encounter_type: str
    area_id: str
    status: str = "latent"
    participants: list[str] = field(default_factory=list)

@dataclass(slots=True)
class ModuleState:
    module_state_id: str
    entered_areas: list[str] = field(default_factory=list)
    resolved_encounters: list[str] = field(default_factory=list)
    triggered_events: dict[str, bool] = field(default_factory=dict)
    quest_flags: dict[str, object] = field(default_factory=dict)
    world_flags: dict[str, object] = field(default_factory=dict)

@dataclass(slots=True)
class ResourceState:
    owner: str
    resources: dict[str, object] = field(default_factory=dict)
