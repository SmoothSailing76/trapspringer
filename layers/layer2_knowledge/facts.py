from trapspringer.schemas.knowledge import KnowledgeFact

class FactStore:
    def __init__(self) -> None:
        self.facts: dict[str, KnowledgeFact] = {}

    def add(self, fact: KnowledgeFact) -> KnowledgeFact:
        self.facts[fact.fact_id] = fact
        return fact

    def get(self, fact_id: str) -> KnowledgeFact | None:
        return self.facts.get(fact_id)

    def ensure(self, fact_id: str, proposition: str, visibility_class: str = "dm_private", **kwargs) -> KnowledgeFact:
        if fact_id in self.facts:
            return self.facts[fact_id]
        return self.add(KnowledgeFact(fact_id=fact_id, proposition=proposition, visibility_class=visibility_class, **kwargs))

    def mark_known(self, fact_id: str, recipient: str) -> KnowledgeFact | None:
        fact = self.get(fact_id)
        if not fact:
            return None
        if recipient not in fact.known_by:
            fact.known_by.append(recipient)
        if recipient not in fact.discovered_by:
            fact.discovered_by.append(recipient)
        if recipient in {"PARTY", "all_players", "public_table"}:
            fact.visibility_class = "party_known"
        return fact

    def all(self) -> list[KnowledgeFact]:
        return list(self.facts.values())
