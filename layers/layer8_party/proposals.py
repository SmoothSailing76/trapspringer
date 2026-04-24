from __future__ import annotations

from trapspringer.layers.layer8_party.personas import build_default_character_persona, build_default_persona_for_actor, display_name_for_actor
from trapspringer.layers.layer8_party.relationships import RelationshipStore
from trapspringer.layers.layer8_party.emotions import EmotionStore
from trapspringer.schemas.party import Proposal


def _proposal(actor_id: str, kind: str, text: str, priority: float, tags: list[str], action_hint: dict | None = None) -> Proposal:
    return Proposal(
        proposal_id=f"PROP-{actor_id}-{kind}".replace(" ", "_"),
        player_id=f"PLY-{display_name_for_actor(actor_id).upper()}-SEAT",
        kind=kind,
        spoken_text=text,
        priority=priority,
        intent_tags=tags,
        action_hint=action_hint or {},
    )


def generate_scene_proposals(
    scene_id: str,
    actor_ids: list[str],
    available_public_information: list[str] | None = None,
    user_action: str | None = None,
    relationships: RelationshipStore | None = None,
    emotions: EmotionStore | None = None,
) -> list[Proposal]:
    public = set(available_public_information or [])
    relationships = relationships or RelationshipStore()
    emotions = emotions or EmotionStore()
    proposals: list[Proposal] = []

    for actor_id in actor_ids:
        pp = build_default_persona_for_actor(actor_id)
        cp = build_default_character_persona(actor_id)
        emotion = emotions.get(actor_id)
        rel_notes = relationships.summary_for(actor_id)
        priority = 0.45 + (pp.assertiveness * 0.25) + (pp.tactical_focus * 0.15)

        if scene_id == "DL1_COLLAPSE_ESCAPE":
            if actor_id in {"PC_TANIS", "PC_STURM"}:
                proposals.append(_proposal(actor_id, "escape_coordination", "Move now. Front and rear guards keep the wounded between you; no one stops for loose coins.", 0.92, ["escape", "collapse", "caller"], {"action_type": "move", "target": "exit_route"}))
            elif actor_id == "PC_TASSLEHOFF":
                proposals.append(_proposal(actor_id, "escape_route_memory", "I remember the way back enough to run it, but nobody let me get distracted by side passages.", 0.80, ["escape", "route", "memory"], {"action_type": "guide"}))
            else:
                proposals.append(_proposal(actor_id, "escape_support", "I keep moving and help whoever stumbles.", 0.70, ["escape", "support"], {"action_type": "move"}))
            continue

        if scene_id == "DL1_AREA_46B_MISHAKAL_FORM" and actor_id in {"PC_GOLDMOON", "NPC_RIVERWIND"}:
            proposals.append(_proposal(actor_id, "sacred_pause", "This is not a place for clever tricks. Let the staff-bearer listen first.", 0.84, ["sacred", "staff", "mission"], {"action_type": "listen"}))
            continue

        if scene_id == "DL1_AREA_70K" and actor_id in {"PC_RAISTLIN", "PC_FLINT"}:
            proposals.append(_proposal(actor_id, "lair_caution", "This is the lair. Mark the exits, keep spread out, and do not assume the treasure is safe ground.", 0.86, ["dragon", "caution", "secret_route"], {"action_type": "guard"}))
            continue

        if actor_id == "PC_TASSLEHOFF":
            if scene_id == "DL1_AREA_44F" and "wicker_truth_known" not in public:
                proposals.append(_proposal(actor_id, "risky_scouting", "I can creep close enough to see whether that dragon thing is breathing. Probably.", 0.82, ["scout", "inspect_structure", "risk"], {"action_type": "inspect", "target": "dragon_structure"}))
            elif scene_id == "DL1_AREA_44K":
                proposals.append(_proposal(actor_id, "curious_probe", "I vote we do not stand right at the big terrible well, but I can peek around the columns.", 0.70, ["scout", "avoid_well", "columns"], {"action_type": "move", "target": "columns"}))
            else:
                proposals.append(_proposal(actor_id, "curious_option", "I can take a quick look before everyone stomps in.", 0.60, ["scout", "curiosity"]))
        elif actor_id == "PC_FLINT":
            proposals.append(_proposal(actor_id, "caution_warning", "Slow down. Shields up, eyes on the dark corners, and nobody touches anything that looks important.", 0.74, ["caution", "hold_formation", "guard"], {"action_type": "wait"}))
        elif actor_id == "PC_STURM":
            proposals.append(_proposal(actor_id, "front_rank_plan", "Front rank holds. If something comes out, it meets steel before it reaches the staff.", 0.76, ["front_rank", "protect_staff", "melee"], {"action_type": "guard"}))
        elif actor_id == "PC_CARAMON":
            text = "I stay near Raistlin and hit whatever gets past the front."
            if "protective_of:PC_RAISTLIN" in rel_notes:
                text = "I am not leaving Raistlin exposed. I hold close and smash anything that reaches him."
            proposals.append(_proposal(actor_id, "protective_position", text, 0.68, ["protect_raistlin", "melee", "rear_guard"], {"action_type": "guard", "target": "PC_RAISTLIN"}))
        elif actor_id == "PC_RAISTLIN":
            if scene_id == "DL1_AREA_44K":
                proposals.append(_proposal(actor_id, "rules_caution", "Open ground, a deep shaft, and a temple. Choose cover before curiosity gets us killed.", 0.71, ["seek_cover", "analyze", "avoid_open_ground"], {"action_type": "move", "target": "cover"}))
            else:
                proposals.append(_proposal(actor_id, "conserve_power", "Do not ask me to waste a spell on a problem a sword can solve.", 0.58, ["conserve_spells", "stay_back"], {"action_type": "wait"}))
        elif actor_id == "PC_GOLDMOON":
            proposals.append(_proposal(actor_id, "mission_focus", "The staff brought us here for a reason. We should be careful, but not turn back from the path.", 0.72, ["mission", "staff", "advance_quest"], {"action_type": "advance_carefully"}))
        elif actor_id == "NPC_RIVERWIND":
            proposals.append(_proposal(actor_id, "watchful_guard", "We move only with a way out behind us.", 0.66, ["guard_goldmoon", "escape_route", "caution"], {"action_type": "guard", "target": "PC_GOLDMOON"}))
        else:
            proposals.append(_proposal(actor_id, "cooperate", "I follow the caller's plan.", priority, ["cooperate"]))

        # User action reaction adds social texture without overriding user agency.
        if user_action and pp.talkativeness > 0.5:
            lowered = user_action.lower()
            if "charge" in lowered or "attack" in lowered:
                if cp.caution > 0.65:
                    proposals.append(_proposal(actor_id, "object_user_risk", f"{display_name_for_actor(actor_id)}'s player winces: 'That is bold. Can we at least keep a rear guard?'", 0.50, ["react_to_user", "caution"]))
                elif cp.courage > 0.75:
                    proposals.append(_proposal(actor_id, "support_user_attack", "If you go in, I go in beside you.", 0.55, ["react_to_user", "support_attack"]))
        if emotion == "urgent":
            proposals[-1].priority = min(1.0, proposals[-1].priority + 0.08)

    return sorted(proposals, key=lambda p: p.priority, reverse=True)
