from dataclasses import dataclass, field

@dataclass(slots=True)
class ProcedureFrame:
    frame_id: str
    mode: str = "setup"
    phase: str = "prompt"
    scene_id: str | None = None
    active_actor_order: list[str] = field(default_factory=list)
