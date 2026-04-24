from dataclasses import dataclass, field

@dataclass(slots=True)
class KnowledgeFact:
    fact_id: str
    proposition: str
    truth_status: str = "true"
    visibility_class: str = "dm_private"
    discovered_by: list[str] = field(default_factory=list)
    known_by: list[str] = field(default_factory=list)
    source: str | None = None
    tags: list[str] = field(default_factory=list)
    discovery_conditions: list[str] = field(default_factory=list)

    def is_public(self) -> bool:
        return self.visibility_class in {"public_table", "party_known"}

@dataclass(slots=True)
class BeliefRecord:
    belief_id: str
    actor_id: str
    proposition: str
    belief_state: str
    evidence: list[str] = field(default_factory=list)

@dataclass(slots=True)
class PerceptionEvent:
    perception_id: str
    actor_id: str
    target_fact_id: str
    channel: str
    result: str

@dataclass(slots=True)
class CommunicationEvent:
    communication_id: str
    speaker: str
    listeners: list[str] | str
    content_fact_ids: list[str] = field(default_factory=list)
    mode: str = "speech"
    in_world: bool = True

@dataclass(slots=True)
class KnowledgeQuery:
    query_id: str
    recipient: str
    requested_fact_ids: list[str] = field(default_factory=list)
    actor_id: str | None = None
    context: dict[str, object] = field(default_factory=dict)
