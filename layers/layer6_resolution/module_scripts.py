from trapspringer.schemas.resolution import PrivateOutcome, PublicOutcome, ResolutionResult


def resolve_toede_escape(state: dict, map_service=None) -> ResolutionResult:
    already = state["module"].world_flags.get("toede_fled", False)
    if already:
        return ResolutionResult("RES-TOEDE-FLEE", "no_effect")
    mutations = [
        {"path": "module.world_flags.toede_fled", "value": True},
        {"path": "characters.NPC_TOEDE.status", "value": "fled"},
        {"path": "characters.NPC_TOEDE.location.zone", "value": "toede_escape_path"},
    ]
    if map_service:
        try:
            map_service.place_entity("DL1_EVENT_1_AMBUSH", "NPC_TOEDE", "toede_escape_path")
        except Exception:
            pass
    return ResolutionResult(
        resolution_id="RES-TOEDE-FLEE",
        status="resolved",
        private_outcome=PrivateOutcome({"toede_fled": True}),
        public_outcome=PublicOutcome("Fewmaster Toede wheels his swaybacked pony around and gallops into the woods, leaving his hobgoblins to attack."),
        state_mutations=mutations,
    )


def resolve_event2_join(state: dict) -> ResolutionResult:
    module = state["module"]
    if module.world_flags.get("goldmoon_joined"):
        return ResolutionResult("RES-EVENT2-JOIN", "no_effect", public_outcome=PublicOutcome("Goldmoon and Riverwind are already with the party."))
    mutations = [
        {"path": "module.triggered_events.EVENT_2", "value": True},
        {"path": "module.world_flags.goldmoon_joined", "value": True},
        {"path": "module.world_flags.riverwind_joined", "value": True},
        {"path": "module.quest_flags.staff_in_party_possession", "value": True},
        {"path": "characters.PC_GOLDMOON.status", "value": "active"},
        {"path": "characters.NPC_RIVERWIND.status", "value": "active"},
        {"path": "characters.PC_GOLDMOON.location.zone", "value": "music_camp"},
        {"path": "characters.NPC_RIVERWIND.location.zone", "value": "music_camp"},
    ]
    return ResolutionResult(
        "RES-EVENT2-JOIN",
        "resolved",
        PrivateOutcome({"goldmoon_joined": True, "riverwind_joined": True, "staff_in_party": True}),
        PublicOutcome("Goldmoon and Riverwind agree to travel with the companions. The blue crystal staff is now openly part of the party's fate."),
        mutations,
        knowledge_effects=[{"fact_id": "F-GOLDMOON-HAS-STAFF", "proposition": "Goldmoon bears the Blue Crystal Staff.", "visibility_after": "party_known", "discovered_by": "PARTY"}],
    )


def resolve_inspect_wicker_dragon(state: dict, actor_id: str = "PC_TASSLEHOFF") -> ResolutionResult:
    if state["module"].world_flags.get("wicker_dragon_discovered"):
        return ResolutionResult("RES-44F-WICKER", "no_effect", public_outcome=PublicOutcome("The dragon figure is already known to be a wicker model."))
    mutations = [{"path": "module.world_flags.wicker_dragon_discovered", "value": True}]
    return ResolutionResult(
        "RES-44F-WICKER",
        "resolved",
        PrivateOutcome({"fact": "wicker_dragon", "discovered_by": actor_id}),
        PublicOutcome("Up close, the dragon shape proves to be woven wicker over a wooden frame, not living flesh."),
        mutations,
        knowledge_effects=[{"fact_id": "F-44F-WICKER-DRAGON", "proposition": "The dragon shape at the Temple of Baaz is a wicker model.", "visibility_after": "party_known", "discovered_by": "PARTY"}],
    )


