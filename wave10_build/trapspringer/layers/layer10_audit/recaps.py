from __future__ import annotations

from typing import Any


def recap_round(events: list[dict[str, Any]], limit: int | None = None) -> str:
    selected = events[-limit:] if limit else events
    lines: list[str] = []
    for event in selected:
        etype = event.get("event_type")
        payload = event.get("payload", {}) or {}
        if etype == "narration_event":
            text = payload.get("spoken_text")
            if text:
                lines.append(str(text))
        elif etype == "roll_event":
            roll = payload.get("roll", payload)
            purpose = roll.get("purpose", "roll") if isinstance(roll, dict) else "roll"
            total = roll.get("total") if isinstance(roll, dict) else None
            lines.append(f"Roll {purpose}: {total}.")
    return "\n".join(lines[-8:]) or "No recap events recorded yet."
