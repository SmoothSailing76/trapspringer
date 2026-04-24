def build_analytics(events: list[dict[str, object]]) -> dict[str, object]:
    return {"event_count": len(events)}