def resolve_khisanth_surface_arrival(state: dict) -> ResolutionResult:
    if state["module"].world_flags.get("khisanth_surface_seen"):
        return ResolutionResult("RES-44K-KHISANTH", "no_effect", public_outcome=PublicOutcome("The plaza remains under the shadow of Khisanth's arrival."))
    mutations = [{"path": "module.world_flags.khisanth_surface_seen", "value": True}]
    return ResolutionResult(
        "RES-44K-KHISANTH",
        "resolved",
        PrivateOutcome({"khisanth_arrives": True}),
        PublicOutcome("A rush of dead-cold air rises from the well. Khisanth, an immense black dragon, bursts upward and casts darkness over the plaza."),
        mutations,
        knowledge_effects=[{"fact_id": "F-KHISANTH-SEEN", "proposition": "Khisanth is real and has emerged from the great well at Xak Tsaroth.", "visibility_after": "party_known", "discovered_by": "PARTY"}],
    )


def resolve_mishakal_audience_and_recharge(state: dict) -> ResolutionResult:
    """v0.2.0 main path: statue audience and full staff recharge."""
    if state["module"].world_flags.get("mishakal_audience_complete"):
        return ResolutionResult("RES-MISHAKAL-AUDIENCE", "no_effect", public_outcome=PublicOutcome("Mishakal's chamber remains warm and still; the staff is already recharged."))
    mutations = [
        {"path": "module.world_flags.mishakal_audience_complete", "value": True},
        {"path": "module.quest_flags.staff_recharged_at_mishakal", "value": True},
        {"path": "module.world_flags.temple_mishakal_entered", "value": True},
    ]
    return ResolutionResult(
        "RES-MISHAKAL-AUDIENCE",
        "resolved",
        PrivateOutcome({"mishakal_message": True, "staff_charges": 20}),
        PublicOutcome("The statue of Mishakal comes alive with warmth and sorrow. She tells you that the gods have not abandoned the world: mortals turned away. Far below, in the dragon's lair, lie the Disks of Mishakal. The Blue Crystal Staff glows in her arms and is restored to full power."),
        mutations,
        knowledge_effects=[{"fact_id":"F-MISHAKAL-QUEST","proposition":"The Disks of Mishakal lie below in the dragon's lair and can restore true clerical worship.","visibility_after":"party_known","discovered_by":"PARTY"}],
    )


def resolve_descent_started(state: dict) -> ResolutionResult:
    if state["module"].world_flags.get("descent_started"):
        return ResolutionResult("RES-DESCENT", "no_effect", public_outcome=PublicOutcome("The descent route into the buried city is already open."))
    mutations = [
        {"path":"module.world_flags.descent_started","value":True},
        {"path":"module.world_flags.great_well_descended","value":True},
    ]
    return ResolutionResult(
        "RES-DESCENT",
        "resolved",
        PrivateOutcome({"route":"temple_to_lower_city"}),
        PublicOutcome("You commit to the descent: past the Great Well, broken halls, the Aghar elevator, and slick sewer passages that slide toward the ancient city below."),
        mutations,
    )


def resolve_lower_city_route_discovery(state: dict) -> ResolutionResult:
    if state["module"].world_flags.get("secret_route_known"):
        return ResolutionResult("RES-LOWER-CITY-ROUTE", "no_effect", public_outcome=PublicOutcome("The secret route toward the dragon's lair is already known."))
    mutations = [
        {"path":"module.world_flags.lower_city_reached","value":True},
        {"path":"module.world_flags.secret_route_known","value":True},
    ]
    return ResolutionResult(
        "RES-LOWER-CITY-ROUTE",
        "resolved",
        PrivateOutcome({"secret_route":"69b_to_70k"}),
        PublicOutcome("In the lower city, Aghar gossip and a crude hidden map point to a secret way: sewer access at 69b leads toward Khisanth's lair beneath the Hall of Justice."),
        mutations,
        knowledge_effects=[{"fact_id":"F-SECRET-ROUTE-70K","proposition":"The sewer access at 69b leads through a tunnel toward Khisanth's lair at 70k.","visibility_after":"party_known","discovered_by":"PARTY"}],
    )


