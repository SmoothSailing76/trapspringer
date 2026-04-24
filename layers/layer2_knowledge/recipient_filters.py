from trapspringer.schemas.knowledge import KnowledgeFact

PUBLIC_RECIPIENTS = {"all_players", "public_table", "party", "PARTY"}
DM_RECIPIENTS = {"dm", "dm_runtime", "debug", "dm_private"}

def _allowed(fact: KnowledgeFact, recipient: str, actor_id: str | None = None) -> bool:
    if recipient in DM_RECIPIENTS:
        return True
    if fact.visibility_class in {"public_table", "party_known"}:
        return True
    if recipient in PUBLIC_RECIPIENTS and ("PARTY" in fact.known_by or "public_table" in fact.known_by):
        return True
    if actor_id and actor_id in fact.known_by:
        return True
    if recipient in fact.known_by:
        return True
    return False

def filter_facts(facts: list[KnowledgeFact], recipient: str, actor_id: str | None = None) -> list[KnowledgeFact]:
    return [fact for fact in facts if _allowed(fact, recipient, actor_id)]
