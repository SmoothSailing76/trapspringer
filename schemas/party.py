from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PlayerPersona:
    persona_id: str
    talkativeness: float = 0.5
    assertiveness: float = 0.5
    rules_mastery: float = 0.5
    risk_tolerance: float = 0.5
    tactical_focus: float = 0.5
    roleplay_focus: float = 0.5
    memory_reliability: float = 0.75
    cooperativeness: float = 0.7
    meta_restraint: float = 0.7
    humor_level: float = 0.2
    conflict_tolerance: float = 0.4
    deference_to_caller: float = 0.65
    spotlight_seeking: float = 0.4
    attachment_to_character_safety: float = 0.55
    attachment_to_loot: float = 0.35
    attachment_to_mission: float = 0.65
    archetype: str = "balanced_player"


@dataclass(slots=True)
class CharacterPersona:
    persona_id: str
    temperament: list[str] = field(default_factory=list)
    core_goals: list[str] = field(default_factory=list)
    preferred_actions: list[str] = field(default_factory=list)
    social_style: str = "plainspoken"
    courage: float = 0.6
    caution: float = 0.5
    curiosity: float = 0.5
    mercy: float = 0.5
    discipline: float = 0.5
    protectiveness: float = 0.5
    willingness_to_retreat: float = 0.4


@dataclass(slots=True)
class PlayerAgent:
    player_id: str
    display_name: str
    character_id: str
    player_persona_id: str
    character_persona_id: str
    is_human_user: bool = False
    table_roles: list[str] = field(default_factory=list)
    engagement_state: str = "active"
    last_contribution_turn: int = 0


@dataclass(slots=True)
class Proposal:
    proposal_id: str
    player_id: str
    kind: str
    spoken_text: str
    priority: float = 0.5
    intent_tags: list[str] = field(default_factory=list)
    action_hint: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DiscussionLine:
    speaker: str
    text: str
    channel: str = "ooc_talk"
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PartyDiscussionBundle:
    discussion: list[DiscussionLine] = field(default_factory=list)
    caller_summary: str | None = None
    declarations: list[dict[str, object]] = field(default_factory=list)
    proposals: list[Proposal] = field(default_factory=list)
    dissent: list[str] = field(default_factory=list)
    mapper_notes: list[dict[str, object]] = field(default_factory=list)
    emotional_tone: str = "focused"
    caller_state: dict[str, object] = field(default_factory=dict)
    memory_state: dict[str, object] = field(default_factory=dict)
