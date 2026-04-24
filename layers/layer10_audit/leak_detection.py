from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable


DEFAULT_SECRET_TERMS = (
    "dm_private",
    "objective_truth",
    "hidden_feature",
    "secret door",
    "secret passage",
    "exact hp",
    "state_hash",
    "private_outcome",
    "khisanth_defeated",  # should only appear publicly after finale scripting, not in early demos
    "F-AREA4-HIDDEN-BAAZ",
)


@dataclass(slots=True)
class LeakIssue:
    event_id: str
    sequence: int
    term: str
    text: str
    severity: str = "warning"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _event_text(event: dict[str, Any]) -> str:
    payload = event.get("payload", {}) or {}
    chunks: list[str] = []
    for key in ("spoken_text", "prompt", "text", "narration"):
        value = payload.get(key)
        if isinstance(value, str):
            chunks.append(value)
    return "\n".join(chunks)


def scan_public_narration_for_leaks(events: Iterable[dict[str, Any]], secret_terms: Iterable[str] | None = None) -> list[dict[str, Any]]:
    """Lightweight public-log leak scan.

    This intentionally errs on the side of flagging suspicious debug/canon words in
    player-visible narration. It is a hardening tool, not a substitute for Layer 2.
    """
    terms = tuple(t.lower() for t in (secret_terms or DEFAULT_SECRET_TERMS))
    issues: list[LeakIssue] = []
    for event in events:
        if event.get("visibility") not in {"public_table", "actor_private", "subset_private"}:
            continue
        if event.get("event_type") != "narration_event":
            continue
        text = _event_text(event)
        lower = text.lower()
        for term in terms:
            if term and term in lower:
                issues.append(
                    LeakIssue(
                        event_id=str(event.get("event_id", "")),
                        sequence=int(event.get("sequence", -1)),
                        term=term,
                        text=text[:240],
                    )
                )
    return [issue.to_dict() for issue in issues]


def public_event_count(events: Iterable[dict[str, Any]]) -> int:
    return sum(1 for event in events if event.get("visibility") in {"public_table", "actor_private", "subset_private"})
