from __future__ import annotations


class TablePacingController:
    """Controls how much table chatter is surfaced."""

    def __init__(self, max_lines_default: int = 6) -> None:
        self.max_lines_default = max_lines_default
        self.scene_counts: dict[str, int] = {}

    def max_lines_for_scene(self, scene_id: str, urgency: str = "normal") -> int:
        count = self.scene_counts.get(scene_id, 0)
        base = self.max_lines_default
        if urgency in {"urgent", "combat", "escape"}:
            base = 4
        elif urgency in {"sacred", "mystery"}:
            base = 7
        if count >= 2:
            base = max(3, base - 2)
        return base

    def mark_scene_discussed(self, scene_id: str) -> None:
        self.scene_counts[scene_id] = self.scene_counts.get(scene_id, 0) + 1

    def urgency_for_tags(self, tags: list[str] | None = None) -> str:
        tags = tags or []
        if "escape" in tags or "collapse" in tags:
            return "escape"
        if "combat" in tags:
            return "combat"
        if "sacred" in tags:
            return "sacred"
        if "mystery" in tags:
            return "mystery"
        return "normal"
