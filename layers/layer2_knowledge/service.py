from trapspringer.layers.layer2_knowledge.beliefs import BeliefStore
from trapspringer.layers.layer2_knowledge.facts import FactStore
from trapspringer.layers.layer2_knowledge.models import KnowledgeDiff, KnowledgeResult
from trapspringer.layers.layer2_knowledge.recipient_filters import filter_facts
from trapspringer.layers.layer2_knowledge.discovery import apply_discovery_to_fact
from trapspringer.layers.layer2_knowledge.propagation import propagate
from trapspringer.schemas.knowledge import KnowledgeFact

class KnowledgeService:
    def __init__(self) -> None:
        self.facts = FactStore()
        self.beliefs = BeliefStore()
        self._seed_core_facts()

    def _seed_core_facts(self) -> None:
        self.facts.ensure(
            "F-EVENT1-AMBUSHERS",
            "Hobgoblins have emerged from both sides of the road and surrounded the party.",
            visibility_class="public_table",
            known_by=["PARTY", "public_table"],
            source="DL1_EVENT_1",
        )
        self.facts.ensure(
            "F-TOEDE-FLEES",
            "Fewmaster Toede has no intention of granting mercy and flees after ordering the attack.",
            visibility_class="dm_private",
            source="DL1_EVENT_1",
        )
        self.facts.ensure(
            "F-AREA4-DRACONIAN-AMBUSH",
            "Baaz draconians are concealed in the trees in area 4 awaiting a horn warning.",
            visibility_class="dm_private",
            source="DL1_AREA_4",
            discovery_conditions=["climb_tree", "spot_hidden_draconians"],
        )

    def add_fact(self, fact: KnowledgeFact | dict) -> KnowledgeFact:
        if isinstance(fact, dict):
            fact = KnowledgeFact(**fact)
        return self.facts.add(fact)

    def filter_for_recipient(self, query) -> KnowledgeResult:
        actor_id = getattr(query, "actor_id", None) or (getattr(query, "context", {}) or {}).get("actor_id") if query is not None else None
        requested = getattr(query, "requested_fact_ids", []) if query is not None else []
        recipient = getattr(query, "recipient", "all_players") if query is not None else "all_players"
        facts = [self.facts.facts[fid] for fid in requested if fid in self.facts.facts] if requested else self.facts.all()
        return KnowledgeResult(status="ok", facts=filter_facts(facts, recipient, actor_id))

    def apply_discovery(self, effect: dict[str, object]) -> KnowledgeDiff:
        fact_id = str(effect.get("fact_id"))
        proposition = str(effect.get("proposition", fact_id))
        fact = self.facts.get(fact_id) or self.facts.ensure(fact_id, proposition, visibility_class=str(effect.get("visibility_before", "dm_private")))
        discovered_by = effect.get("discovered_by", effect.get("recipient", "PARTY"))
        visibility_after = str(effect.get("visibility_after", "party_known"))
        apply_discovery_to_fact(fact, discovered_by, visibility_after=visibility_after)
        return KnowledgeDiff(status="ok", changes=[{"fact_id": fact_id, "known_by": fact.known_by, "visibility_after": fact.visibility_class}])

    def propagate_communication(self, event: dict[str, object]) -> KnowledgeDiff:
        return KnowledgeDiff(status="ok", changes=propagate(self.facts, event))
