from trapspringer.schemas.knowledge import KnowledgeFact


def apply_discovery_to_fact(fact: KnowledgeFact, discovered_by: list[str] | str, visibility_after: str | None = None) -> KnowledgeFact:
    recipients = [discovered_by] if isinstance(discovered_by, str) else list(discovered_by)
    for recipient in recipients:
        if recipient not in fact.discovered_by:
            fact.discovered_by.append(recipient)
        if recipient not in fact.known_by:
            fact.known_by.append(recipient)
    if visibility_after:
        fact.visibility_class = visibility_after
    elif any(r in {"PARTY", "all_players", "public_table"} for r in recipients):
        fact.visibility_class = "party_known"
    return fact
