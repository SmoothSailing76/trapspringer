from dataclasses import dataclass, field
from .actions import Action

@dataclass(slots=True)
class Declaration:
    declaration_id: str
    actor_id: str
    spoken_text: str
    action: Action
    revision_of: str | None = None

@dataclass(slots=True)
class CallerSummary:
    caller_id: str | None
    summary_text: str

@dataclass(slots=True)
class RevisionLink:
    prior_declaration_id: str
    next_declaration_id: str

@dataclass(slots=True)
class DeclarationSet:
    declarations: list[Declaration] = field(default_factory=list)
    caller_summary: CallerSummary | None = None
