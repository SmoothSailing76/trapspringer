from dataclasses import dataclass, field

@dataclass(slots=True)
class CanonQuery:
    query_id: str
    question: str
    domain: str
    context: dict[str, object] = field(default_factory=dict)

@dataclass(slots=True)
class AuthorityTrace:
    selected_source: str | None = None
    domain: str | None = None
    precedence_reason: str | None = None

@dataclass(slots=True)
class CanonAnswer:
    query_id: str
    status: str
    answer: str | None = None
    authority_trace: AuthorityTrace = field(default_factory=AuthorityTrace)
    citations: list[dict[str, str]] = field(default_factory=list)
    requires_ruling: bool = False

@dataclass(slots=True)
class RulingRecord:
    ruling_id: str
    title: str
    decision: str
    basis: str
