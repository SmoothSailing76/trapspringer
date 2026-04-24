def classify_visibility(fact: dict[str, object], recipient: str) -> str:
    return str(fact.get("visibility_class", "dm_private"))
