import json
from pathlib import Path
from trapspringer.domain.outcomes import SpatialQueryResult
from trapspringer.layers.layer9_map.public_map_store import PublicMapStore
from trapspringer.layers.layer9_map.true_map_store import TrueMapStore
from trapspringer.layers.layer9_map.scene_graph import RuntimeSceneGraph
from trapspringer.layers.layer9_map.reveals import reveal_area_entry, reveal_hidden_feature
from trapspringer.layers.layer9_map.los import query_los

PACKAGE_ROOT = Path(__file__).resolve().parents[2]

_TEMPLATE_FILES = {
    "EVENT_1_AMBUSH_MAP": "event_1_ambush_map.json",
    "AREA4_AMBUSH_MAP": "area4_ambush_map.json",
    "EVENT_2_ROADSIDE_MAP": "event_2_roadside_map.json",
    "AREA_44F_TEMPLE_BAAZ_MAP": "area_44f_temple_baaz_map.json",
    "AREA_44K_PLAZA_DEATH_MAP": "area_44k_plaza_death_map.json",
    "TEMPLE_MISHAKAL_MAP": "temple_mishakal_map.json",
    "DESCENT_MAP": "descent_map.json",
    "LOWER_CITY_MAP": "lower_city_map.json",
    "DRAGON_LAIR_70K_MAP": "dragon_lair_70k_map.json",
    "COLLAPSE_EPILOGUE_MAP": "collapse_epilogue_map.json",
}

class MapVisibilityService:
    def __init__(self) -> None:
        self.true_maps = TrueMapStore()
        self.public_maps = PublicMapStore()
        self.scene_graphs: dict[str, RuntimeSceneGraph] = {}

    def load_scene_template(self, template_id: str) -> dict:
        filename = _TEMPLATE_FILES.get(template_id)
        if not filename:
            raise KeyError(template_id)
        return json.loads((PACKAGE_ROOT / f"data/maps/scene_templates/{filename}").read_text())

    def instantiate_scene_graph(self, scene_id: str, template_id: str) -> RuntimeSceneGraph:
        data = self.load_scene_template(template_id)
        graph = RuntimeSceneGraph(
            scene_id=scene_id,
            template_id=template_id,
            zones=list(data["zones"]),
            connections=list(data["connections"]),
            line_of_sight=dict(data["line_of_sight"]),
        )
        self.scene_graphs[scene_id] = graph
        for entity in data.get("initial_entities", []):
            graph.place(str(entity["entity_id"]), str(entity["zone"]), hidden=bool(entity.get("hidden", False)), concealed=bool(entity.get("concealed", False)))
        self.public_maps.reveal_area(scene_id)
        return graph

    def setup_scene_from_content(self, scene_content: dict, party_ids: list[str], scene_id: str | None = None):
        sid = scene_id or str(scene_content["scene_id"])
        graph = self.instantiate_scene_graph(sid, str(scene_content["map_template_id"]))
        # Place party in first zone by template convention.
        start_zone = graph.zones[0] if graph.zones else "start"
        if sid == "DL1_EVENT_2_GOLDMOON":
            start_zone = "roadside_party"
            graph.place("PC_GOLDMOON", "music_camp")
            graph.place("NPC_RIVERWIND", "music_camp")
        elif sid == "DL1_AREA_44F":
            start_zone = "swamp_edge"
        elif sid == "DL1_AREA_44K":
            start_zone = "swamp_entry"
        for aid in party_ids:
            graph.place(aid, start_zone)
        return graph

    def place_entity(self, scene_id: str, entity_id: str, zone: str, hidden: bool = False, concealed: bool = False) -> None:
        self.scene_graphs[scene_id].place(entity_id, zone, hidden=hidden, concealed=concealed)

    def reveal_entity(self, scene_id: str, entity_id: str):
        graph = self.scene_graphs[scene_id]
        graph.reveal_entity(entity_id)
        return {"type": "reveal_entity", "scene_id": scene_id, "entity_id": entity_id}

    def query_visibility(self, request: dict | None = None) -> SpatialQueryResult:
        request = request or {}
        scene_id = str(request.get("scene_id", "DL1_EVENT_1_AMBUSH"))
        graph = self.scene_graphs.get(scene_id)
        detail = query_los(graph, str(request.get("observer")), str(request.get("target")), bool(request.get("include_concealed", False)))
        return SpatialQueryResult(status="ok", payload=detail)

    def query_reachability(self, request: dict | None = None) -> SpatialQueryResult:
        request = request or {}
        scene_id = str(request.get("scene_id", "DL1_EVENT_1_AMBUSH"))
        graph = self.scene_graphs.get(scene_id)
        reachable = False if graph is None else graph.reachable(str(request.get("actor")), str(request.get("target_zone")))
        reason = "reachable" if reachable else "not_connected"
        return SpatialQueryResult(status="ok", payload={"reachable": reachable, "reason": reason})

    def reveal_feature(self, scene_id: str, feature_id: str):
        self.public_maps.annotate(scene_id, f"revealed:{feature_id}")
        return {"type": "hidden_feature_found", "scene_id": scene_id, "feature_id": feature_id}

    def apply_map_changes(self, diff: dict | None = None):
        return self.public_maps.apply_diff(diff or {})

    def reveal_for_trigger(self, trigger: dict | None = None):
        trigger = trigger or {}
        kind = trigger.get("type")
        if kind == "area_entry":
            area_id = str(trigger.get("area_id"))
            visible_connections = trigger.get("visible_connections", [])
            diff = reveal_area_entry(area_id, visible_connections)
            return self.public_maps.apply_diff(diff)
        if kind == "hidden_feature_found":
            feature_id = str(trigger.get("feature_id"))
            feature = self.true_maps.discover_feature(feature_id)
            if feature is None:
                return {"changes": []}
            diff = reveal_hidden_feature(feature)
            return self.public_maps.apply_diff(diff)
        return {"changes": []}

    def public_map_snapshot(self) -> dict[str, object]:
        m = self.public_maps.map
        return {
            "map_id": m.map_id,
            "revealed_areas": list(m.revealed_areas),
            "revealed_connections": list(m.revealed_connections),
            "player_annotations": list(m.player_annotations),
            "uncertain_features": list(m.uncertain_features),
        }
