def classify_question(question: str, domain_hint: str | None = None) -> str:
    if domain_hint:
        return domain_hint
    q = question.lower()
    if "area" in q or "room" in q or "event" in q:
        return "module_content"
    if "spell" in q or "attack" in q or "save" in q:
        return "core_rules"
    return "adjudication"
