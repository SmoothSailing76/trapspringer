from dataclasses import dataclass, field

@dataclass(slots=True)
class PromptBundle:
    prompt_text: str
    metadata: dict[str, object] = field(default_factory=dict)

@dataclass(slots=True)
class DialogueBundle:
    speaker: str
    spoken_text: str
    metadata: dict[str, object] = field(default_factory=dict)

@dataclass(slots=True)
class NarrationRequest:
    narration_id: str
    mode: str
    recipient: str
    scene_id: str | None = None
    public_outcome: dict[str, object] = field(default_factory=dict)
    prompt_needed: bool = False
    tone: str | None = None

@dataclass(slots=True)
class NarrationResult:
    narration_id: str
    spoken_text: str
    prompt: str | None = None
    ui_annotations: list[str] = field(default_factory=list)
