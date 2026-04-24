from dataclasses import dataclass, field
from .actions import Action

@dataclass(slots=True)
class RevisionGuidance:
    closest_legal_actions: list[str] = field(default_factory=list)
    notes: str | None = None

@dataclass(slots=True)
class ClarificationRequest:
    clarification_prompt: str
    allowed_options: list[str] = field(default_factory=list)

@dataclass(slots=True)
class ValidationRequest:
    validation_id: str
    action: Action
    context: dict[str, object] = field(default_factory=dict)

@dataclass(slots=True)
class ValidationResult:
    validation_id: str
    action_id: str
    status: str
    reason_code: str | None = None
    human_reason: str | None = None
    rule_basis: dict[str, object] = field(default_factory=dict)
    allowed_revisions: list[str] = field(default_factory=list)
    clarification: ClarificationRequest | None = None
    revision_guidance: RevisionGuidance | None = None
