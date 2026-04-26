import json
from pathlib import Path
from trapspringer.config.feature_flags import FeatureFlags
from trapspringer.config.policies import ExecutionPolicies
from trapspringer.config.settings import EngineSettings
from trapspringer.engine.runtime import RuntimeContext, RuntimeSession

PACKAGE_ROOT = Path(__file__).resolve().parents[1]

class LifecycleManager:
    def load_module_manifest(self, module_id: str = "DL1_DRAGONS_OF_DESPAIR") -> dict:
        path = PACKAGE_ROOT / "data/manifests/module_manifest_dl1.json"
        manifest = json.loads(path.read_text())
        if manifest.get("module_id") != module_id:
            raise ValueError(f"Unexpected module manifest: {manifest.get('module_id')}")
        return manifest

    def create_session(self, campaign_id: str, services: dict | None = None, user_character_id: str | None = None) -> RuntimeSession:
        manifest = self.load_module_manifest()
        context = RuntimeContext(
            campaign_id=campaign_id,
            module_id=manifest["module_id"],
            active_scene_id=manifest["start_scene_id"],
        )
        return RuntimeSession(
            context=context,
            settings=EngineSettings(),
            policies=ExecutionPolicies(),
            feature_flags=FeatureFlags(),
            services=services or {},
        )

    def bootstrap_dl1_campaign(self, campaign_id: str, services: dict, user_character_id: str | None = None) -> RuntimeSession:
        manifest = self.load_module_manifest()
        session = self.create_session(campaign_id, services=services, user_character_id=user_character_id)
        state_service = services["state"]
        procedure_service = services["procedure"]
        map_service = services["map"]
        party_service = services["party"]
        audit_service = services["audit"]

        state_service.create_initial_state({"campaign_id": campaign_id})
        state = state_service.read_state()
        party_ids = list(state["party"].member_ids)
        party_service.initialize_seats(user_character_id, party_ids)

        # Opening Event 1 frame and module flag.
        frame = procedure_service.trigger_opening_module_event(manifest["start_scene_id"])
        state_service.mark_event_triggered("EVENT_1")
        state["module"].world_flags["event1_started"] = True
        state["module"].world_flags["current_milestone"] = "start_of_event_1"
        session.context.current_frame_id = frame.frame_id
        session.context.active_scene_id = frame.scene_id

        # Scene graph and actor positions.
        scene_content = state["scene"].content
        graph = map_service.instantiate_scene_graph(frame.scene_id, scene_content["map_template_id"])
        for actor_id in party_ids:
            graph.place(actor_id, "road_center_party")
        for i in range(10):
            graph.place(f"HOBGOBLIN_EVENT1_{i+1}", "left_woodline" if i % 2 == 0 else "right_woodline")
        graph.place("NPC_TOEDE", "toede_front")

        audit_service.append_event_from_dict({
            "event_id": "EVT-CAMPAIGN-START",
            "event_type": "campaign_start",
            "source_layer": "lifecycle",
            "visibility": "dm_private",
            "payload": {"campaign_id": campaign_id, "module_id": manifest["module_id"]},
        })
        audit_service.append_event_from_dict({
            "event_id": "EVT-DL1-EVENT1-TRIGGER",
            "event_type": "module_event",
            "source_layer": "layer4",
            "visibility": "dm_private",
            "payload": {"event_id": "EVENT_1", "scene_id": frame.scene_id},
        })
        snap = audit_service.create_snapshot("start_of_event_1", state=state, milestone_id="start_of_event_1")
        session.context.current_snapshot_id = snap
        return session
