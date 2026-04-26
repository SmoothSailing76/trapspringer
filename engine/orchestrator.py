from dataclasses import dataclass, field, asdict, is_dataclass
from typing import Any

from trapspringer.engine.lifecycle import LifecycleManager
from trapspringer.engine.runtime import RuntimeSession
from trapspringer.engine.ids import IdService
from trapspringer.layers.layer1_authority.service import AuthorityService
from trapspringer.layers.layer2_knowledge.service import KnowledgeService
from trapspringer.layers.layer3_state.service import StateService
from trapspringer.layers.layer4_procedure.service import ProcedureService
from trapspringer.layers.layer5_validation.service import ValidationService
from trapspringer.layers.layer5_validation.parser import parse_user_declaration
from trapspringer.layers.layer6_resolution.service import ResolutionService
from trapspringer.layers.layer7_narration.service import NarrationService
from trapspringer.layers.layer8_party.service import PartySimulationService
from trapspringer.layers.layer9_map.service import MapVisibilityService
from trapspringer.layers.layer10_audit.service import AuditReplayService
from trapspringer.schemas.actions import Action, ActionContext, ActionTarget
from trapspringer.schemas.declarations import Declaration, DeclarationSet
from trapspringer.schemas.validation import ValidationRequest
from trapspringer.schemas.resolution import ResolutionRequest, ResolutionResult


