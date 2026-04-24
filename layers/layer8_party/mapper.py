from __future__ import annotations


def update_mapper_notes(request) -> list[dict[str, object]]:
    scene_id = (request or {}).get("scene_id", "")
    public_info = set((request or {}).get("available_public_information", []))
    notes: list[dict[str, object]] = []
    if scene_id == "DL1_AREA_44K":
        notes.append({"mapper": "PC_TASSLEHOFF", "note": "Large plaza; well in center; temple to north.", "confidence": "high"})
    elif scene_id == "DL1_AREA_44F":
        notes.append({"mapper": "PC_TASSLEHOFF", "note": "Camp with huts and dragon-shaped structure near fire.", "confidence": "medium"})
    elif "visible_exits" in public_info:
        notes.append({"mapper": "PC_TASSLEHOFF", "note": "Marks visible exits only; hidden routes not assumed.", "confidence": "medium"})
    return notes


def mapper_clarification(scene_id: str) -> str | None:
    if scene_id == "DL1_AREA_44K":
        return "Mapper asks: is the temple directly north of the well, or offset?"
    return None
