import json
from pathlib import Path
from trapspringer.schemas.loaders import (
    load_encounter,
    load_module_manifest,
    load_npc,
    load_pregen,
    load_scene,
)
from trapspringer.schemas.maps import Position
from trapspringer.schemas.state import CampaignState, CharacterState, PartyState, SceneState, TimeState
from trapspringer.layers.layer3_state.campaign_store import CampaignStore
from trapspringer.layers.layer3_state.module_flags import initial_dl1_module_state
from trapspringer.layers.layer3_state.mutator import apply_mutations

PACKAGE_ROOT = Path(__file__).resolve().parents[2]

ACTIVE_EVENT1_PARTY = ["tanis", "tasslehoff", "sturm", "caramon", "raistlin", "flint"]
OPTIONAL_DL1_ACTORS = ["goldmoon", "riverwind"]

class StateService:
    def __init__(self) -> None:
        self.store = CampaignStore()

    def _load_json(self, rel_path: str) -> dict:
        return json.loads((PACKAGE_ROOT / rel_path).read_text())

    def _char_from_data(self, data: dict, actor_id: str | None = None, hp: int | None = None, team: str = "party") -> CharacterState:
        aid = actor_id or data["actor_id"]
        return CharacterState(
            actor_id=aid,
            name=data["name"],
            actor_type=data["actor_type"],
            current_hp=int(hp if hp is not None else data.get("current_hp", data.get("max_hp", 0))),
            max_hp=int(hp if hp is not None else data.get("max_hp", 0)),
            ac=int(data.get("ac", 10)),
            level=int(data.get("level", 0)),
            character_class=data.get("class"),
            alignment=data.get("alignment"),
            movement=int(data.get("movement", 12)),
            location=Position(area_id="EVENT_1_START", zone="road_center_party" if team == "party" else None),
            inventory=list(data.get("equipment", [])),
            spells=list(data.get("spells", [])),
            damage=str(data.get("damage", "1d6")),
            status=str(data.get("starting_status", "active")),
            team=team,
        )

    def load_pregen(self, pregen_id: str, team: str = "party") -> CharacterState:
        return self._char_from_data(load_pregen(PACKAGE_ROOT / f"data/dl1/pregens/{pregen_id}.json"), team=team)

    def load_toede(self) -> CharacterState:
        c = self._char_from_data(load_npc(PACKAGE_ROOT / "data/dl1/npcs/toede.json"), team="enemy")
        c.location = Position(area_id="EVENT_1_START", zone="toede_front")
        return c

    def load_event1_hobgoblins(self) -> dict[str, CharacterState]:
        data = load_encounter(PACKAGE_ROOT / "data/dl1/encounters/hobgoblin_event1_group.json")
        out: dict[str, CharacterState] = {}
        for i, hp in enumerate(data["max_hp_values"], start=1):
            aid = f"HOBGOBLIN_EVENT1_{i}"
            c = self._char_from_data(data, actor_id=aid, hp=int(hp), team="enemy")
            c.name = f"Hobgoblin {i}"
            c.location = Position(area_id="EVENT_1_START", zone="left_woodline" if i % 2 else "right_woodline")
            out[aid] = c
        return out

    def create_character_states_from_pregens(self, pregen_ids: list[str]) -> dict[str, CharacterState]:
        chars = [self.load_pregen(pid) for pid in pregen_ids]
        return {c.actor_id: c for c in chars}

    def create_party_state_from_pregens(self, pregen_ids: list[str]) -> PartyState:
        chars = [self.load_pregen(pid) for pid in pregen_ids]
        ids = [c.actor_id for c in chars]
        return PartyState(
            party_id="PARTY-0001",
            member_ids=ids,
            caller_actor_id="PC_TANIS" if "PC_TANIS" in ids else ids[0],
            mapper_actor_id="PC_TASSLEHOFF" if "PC_TASSLEHOFF" in ids else ids[0],
            marching_order=list(ids),
        )

    def create_initial_state(self, config: dict | None = None) -> CampaignState:
        config = config or {}
        scene_content = load_scene(PACKAGE_ROOT / "data/dl1/scenes/event_1_ambush.json")
        campaign = CampaignState(config.get("campaign_id", "DL1-CAMPAIGN-001"), "ADND_1E", "DL1_DRAGONS_OF_DESPAIR", "active", "DL1_EVENT_1_AMBUSH")
        time = TimeState(day=1, hour=20, mode="setup")
        characters = self.create_character_states_from_pregens(ACTIVE_EVENT1_PARTY)
        # Load later module actors as inactive until their scenes introduce them.
        for pid in OPTIONAL_DL1_ACTORS:
            c = self.load_pregen(pid, team="party")
            if c.actor_id == "PC_GOLDMOON":
                c.status = "offstage"
            if c.actor_id == "NPC_RIVERWIND":
                c.status = "offstage"
                c.actor_type = "npc"
            characters[c.actor_id] = c
        characters["NPC_TOEDE"] = self.load_toede()
        characters.update(self.load_event1_hobgoblins())
        party = self.create_party_state_from_pregens(ACTIVE_EVENT1_PARTY)
        participants = list(party.member_ids) + ["NPC_TOEDE"] + [f"HOBGOBLIN_EVENT1_{i}" for i in range(1, 11)]
        scene = SceneState("DL1_EVENT_1_AMBUSH", "combat_opening", "EVENT_1_START", participants=participants, hazards=[], content=scene_content)
        module = initial_dl1_module_state()
        module.world_flags.setdefault("toede_fled", False)
        module.world_flags.setdefault("goldmoon_joined", False)
        module.world_flags.setdefault("riverwind_joined", False)
        module.world_flags.setdefault("wicker_dragon_discovered", False)
        module.world_flags.setdefault("khisanth_surface_seen", False)
        module.world_flags.setdefault("current_route", "ROAD_EAST_OF_SOLACE")
        self.store.state = {"campaign": campaign, "time": time, "characters": characters, "party": party, "scene": scene, "module": module}
        return campaign

    def load_scene_content(self, scene_id: str) -> dict:
        manifest = load_module_manifest(PACKAGE_ROOT / "data/manifests/module_manifest_dl1.json")
        rel = manifest["scene_files"].get(scene_id)
        if not rel:
            raise KeyError(scene_id)
        return load_scene(PACKAGE_ROOT / rel)

    def transition_to_scene(self, scene_id: str) -> SceneState:
        content = self.load_scene_content(scene_id)
        scene = SceneState(scene_id, content.get("type", "exploration"), content.get("area_id", scene_id), participants=list(self.store.state["party"].member_ids), content=content)
        self.store.state["scene"] = scene
        self.store.state["campaign"].active_scene_id = scene_id
        self.store.state["time"].mode = content.get("type", "exploration")
        if content.get("area_id"):
            self.store.state["module"].entered_areas.append(str(content.get("area_id")))
        return scene

    def add_actor_to_party(self, actor_id: str) -> None:
        state = self.store.state
        party = state["party"]
        actor = state["characters"].get(actor_id)
        if actor is None:
            return
        actor.status = "active"
        actor.team = "party"
        actor.location = Position(area_id=state["scene"].area_id, zone="roadside_party")
        if actor_id not in party.member_ids:
            party.member_ids.append(actor_id)
            party.marching_order.append(actor_id)

    def mark_event_triggered(self, event_id: str) -> None:
        module = self.store.state.get("module")
        if module is not None:
            module.triggered_events[event_id] = True

    def read_state(self, query: dict | None = None):
        return self.store.state

    def commit_mutations(self, mutation_set: list[dict[str, object]]):
        return apply_mutations(self.store.state, mutation_set)

    def active_enemies(self) -> list[str]:
        chars = self.store.state.get("characters", {})
        return [aid for aid, c in chars.items() if getattr(c, "team", None) == "enemy" and getattr(c, "is_active", False)]

    def active_party_members(self) -> list[str]:
        chars = self.store.state.get("characters", {})
        return [aid for aid, c in chars.items() if getattr(c, "team", None) == "party" and getattr(c, "is_active", False)]
