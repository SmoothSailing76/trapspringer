from __future__ import annotations


class EmotionStore:
    """Tracks temporary table/character emotional state."""

    def __init__(self) -> None:
        self.emotions: dict[str, str] = {}

    def get(self, actor_id: str) -> str:
        return self.emotions.get(actor_id, "focused")

    def set(self, actor_id: str, emotion: str) -> None:
        self.emotions[actor_id] = emotion

    def apply_scene_pressure(self, actor_ids: list[str], scene_id: str) -> None:
        if scene_id == "DL1_AREA_44K":
            for actor_id in actor_ids:
                if actor_id in {"PC_TASSLEHOFF", "PC_STURM"}:
                    self.set(actor_id, "keyed_up")
                elif actor_id == "PC_RAISTLIN":
                    self.set(actor_id, "coldly_alert")
                else:
                    self.set(actor_id, "tense")
        elif scene_id == "DL1_AREA_70K":
            for actor_id in actor_ids:
                self.set(actor_id, "urgent")
        elif scene_id == "DL1_EVENT_2_GOLDMOON":
            for actor_id in actor_ids:
                self.set(actor_id, "curious")

    def table_tone(self, actor_ids: list[str]) -> str:
        values = [self.get(actor_id) for actor_id in actor_ids]
        if "urgent" in values:
            return "urgent"
        if values.count("tense") >= 3:
            return "tense"
        if "curious" in values:
            return "curious"
        return "focused"
