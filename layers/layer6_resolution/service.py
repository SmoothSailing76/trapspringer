from __future__ import annotations

from trapspringer.schemas.resolution import ResolutionRequest, ResolutionResult, PublicOutcome, PrivateOutcome
from trapspringer.services.random_service import RandomService
from trapspringer.layers.layer6_resolution.combat import resolve_melee_attack, resolve_move, resolve_wait, resolve_missile_attack, resolve_initiative, resolve_surprise
from trapspringer.layers.layer6_resolution.spells import resolve_spell
from trapspringer.layers.layer6_resolution import module_scripts as scripts
from trapspringer.layers.layer6_resolution.path_movement import resolve_move_along_path
from trapspringer.layers.layer6_resolution.open_ended import resolve_open_ended_intent


class ResolutionService:
    def __init__(self, rng: RandomService | None = None) -> None:
        self.rng = rng or RandomService(seed=1)

    def resolve(self, request: ResolutionRequest) -> ResolutionResult:
        action = request.payload.get("action")
        state = request.payload.get("state", {})
        map_service = request.payload.get("map_service")
        if action is None:
            return ResolutionResult(request.resolution_id, "no_effect", public_outcome=PublicOutcome("No action resolved."))
        if action.action_type == "melee_attack":
            return resolve_melee_attack(action, state, self.rng)
        if action.action_type == "missile_attack":
            return resolve_missile_attack(action, state, self.rng)
        if action.action_type == "cast_spell":
            return resolve_spell({"actor_id": action.actor_id, "target_id": action.target.id if action.target else None, "spell": action.extra.get("spell") or action.method}, state, self.rng)
        if action.action_type == "move":
            path = action.extra.get("path")
            if path is None and map_service is not None and action.extra.get("path_id"):
                path = map_service.get_path(str(action.extra.get("path_id")))
            return resolve_move_along_path(action, state, map_service, path)
        if action.action_type == "wait":
            return resolve_wait(action, state, self.rng)
        return ResolutionResult(request.resolution_id, "no_effect", PrivateOutcome({"unknown_action": action.action_type}))

    def resolve_initiative(self) -> dict:
        return resolve_initiative(self.rng)

    def resolve_surprise(self, side: str = "party", threshold: int = 2):
        return resolve_surprise(side, self.rng, threshold)

    def resolve_spell_effect(self, request: dict, state: dict | None = None) -> ResolutionResult:
        return resolve_spell(request, state or request.get("state", {}), self.rng)

    def resolve_toede_escape(self, state: dict, map_service=None) -> ResolutionResult:
        return scripts.resolve_toede_escape(state, map_service)

    def resolve_event2_join(self, state: dict) -> ResolutionResult:
        return scripts.resolve_event2_join(state)

    def resolve_inspect_wicker_dragon(self, state: dict, actor_id: str = "PC_TASSLEHOFF") -> ResolutionResult:
        return scripts.resolve_inspect_wicker_dragon(state, actor_id)

    def resolve_khisanth_surface_arrival(self, state: dict) -> ResolutionResult:
        return scripts.resolve_khisanth_surface_arrival(state)

    def resolve_mishakal_audience_and_recharge(self, state: dict) -> ResolutionResult:
        return scripts.resolve_mishakal_audience_and_recharge(state)

    def resolve_descent_started(self, state: dict) -> ResolutionResult:
        return scripts.resolve_descent_started(state)

    def resolve_lower_city_route_discovery(self, state: dict) -> ResolutionResult:
        return scripts.resolve_lower_city_route_discovery(state)

    def resolve_dragon_lair_finale(self, state: dict, breaker: str = "PC_GOLDMOON") -> ResolutionResult:
        return scripts.resolve_dragon_lair_finale(state, breaker=breaker)

    def resolve_collapse_escape_and_epilogue(self, state: dict, breaker: str = "PC_GOLDMOON") -> ResolutionResult:
        return scripts.resolve_collapse_escape_and_epilogue(state, breaker=breaker)

# v0.5 facade extension: bind as an instance method without disturbing the
# existing v0.4 class body above.
def _v050_resolve_open_ended_intent(self, intent, state: dict) -> ResolutionResult:
    return resolve_open_ended_intent(intent, state)

ResolutionService.resolve_open_ended_intent = _v050_resolve_open_ended_intent