def resolve_dragon_lair_finale(state: dict, breaker: str = "PC_GOLDMOON") -> ResolutionResult:
    if state["module"].quest_flags.get("staff_shattered"):
        return ResolutionResult("RES-70K-FINALE", "no_effect", public_outcome=PublicOutcome("Khisanth has already been defeated and the cavern is collapsing."))
    mutations = [
        {"path":"module.world_flags.dragon_lair_entered","value":True},
        {"path":"module.quest_flags.disks_recovered","value":True},
        {"path":"module.quest_flags.khisanth_defeated","value":True},
        {"path":"module.quest_flags.staff_shattered","value":True},
        {"path":"module.world_flags.cavern_collapse_active","value":True},
        {"path":"module.world_flags.collapse_escape_started","value":True},
    ]
    return ResolutionResult(
        "RES-70K-FINALE",
        "resolved",
        PrivateOutcome({"disks_recovered":True,"khisanth_defeated":True,"breaker":breaker}),
        PublicOutcome("The staff strikes Khisanth and shatters. Blue light surges outward in ringing waves, swallowing the dragon and shaking the rotunda. The Disks of Mishakal are seized from the hoard as the ceiling begins to fail. The cavern is collapsing."),
        mutations,
        knowledge_effects=[{"fact_id":"F-DISKS-RECOVERED","proposition":"The party has recovered the Disks of Mishakal.","visibility_after":"party_known","discovered_by":"PARTY"}],
    )


def resolve_collapse_escape_and_epilogue(state: dict, breaker: str = "PC_GOLDMOON") -> ResolutionResult:
    if state["module"].quest_flags.get("medallion_created"):
        return ResolutionResult("RES-EPILOGUE", "no_effect", public_outcome=PublicOutcome("The epilogue has already occurred."))
    mutations = [
        {"path":"module.world_flags.cavern_collapse_active","value":False},
        {"path":"module.world_flags.epilogue_complete","value":True},
        {"path":"module.quest_flags.medallion_created","value":True},
        {"path":"module.quest_flags.clerical_magic_restored","value":True},
    ]
    return ResolutionResult(
        "RES-EPILOGUE",
        "resolved",
        PrivateOutcome({"breaker_restored":breaker,"medallion_created":True}),
        PublicOutcome("You escape back to the Temple of Mishakal. The one who broke the staff lies unharmed at the statue's feet, all wounds restored. A platinum Medallion of Faith now rests at their throat, and the staff has become part of the statue."),
        mutations,
        knowledge_effects=[{"fact_id":"F-MEDALLION-CREATED","proposition":"The Medallion of Faith has appeared and true clerical worship can return.","visibility_after":"party_known","discovered_by":"PARTY"}],
    )


# ---------------------------------------------------------------------------
# Optional branches
# ---------------------------------------------------------------------------

def resolve_road_east_goblin_scouts(state: dict, rng=None) -> ResolutionResult:
    """Optional branch: goblin scouts on the Road East of Solace."""
    from trapspringer.rules import adnd1e_v04
    from trapspringer.services.random_service import RandomService
    rng = rng or RandomService(seed=1)
    if state["module"].world_flags.get("road_east_scouts_resolved"):
        return ResolutionResult("RES-ROAD-SCOUTS", "no_effect", public_outcome=PublicOutcome("The road east is already clear."))
    reaction = adnd1e_v04.reaction_check(rng, modifier=-2, npc_id="goblin_scouts")
    if reaction.result in ("hostile", "unfriendly"):
        outcome_text = "Three goblin scouts spring from the underbrush, blades out. They attack!"
        outcome_flag = "road_east_scouts_hostile"
    else:
        outcome_text = "A trio of goblin scouts materializes from the brush, then melts back into the forest. They decided you were not worth the trouble."
        outcome_flag = "road_east_scouts_fled"
    mutations = [
        {"path": "module.world_flags.road_east_scouts_resolved", "value": True},
        {"path": f"module.world_flags.{outcome_flag}", "value": True},
    ]
    return ResolutionResult(
        "RES-ROAD-SCOUTS", "resolved",
        PrivateOutcome({"reaction": reaction.result, "roll": reaction.roll}),
        PublicOutcome(outcome_text),
        mutations,
    )


