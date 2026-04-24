from __future__ import annotations


class MapperState:
    """Persistent mapper state with deterministic, bounded fallibility."""

    def __init__(self, mapper_id: str = "PC_TASSLEHOFF", fallible: bool = True) -> None:
        self.mapper_id = mapper_id
        self.fallible = fallible
        self.notes: list[dict[str, object]] = []
        self.corrections: list[dict[str, object]] = []

    def add_note(self, scene_id: str, note: str, confidence: str = "medium", possible_error: str | None = None) -> dict[str, object]:
        entry = {"mapper": self.mapper_id, "scene_id": scene_id, "note": note, "confidence": confidence}
        if possible_error and self.fallible:
            entry["possible_error"] = possible_error
        self.notes.append(entry)
        return entry

    def correct(self, scene_id: str, correction: str) -> dict[str, object]:
        entry = {"mapper": self.mapper_id, "scene_id": scene_id, "correction": correction}
        self.corrections.append(entry)
        return entry

    def latest_for_scene(self, scene_id: str) -> list[dict[str, object]]:
        return [note for note in self.notes if note.get("scene_id") == scene_id]


def update_mapper_notes(request) -> list[dict[str, object]]:
    scene_id = (request or {}).get("scene_id", "")
    public_info = set((request or {}).get("available_public_information", []))
    state: MapperState | None = (request or {}).get("mapper_state")
    notes: list[dict[str, object]] = []

    def note(text: str, confidence: str = "medium", possible_error: str | None = None) -> None:
        if state is not None:
            notes.append(state.add_note(scene_id, text, confidence, possible_error))
        else:
            entry = {"mapper": "PC_TASSLEHOFF", "scene_id": scene_id, "note": text, "confidence": confidence}
            if possible_error:
                entry["possible_error"] = possible_error
            notes.append(entry)

    if scene_id == "DL1_AREA_44K":
        note("Large plaza; well in center; temple to north.", "high")
    elif scene_id == "DL1_AREA_44F":
        note("Camp with huts and dragon-shaped structure near fire.", "medium", "distance and firelight may distort exact hut spacing")
    elif scene_id == "DL1_AREA_46B_MISHAKAL_FORM":
        note("Sacred chamber; record exits only after audience resolves.", "medium")
    elif scene_id == "DL1_AREA_70K":
        note("Dragon court is large and irregular; mark exits only after visual confirmation.", "low", "collapse and treasure piles make precise scale unreliable")
    elif "visible_exits" in public_info:
        note("Marks visible exits only; hidden routes not assumed.", "medium")
    return notes


def mapper_clarification(scene_id: str) -> str | None:
    if scene_id == "DL1_AREA_44K":
        return "Mapper asks: is the temple directly north of the well, or offset?"
    if scene_id == "DL1_AREA_70K":
        return "Mapper asks: do we have a clear route back out, or is the lair geometry too broken to trust?"
    return None
