from __future__ import annotations

from trapspringer.layers.layer8_party.caller import summarize_for_caller
from trapspringer.layers.layer8_party.mapper import mapper_clarification
from trapspringer.layers.layer8_party.personas import build_default_persona_for_actor, display_name_for_actor
from trapspringer.layers.layer8_party.proposals import generate_scene_proposals
from trapspringer.layers.layer8_party.relationships import RelationshipStore
from trapspringer.layers.layer8_party.emotions import EmotionStore
from trapspringer.schemas.party import DiscussionLine, Proposal


STYLE_LINES = {
    "PC_FLINT": "No charging blind. Keep a shield line and make them come to us.",
    "PC_STURM": "Front rank holds. If there is a leader, we challenge him only if he stays.",
    "PC_RAISTLIN": "I will stay behind Caramon. Wake me when there is a target worth a spell.",
    "PC_TASSLEHOFF": "I can get a look at the strange thing before anyone else steps on something awful.",
    "PC_CARAMON": "I stay with Raistlin and hit whatever gets close.",
    "PC_GOLDMOON": "The staff is why these enemies are moving. We should learn who fears it.",
    "NPC_RIVERWIND": "We do not linger where the enemy has chosen the ground.",
}


def event1_opening_discussion(simulated_actor_ids: list[str]) -> list[DiscussionLine]:
    lines = []
    for actor_id in simulated_actor_ids:
        if actor_id in STYLE_LINES:
            lines.append(DiscussionLine(display_name_for_actor(actor_id) + "'s Player", STYLE_LINES[actor_id], tags=["opening_reaction"]))
    return lines[:5]


def build_discussion_from_proposals(proposals: list[Proposal], max_lines: int = 6) -> list[DiscussionLine]:
    lines: list[DiscussionLine] = []
    seen_speakers: set[str] = set()
    for proposal in proposals:
        actor_guess = proposal.player_id.replace("PLY-", "").replace("-SEAT", "").title()
        speaker = actor_guess + "'s Player" if "'s Player" not in actor_guess else actor_guess
        # Keep it from becoming one player monologue unless very high priority.
        if speaker in seen_speakers and proposal.priority < 0.78:
            continue
        seen_speakers.add(speaker)
        channel = "ooc_talk"
        if "mission" in proposal.intent_tags or "guard_goldmoon" in proposal.intent_tags:
            channel = "in_character_speech"
        lines.append(DiscussionLine(speaker, proposal.spoken_text, channel=channel, tags=proposal.intent_tags))
        if len(lines) >= max_lines:
            break
    return lines


def scene_discussion(scene_id: str, simulated_actor_ids: list[str]) -> tuple[list[DiscussionLine], str]:
    proposals = generate_scene_proposals(scene_id, simulated_actor_ids)
    lines = build_discussion_from_proposals(proposals)
    summary = summarize_for_caller(lines, proposals) or "The party holds formation and focuses on immediate threats."
    mapper_question = mapper_clarification(scene_id)
    if mapper_question:
        lines.append(DiscussionLine("Tasslehoff's Player", mapper_question, tags=["mapper", "clarification"]))
    return lines, summary


def discuss_scene(
    scene_id: str,
    simulated_actor_ids: list[str],
    available_public_information: list[str] | None = None,
    user_action: str | None = None,
    relationships: RelationshipStore | None = None,
    emotions: EmotionStore | None = None,
) -> tuple[list[DiscussionLine], str, list[Proposal], list[str]]:
    emotions = emotions or EmotionStore()
    relationships = relationships or RelationshipStore()
    emotions.apply_scene_pressure(simulated_actor_ids, scene_id)
    proposals = generate_scene_proposals(scene_id, simulated_actor_ids, available_public_information, user_action, relationships, emotions)
    lines = build_discussion_from_proposals(proposals)

    dissent: list[str] = []
    # Cautious/risky conflict marker.
    tags = [tag for p in proposals for tag in p.intent_tags]
    if "risk" in tags and "caution" in tags:
        dissent.append("Tasslehoff wants a closer look; Flint wants a guard line before anyone advances.")
    if user_action and ("attack" in user_action.lower() or "charge" in user_action.lower()):
        cautious = [aid for aid in simulated_actor_ids if build_default_persona_for_actor(aid).risk_tolerance < 0.4]
        if cautious:
            dissent.append("The cautious players accept the attack only if the rear stays covered.")

    summary = summarize_for_caller(lines, proposals) or "Caller summary: proceed with caution and keep the party together."
    mapper_question = mapper_clarification(scene_id)
    if mapper_question:
        lines.append(DiscussionLine("Tasslehoff's Player", mapper_question, tags=["mapper", "clarification"]))
    return lines, summary, proposals, dissent