def resolve_road_east_nomad_camp(state: dict, rng=None) -> ResolutionResult:
    """Optional branch: Que-Shu nomad camp on the Road East of Solace."""
    from trapspringer.rules import adnd1e_v04
    from trapspringer.services.random_service import RandomService
    rng = rng or RandomService(seed=1)
    if state["module"].world_flags.get("nomad_camp_resolved"):
        return ResolutionResult("RES-NOMAD-CAMP", "no_effect", public_outcome=PublicOutcome("The nomad camp has already been visited."))
    cha_mod = 1 if state["module"].world_flags.get("goldmoon_joined") else 0
    reaction = adnd1e_v04.reaction_check(rng, modifier=cha_mod, npc_id="que_shu_nomads")
    if reaction.result in ("friendly", "helpful"):
        outcome_text = "The Que-Shu nomads recognize Goldmoon's staff markings and offer water, dried meat, and what little news they have: draconian patrols are thickening east of Que-Kiri."
        outcome_flag = "nomad_camp_friendly"
        sets_intel = True
    else:
        outcome_text = "The nomad camp is wary. They watch you pass without offering trade or counsel, hands near their weapons."
        outcome_flag = "nomad_camp_neutral"
        sets_intel = False
    mutations = [
        {"path": "module.world_flags.nomad_camp_resolved", "value": True},
        {"path": f"module.world_flags.{outcome_flag}", "value": True},
    ]
    knowledge = []
    if sets_intel:
        knowledge.append({"fact_id": "F-DRACONIAN-PATROLS", "proposition": "Draconian patrols are increasing east of Que-Kiri.", "visibility_after": "party_known", "discovered_by": "PARTY"})
    return ResolutionResult(
        "RES-NOMAD-CAMP", "resolved",
        PrivateOutcome({"reaction": reaction.result, "cha_mod": cha_mod}),
        PublicOutcome(outcome_text),
        mutations,
        knowledge_effects=knowledge,
    )


def resolve_road_east_rejoin_main_path(state: dict) -> ResolutionResult:
    """Optional branch: party returns to the main road toward Xak Tsaroth."""
    if state["module"].world_flags.get("road_east_rejoined"):
        return ResolutionResult("RES-ROAD-REJOIN", "no_effect", public_outcome=PublicOutcome("The party is already back on the main path."))
    mutations = [
        {"path": "module.world_flags.road_east_rejoined", "value": True},
        {"path": "module.world_flags.xak_tsaroth_reached", "value": True},
    ]
    return ResolutionResult(
        "RES-ROAD-REJOIN", "resolved",
        PrivateOutcome({"rejoined": True}),
        PublicOutcome("The eastern detour ends where the crumbled road bends south. Ahead, through dead cypress and swamp-mist, the black towers of Xak Tsaroth are visible at last."),
        mutations,
        knowledge_effects=[{"fact_id": "F-XAK-TSAROTH-VISIBLE", "proposition": "Xak Tsaroth is visible from the eastern road junction.", "visibility_after": "party_known", "discovered_by": "PARTY"}],
    )


def resolve_main_path_milestone(session, next_milestone_id: str):
    """Advance a runtime session to a registered v0.2 main-path milestone.

    This helper is intentionally light: the orchestrator owns scene transitions and
    checkpointing, while this function centralizes registry validation and flag
    application for milestone state.
    """
    from trapspringer.layers.layer4_procedure.transitions import load_main_path_registry, validate_main_path_transition, apply_milestone_flags
    from trapspringer.schemas.resolution import PrivateOutcome, PublicOutcome, ResolutionResult

    state = session.services["state"].read_state() if hasattr(session, "services") else session["state"].read_state()
    module_state = state["module"]
    registry = load_main_path_registry()
    current_id = str(module_state.world_flags.get("current_milestone") or "start_of_event_1")
    ok, reason = validate_main_path_transition(current_id, next_milestone_id, registry, module_state)
    if not ok:
        return ResolutionResult(
            f"RES-MILESTONE-{next_milestone_id}",
            "blocked",
            PrivateOutcome({"current_milestone": current_id, "target_milestone": next_milestone_id, "reason": reason}),
            PublicOutcome(f"Milestone transition blocked: {reason}"),
            [],
        )
    flags = apply_milestone_flags(next_milestone_id, registry, module_state)
    milestone = registry[next_milestone_id]
    return ResolutionResult(
        f"RES-MILESTONE-{next_milestone_id}",
        "resolved",
        PrivateOutcome({"milestone": next_milestone_id, "flags_set": flags}),
        PublicOutcome(f"Milestone reached: {milestone.label}."),
        [],
    )
