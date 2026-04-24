from trapspringer.schemas.maps import RevealDiff


def reveal_area_entry(area_id: str, visible_connections: list[tuple[str, str, str | None]] | None = None) -> RevealDiff:
    changes: list[dict[str, object]] = [{"type": "reveal_area", "area_id": area_id}]
    for from_id, to_id, label in visible_connections or []:
        changes.append({"type": "reveal_connection", "from": from_id, "to": to_id, "label": label or f"{from_id}->{to_id}"})
    return RevealDiff(map_diff_id=f"MAPDIF-{area_id}", changes=changes)


def reveal_hidden_feature(feature) -> RevealDiff:
    changes = []
    if getattr(feature, "area_id", None):
        changes.append({"type": "annotation", "location": feature.area_id, "note": f"Discovered {feature.feature_type}"})
    if getattr(feature, "connects_to", None):
        changes.append({"type": "reveal_connection", "from": feature.area_id, "to": feature.connects_to, "label": feature.feature_id})
    return RevealDiff(map_diff_id=f"MAPDIF-{feature.feature_id}", changes=changes)