def _plain(obj):
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, dict):
        return {k: _plain(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_plain(v) for v in obj]
    return obj

@dataclass(slots=True)
class EngineTurnResult:
    narration: str | None = None
    prompt: str | None = None
    events: list[dict[str, Any]] = field(default_factory=list)
    discussion: list[str] = field(default_factory=list)
    validations: list[dict[str, Any]] = field(default_factory=list)
    resolutions: list[dict[str, Any]] = field(default_factory=list)

class Orchestrator:
    """Master runtime coordinator for the Event 1 vertical slice."""

    def __init__(self) -> None:
        self.ids = IdService()
        self.lifecycle = LifecycleManager()
        self.layer1 = AuthorityService()
        self.layer2 = KnowledgeService()
        self.layer3 = StateService()
        self.layer4 = ProcedureService()
        self.layer5 = ValidationService()
        self.layer6 = ResolutionService()
        self.layer7 = NarrationService()
        self.layer8 = PartySimulationService()
        self.layer9 = MapVisibilityService()
        self.layer10 = AuditReplayService()

    def _services(self) -> dict[str, object]:
        return {"authority": self.layer1, "knowledge": self.layer2, "state": self.layer3, "procedure": self.layer4, "validation": self.layer5, "resolution": self.layer6, "narration": self.layer7, "party": self.layer8, "map": self.layer9, "audit": self.layer10}

    def start_campaign(self, campaign_id: str = "DL1-CAMPAIGN-001", user_character_id: str | None = None) -> RuntimeSession:
        return self.lifecycle.bootstrap_dl1_campaign(campaign_id, services=self._services(), user_character_id=user_character_id)

    def _user_actor_id(self) -> str:
        for seat in self.layer8.seats.values():
            if seat.is_human_user:
                return seat.character_id
        return "PC_TANIS"

    def _append(self, event_type: str, source_layer: str, payload: dict[str, Any], visibility: str = "public_table") -> None:
        self.layer10.append_event_from_dict({"event_id": self.ids.next("EVT"), "event_type": event_type, "source_layer": source_layer, "visibility": visibility, "payload": _plain(payload)})

    def _log_roll_events_from_resolution(self, result: ResolutionResult) -> None:
        summary = getattr(result.private_outcome, "summary", {}) or {}
        for key in ("attack_roll", "damage_roll"):
            roll = summary.get(key)
            if roll:
                self._append("roll_event", "random_service", {"roll": roll, "resolution_id": result.resolution_id}, visibility=str(roll.get("visibility", "dm_private")))

    def _enemy_declarations(self, state: dict) -> list[Declaration]:
        active_party = [aid for aid, c in state["characters"].items() if getattr(c, "team", None) == "party" and getattr(c, "is_active", False)]
        if not active_party:
            return []
        target_cycle = active_party
        declarations: list[Declaration] = []
        ctx = ActionContext(mode="combat", phase="declaration", scene_id="DL1_EVENT_1_AMBUSH")
        enemies = [aid for aid, c in state["characters"].items() if getattr(c, "team", None) == "enemy" and getattr(c, "is_active", False) and aid != "NPC_TOEDE"]
        for idx, enemy_id in enumerate(enemies, start=1):
            target_id = target_cycle[(idx - 1) % len(target_cycle)]
            action = Action(f"ACT-ENEMY-{idx:02d}", enemy_id, "melee_attack", ctx, target=ActionTarget("actor", target_id), spoken_text=f"{enemy_id} attacks {target_id}.")
            declarations.append(Declaration(f"DEC-ENEMY-{idx:02d}", enemy_id, action.spoken_text or "", action))
        return declarations

    def _combat_round(self, user_input: str) -> EngineTurnResult:
        state = self.layer3.read_state()
        discussion_bundle = self.layer8.simulate_discussion({"state": state})
        sim_decls = self.layer8.generate_declarations({"state": state})
        user_decl = parse_user_declaration(user_input, self._user_actor_id(), action_id=self.ids.next("ACT"), mode="combat")
        all_decls = DeclarationSet(declarations=[user_decl] + list(sim_decls.declarations), caller_summary=sim_decls.caller_summary)
        self._append("party_discussion", "layer8", {"lines": discussion_bundle.discussion, "caller_summary": discussion_bundle.caller_summary})
        self._append("declaration_event", "layer4", {"declarations": all_decls.declarations})

        # Toede's scripted exit occurs before normal round resolution.
        toede_result = self.layer6.resolve_toede_escape(state, self.layer9)
        toede_commit = self.layer3.commit_mutations(toede_result.state_mutations)
        self._append("resolution_event", "layer6", {"resolution": toede_result}, visibility="dm_private")
        if toede_result.state_mutations:
            self._append("state_mutation_event", "layer3", {"commit": toede_commit}, visibility="dm_private")
        self._log_roll_events_from_resolution(toede_result)

        validation_context = {"mode": "combat", "phase": "declaration", "state": state, "map_service": self.layer9}
        validations = []
        valid_decls: list[Declaration] = []
        for decl in all_decls.declarations:
            vr = self.layer5.validate_action(ValidationRequest(self.ids.next("VAL"), decl.action, validation_context))
            validations.append(vr)
            if vr.status == "valid":
                valid_decls.append(decl)
            else:
                self._append("validation_event", "layer5", {"validation": vr})
                narration = self.layer7.narrate_invalid_action(vr)
                self._append("narration_event", "layer7", {"spoken_text": narration.spoken_text, "prompt": narration.prompt})
                return EngineTurnResult(narration=narration.spoken_text, prompt=narration.prompt, events=self.layer10.event_log.events, validations=[_plain(v) for v in validations])
        self._append("validation_event", "layer5", {"validations": validations})

        # Add enemy attacks after party declarations are validated.
        enemy_decls = self._enemy_declarations(state)
        valid_decls.extend(enemy_decls)

        self.layer4.open_combat("DL1_EVENT_1_AMBUSH", [d.actor_id for d in valid_decls])
        self.layer4.lock_declarations(DeclarationSet(valid_decls))

        results: list[ResolutionResult] = [toede_result]
        for decl in valid_decls:
            req = ResolutionRequest(self.ids.next("RES"), decl.action.action_id, decl.actor_id, "DL1_EVENT_1_AMBUSH", "combat", {"action": decl.action, "state": state, "map_service": self.layer9})
            result = self.layer6.resolve(req)
            commit = self.layer3.commit_mutations(result.state_mutations)
            results.append(result)
            self._append("resolution_event", "layer6", {"resolution": result}, visibility="dm_private")
            self._log_roll_events_from_resolution(result)
            if result.state_mutations:
                self._append("state_mutation_event", "layer3", {"commit": commit}, visibility="dm_private")

        active_enemies = self.layer3.active_enemies()
        # Toede is fled, so active enemies list should not include him after status mutation.
        combat_done = len(active_enemies) == 0
        self.layer4.end_combat_if_done(active_enemies)
        narration = self.layer7.narrate_combat_results(results, round_no=state["time"].round, combat_done=combat_done)
        round_commit = self.layer3.commit_mutations([{"path": "time.round", "value": state["time"].round + 1}])
        self._append("state_mutation_event", "layer3", {"commit": round_commit}, visibility="dm_private")
        self._append("narration_event", "layer7", {"spoken_text": narration.spoken_text, "prompt": narration.prompt})
        snap_id = self.layer10.create_snapshot(f"after_round_{state['time'].round}", state=state)
        self._append("recap_event", "layer10", {"text": self.layer10.recap(limit=12), "snapshot_id": snap_id}, visibility="public_table")
        return EngineTurnResult(narration=narration.spoken_text, prompt=narration.prompt, events=self.layer10.event_log.events, discussion=[l.text for l in discussion_bundle.discussion], validations=[_plain(v) for v in validations], resolutions=[_plain(r) for r in results])


    def _commit_resolution_result(self, result: ResolutionResult, source_layer: str = "layer6") -> None:
        commit = self.layer3.commit_mutations(result.state_mutations)
        self._append("resolution_event", source_layer, {"resolution": result}, visibility="dm_private")
        if result.state_mutations:
            self._append("state_mutation_event", "layer3", {"commit": commit}, visibility="dm_private")
        for effect in result.knowledge_effects:
            diff = self.layer2.apply_discovery(effect)
            self._append("knowledge_event", "layer2", {"effect": effect, "diff": diff}, visibility="dm_private")

    def transition_to_scene(self, scene_id: str) -> EngineTurnResult:
        """Wave 6: move the runtime into a scripted DL1 scene beyond Event 1."""
        scene = self.layer3.transition_to_scene(scene_id)
        state = self.layer3.read_state()
        graph = self.layer9.setup_scene_from_content(scene.content, list(state["party"].member_ids), scene_id=scene_id)
        mode = scene.scene_type if scene.scene_type else "exploration"
        self.layer4.switch_mode({"to_mode": mode, "reason": f"transition_to_{scene_id}"})
        # Keep frame scene aligned even when switch_mode is generic.
        self.layer4._frame.scene_id = scene_id
        self.layer4._frame.phase = "scene_entry"
        self._append("procedure_event", "layer4", {"to_scene": scene_id, "mode": mode})
        self._append("map_mutation_event", "layer9", {"scene_id": scene_id, "zones": graph.zones})
        narration = self.layer7.prompt_scene(self.layer4.current_frame(), scene.content)
        self._append("narration_event", "layer7", {"spoken_text": narration.spoken_text, "prompt": narration.prompt})
        self.layer10.create_snapshot(f"entered_{scene_id}", state=state)
        return EngineTurnResult(narration=narration.spoken_text, prompt=narration.prompt, events=self.layer10.event_log.events)

    def trigger_event2_goldmoon(self) -> EngineTurnResult:
        result = self.transition_to_scene("DL1_EVENT_2_GOLDMOON")
        state = self.layer3.read_state()
        join_result = self.layer6.resolve_event2_join(state)
        self._commit_resolution_result(join_result)
        # Add joined actors to party state using the state service helper after flags/status update.
        self.layer3.add_actor_to_party("PC_GOLDMOON")
        self.layer3.add_actor_to_party("NPC_RIVERWIND")
        self.layer8.refresh_for_party(self._user_actor_id(), list(self.layer3.read_state()["party"].member_ids))
        narration = self.layer7.narrate_resolution(join_result, prompt="Goldmoon and Riverwind are with you. Continue toward Xak Tsaroth?")
        self._append("narration_event", "layer7", {"spoken_text": narration.spoken_text, "prompt": narration.prompt})
        return EngineTurnResult(narration=(result.narration + "\n\n" + narration.spoken_text), prompt=narration.prompt, events=self.layer10.event_log.events)

    def inspect_wicker_dragon(self, actor_id: str | None = None) -> EngineTurnResult:
        state = self.layer3.read_state()
        actor_id = actor_id or self._user_actor_id()
        result = self.layer6.resolve_inspect_wicker_dragon(state, actor_id=actor_id)
        self._commit_resolution_result(result)
        try:
            self.layer9.reveal_feature("DL1_AREA_44F", "F-44F-WICKER-DRAGON")
        except Exception:
            pass
        narration = self.layer7.narrate_resolution(result, prompt="The camp remains before you. What do you do next?")
        self._append("narration_event", "layer7", {"spoken_text": narration.spoken_text, "prompt": narration.prompt})
        return EngineTurnResult(narration=narration.spoken_text, prompt=narration.prompt, events=self.layer10.event_log.events)

    def trigger_khisanth_surface(self) -> EngineTurnResult:
        state = self.layer3.read_state()
        result = self.layer6.resolve_khisanth_surface_arrival(state)
        self._commit_resolution_result(result)
        narration = self.layer7.narrate_resolution(result, prompt="Khisanth wheels above the plaza. Declare immediate actions.")
        self._append("narration_event", "layer7", {"spoken_text": narration.spoken_text, "prompt": narration.prompt})
        return EngineTurnResult(narration=narration.spoken_text, prompt=narration.prompt, events=self.layer10.event_log.events)

    def run_wave6_story_demo(self, session: RuntimeSession) -> list[EngineTurnResult]:
        """A small deterministic content path: Event 2 -> 44f discovery -> 44k dragon reveal."""
        outputs = []
        outputs.append(self.trigger_event2_goldmoon())
        outputs.append(self.transition_to_scene("DL1_AREA_44F"))
        outputs.append(self.inspect_wicker_dragon("PC_TASSLEHOFF"))
        outputs.append(self.transition_to_scene("DL1_AREA_44K"))
        outputs.append(self.trigger_khisanth_surface())
        return outputs


    def _transition_and_script(self, scene_id: str, script_name: str | None = None, prompt: str | None = None) -> EngineTurnResult:
        opening = self.transition_to_scene(scene_id)
        if script_name is None:
            return opening
        state = self.layer3.read_state()
        resolver = getattr(self.layer6, script_name)
        result = resolver(state)
        self._commit_resolution_result(result)
        narration = self.layer7.narrate_resolution(result, prompt=prompt or "Continue.")
        self._append("narration_event", "layer7", {"spoken_text": narration.spoken_text, "prompt": narration.prompt})
        self.layer10.create_snapshot(scene_id.lower(), state=self.layer3.read_state())
        return EngineTurnResult(narration=(opening.narration + "\n\n" + narration.spoken_text), prompt=narration.prompt, events=self.layer10.event_log.events)

    def _main_path_registry(self):
        from trapspringer.layers.layer4_procedure.transitions import load_main_path_registry
        return load_main_path_registry()

    def _advance_milestone(self, milestone_id: str) -> None:
        from trapspringer.layers.layer4_procedure.transitions import validate_main_path_transition, apply_milestone_flags
        registry = self._main_path_registry()
        state = self.layer3.read_state()
        module = state["module"]
        current = str(module.world_flags.get("current_milestone") or "start_of_event_1")
        ok, reason = validate_main_path_transition(current, milestone_id, registry, module)
        if not ok:
            raise RuntimeError(reason)
        flags = apply_milestone_flags(milestone_id, registry, module)
        self._append("module_event", "orchestrator", {"event": "milestone_reached", "milestone_id": milestone_id, "flags_set": flags}, visibility="dm_private")
        if registry[milestone_id].checkpoint:
            self.layer10.create_snapshot(milestone_id, state=self.layer3.read_state(), milestone_id=milestone_id)

    def main_path_status(self) -> dict[str, object]:
        registry = self._main_path_registry()
        state = self.layer3.read_state()
        module = state["module"]
        milestone_id = str(module.world_flags.get("current_milestone") or "start_of_event_1")
        milestone = registry.get(milestone_id)
        q = module.quest_flags
        w = module.world_flags
        return {
            "milestone_id": milestone_id,
            "milestone_label": milestone.label if milestone else milestone_id,
            "scene_id": state["campaign"].active_scene_id,
            "staff": "shattered" if q.get("staff_shattered") else ("recharged" if q.get("staff_recharged_at_mishakal") or w.get("staff_recharged") else ("in party" if q.get("staff_in_party_possession") or w.get("staff_in_party_possession") else "not in party")),
            "disks_recovered": bool(q.get("disks_recovered") or w.get("disks_recovered")),
            "khisanth": "defeated" if q.get("khisanth_defeated") or w.get("khisanth_defeated") else ("seen" if w.get("khisanth_surface_seen") else "unseen"),
            "checkpoint": milestone_id if milestone_id in self.layer10.checkpoint_ids() else None,
            "party_active": len(self.layer3.active_party_members()),
            "snapshots": self.layer10.checkpoint_ids(),
        }

    def run_v020_main_path_demo(self, session: RuntimeSession) -> list[EngineTurnResult]:
        """v0.2.0 complete: deterministic playable DL1 main-path spine.

        Event 1 is expected to have been opened/resolved before this is called.
        Each main milestone is advanced through the registry, applies stable flags,
        and creates a named checkpoint for save/load and replay verification.
        """
        outputs: list[EngineTurnResult] = []
        self._advance_milestone("after_event_1")

        outputs.append(self.trigger_event2_goldmoon())
        self._advance_milestone("goldmoon_joined")

        self._advance_milestone("arrival_xak_tsaroth")
        outputs.append(self.transition_to_scene("DL1_AREA_44F"))
        outputs.append(self.inspect_wicker_dragon("PC_TASSLEHOFF"))
        self._advance_milestone("after_44f")

        outputs.append(self.transition_to_scene("DL1_AREA_44K"))
        outputs.append(self.trigger_khisanth_surface())
        self._advance_milestone("after_44k_surface")

        self._advance_milestone("temple_mishakal")
        outputs.append(self._transition_and_script("DL1_TEMPLE_MISHAKAL", "resolve_mishakal_audience_and_recharge", "The staff is restored. Descend below the temple?"))
        self._advance_milestone("staff_recharged")

        outputs.append(self._transition_and_script("DL1_DESCENT", "resolve_descent_started", "The lower city waits below. Continue?"))
        self._advance_milestone("descent_started")

        outputs.append(self.transition_to_scene("DL1_LOWER_CITY"))
        self._advance_milestone("lower_city")
        state = self.layer3.read_state()
        route_result = self.layer6.resolve_lower_city_route_discovery(state)
        self._commit_resolution_result(route_result)
        route_narr = self.layer7.narrate_resolution(route_result, prompt="The route to the lair is known. Enter 70k?")
        self._append("narration_event", "layer7", {"spoken_text": route_narr.spoken_text, "prompt": route_narr.prompt})
        outputs.append(EngineTurnResult(narration=route_narr.spoken_text, prompt=route_narr.prompt, events=self.layer10.event_log.events))
        self._advance_milestone("secret_route_known")
        self._advance_milestone("before_70k")

        outputs.append(self._transition_and_script("DL1_DRAGON_LAIR_70K", "resolve_dragon_lair_finale", "The cavern is collapsing. Escape!"))
        self._advance_milestone("staff_shattered")
        self._advance_milestone("collapse_escape")

        outputs.append(self._transition_and_script("DL1_COLLAPSE_EPILOGUE", "resolve_collapse_escape_and_epilogue", "The quest of DL1 is complete."))
        self._advance_milestone("epilogue_complete")
        self._append("module_event", "orchestrator", {"event": "v0.2.0_main_path_complete", "snapshots": list(self.layer10.snapshots.snapshots.keys()), "checkpoints": self.layer10.checkpoint_ids()})
        return outputs

    def step(self, session: RuntimeSession, user_input: str | None = None) -> EngineTurnResult:
        frame = self.layer4.current_frame()
        state = self.layer3.read_state()
        if user_input is None:
            narration = self.layer7.prompt_scene(frame, state["scene"].content)
            self._append("narration_event", "layer7", {"spoken_text": narration.spoken_text, "prompt": narration.prompt})
            return EngineTurnResult(narration=narration.spoken_text, prompt=narration.prompt, events=self.layer10.event_log.events)
        self._append("input_received", "orchestrator", {"user_input": user_input})
        return self._combat_round(user_input)

# ---- v0.5 open-ended interaction extension ---------------------------------
def _v050_handle_open_ended_action(self, text: str, actor_id: str | None = None) -> EngineTurnResult:
    from trapspringer.layers.layer4_procedure.open_ended import classify_open_ended_intent, open_ended_policy_response

    actor_id = actor_id or self._user_actor_id()
    state = self.layer3.read_state()
    scene_id = getattr(state.get("campaign"), "active_scene_id", None)
    intent = classify_open_ended_intent(text, actor_id=actor_id, scene_id=scene_id)
    policy = open_ended_policy_response(intent, state)
    self._append("open_ended_intent", "layer4", {"intent": intent, "policy": policy}, visibility="public_table")
    result = self.layer6.resolve_open_ended_intent(intent, state)
    self._commit_resolution_result(result)
    narration = self.layer7.narrate_resolution(result, prompt="How does the party proceed?")
    self._append("narration_event", "layer7", {"spoken_text": narration.spoken_text, "prompt": narration.prompt})
    self.layer10.create_snapshot(f"v050_{intent.intent_type}", state=self.layer3.read_state())
    return EngineTurnResult(narration=narration.spoken_text, prompt=narration.prompt, events=self.layer10.event_log.events, resolutions=[_plain(result)])


def _v050_run_open_ended_demo(self, session: RuntimeSession) -> list[EngineTurnResult]:
    outputs: list[EngineTurnResult] = []
    outputs.append(self.step(session))
    outputs.append(self.handle_open_ended_action("We retreat from the ambush and regroup."))
    outputs.append(self.handle_open_ended_action("We take a hobgoblin prisoner."))
    outputs.append(self.handle_open_ended_action("Tasslehoff scouts ahead, splitting from the main group."))
    outputs.append(self.handle_open_ended_action("Goldmoon throws away the blue crystal staff."))
    outputs.append(self.handle_open_ended_action("We search for another route into Xak Tsaroth."))
    outputs.append(self.handle_open_ended_action("We do something extremely specific that the engine cannot model yet."))
    self._append("module_event", "orchestrator", {"event": "v0.5_open_ended_demo_complete"}, visibility="dm_private")
    return outputs


Orchestrator.handle_open_ended_action = _v050_handle_open_ended_action
Orchestrator.run_v050_open_ended_demo = _v050_run_open_ended_demo
