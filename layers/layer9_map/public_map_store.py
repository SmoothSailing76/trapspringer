from trapspringer.schemas.maps import PublicMap, RevealDiff

class PublicMapStore:
    def __init__(self) -> None:
        self.map = PublicMap(map_id="PUBMAP-PARTY")

    def reveal_area(self, area_id: str) -> dict[str, object] | None:
        if area_id not in self.map.revealed_areas:
            self.map.revealed_areas.append(area_id)
            return {"type": "reveal_area", "area_id": area_id}
        return None

    def reveal_connection(self, from_id: str, to_id: str, label: str | None = None) -> dict[str, object] | None:
        conn = f"{from_id}->{to_id}"
        if conn not in self.map.revealed_connections:
            self.map.revealed_connections.append(conn)
            return {"type": "reveal_connection", "from": from_id, "to": to_id, "label": label or conn}
        return None

    def annotate(self, location: str, note: str) -> dict[str, object]:
        entry = {"location": location, "note": note}
        self.map.player_annotations.append(entry)
        return {"type": "annotation", **entry}

    def apply_diff(self, diff: RevealDiff | dict) -> RevealDiff:
        changes = diff.changes if isinstance(diff, RevealDiff) else list((diff or {}).get("changes", []))
        applied = []
        for change in changes:
            if change.get("type") == "reveal_area":
                out = self.reveal_area(str(change.get("area_id")))
                if out: applied.append(out)
            elif change.get("type") == "reveal_connection":
                out = self.reveal_connection(str(change.get("from")), str(change.get("to")), change.get("label"))
                if out: applied.append(out)
            elif change.get("type") == "annotation":
                applied.append(self.annotate(str(change.get("location")), str(change.get("note"))))
        return RevealDiff(map_diff_id=(diff.map_diff_id if isinstance(diff, RevealDiff) else str((diff or {}).get("map_diff_id", "MAPDIF-APPLIED"))), changes=applied)
