from __future__ import annotations

from trapspringer.layers.layer8_party.convergence import converge_plan
from trapspringer.layers.layer8_party.declarations import build_default_combat_declarations, build_scene_declarations_from_proposals
from trapspringer.layers.layer8_party.discussion import discuss_scene, event1_opening_discussion, scene_discussion
from trapspringer.layers.layer8_party.emotions import EmotionStore
from trapspringer.layers.layer8_party.mapper import update_mapper_notes
from trapspringer.layers.layer8_party.personas import build_default_character_persona, build_default_persona_for_actor
from trapspringer.layers.layer8_party.relationships import RelationshipStore
from trapspringer.layers.layer8_party.seats import build_initial_seat_registry
from trapspringer.schemas.party import PartyDiscussionBundle


class PartySimulationService:
    def __init__(self) -> None:
        self.seats = {}
        self.player_personas = {}
        self.character_personas = {}
        self.relationships = RelationshipStore()
        self.emotions = EmotionStore()
        self.last_discussion: PartyDiscussionBundle | None = None

    def initialize_seats(self, user_character_id: str | None, active_party_ids: list[str]):
        self.seats = build_initial_seat_registry(user_character_id, active_party_ids)
        self._load_personas(active_party_ids)
        return self.seats

    def refresh_for_party(self, user_character_id: str | None, active_party_ids: list[str]):
        self.seats = build_initial_seat_registry(user_character_id, active_party_ids)
        self._load_personas(active_party_ids)
        return self.seats

    def _load_personas(self, active_party_ids: list[str]) -> None:
        self.player_personas = {actor_id: build_default_persona_for_actor(actor_id) for actor_id in active_party_ids}
        self.character_personas = {actor_id: build_default_character_persona(actor_id) for actor_id in active_party_ids}

    def _simulated_actor_ids(self) -> list[str]:
        return [seat.character_id for seat in self.seats.values() if not seat.is_human_user]

    def simulate_discussion(self, request: dict | None = None) -> PartyDiscussionBundle:
        request = request or {}
        state = request.get("state", {})
        scene_id = request.get("scene_id") or (state.get("scene").scene_id if state.get("scene") else "DL1_EVENT_1_AMBUSH")
        actor_ids = self._simulated_actor_ids()
        public_info = request.get("available_public_information", [])
        user_action = request.get("user_action")

        if scene_id == "DL1_EVENT_1_AMBUSH" and not user_action:
            bundle = PartyDiscussionBundle(
                discussion=event1_opening_discussion(actor_ids),
                caller_summary="The party holds formation and focuses on the hobgoblins as Toede flees.",
                emotional_tone=self.emotions.table_tone(actor_ids),
            )
            self.last_discussion = bundle
            return bundle

        lines, summary, proposals, dissent = discuss_scene(
            scene_id,
            actor_ids,
            available_public_information=public_info,
            user_action=user_action,
            relationships=self.relationships,
            emotions=self.emotions,
        )
        converged_summary, convergence_dissent = converge_plan(proposals)
        mapper_notes = update_mapper_notes({"scene_id": scene_id, "available_public_information": public_info})
        bundle = PartyDiscussionBundle(
            discussion=lines,
            caller_summary=converged_summary or summary,
            proposals=proposals,
            dissent=dissent + convergence_dissent,
            mapper_notes=mapper_notes,
            emotional_tone=self.emotions.table_tone(actor_ids),
        )
        self.last_discussion = bundle
        return bundle

    def generate_declarations(self, request: dict | None = None):
        request = request or {}
        scene_id = request.get("scene_id") or "DL1_EVENT_1_AMBUSH"
        actor_ids = self._simulated_actor_ids()
        # Combat remains compatible with earlier waves.
        if scene_id == "DL1_EVENT_1_AMBUSH" or request.get("mode") == "combat":
            return build_default_combat_declarations(actor_ids)
        proposals = self.last_discussion.proposals if self.last_discussion else []
        return build_scene_declarations_from_proposals(scene_id, actor_ids, proposals)

    def react_to_user_action(self, user_action: str, scene_id: str | None = None) -> PartyDiscussionBundle:
        return self.simulate_discussion({"scene_id": scene_id or "DL1_EVENT_1_AMBUSH", "user_action": user_action})

    def update_after_scene_event(self, event_tag: str) -> None:
        self.relationships.nudge_after_event(event_tag)
        if event_tag == "khisanth_surface":
            self.emotions.apply_scene_pressure(self._simulated_actor_ids(), "DL1_AREA_44K")
