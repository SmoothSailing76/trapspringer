from __future__ import annotations

import json
from pathlib import Path

from trapspringer.domain.outcomes import SpatialQueryResult
from trapspringer.layers.layer9_map.public_map_store import PublicMapStore
from trapspringer.layers.layer9_map.true_map_store import TrueMapStore
from trapspringer.layers.layer9_map.scene_graph import RuntimeSceneGraph
from trapspringer.layers.layer9_map.reveals import reveal_area_entry, reveal_hidden_feature
from trapspringer.layers.layer9_map.los import query_los
from trapspringer.layers.layer9_map.dl1_spatial import DL1SpatialRegistry
from trapspringer.layers.layer9_map.fog_of_war import FogOfWarStore
from trapspringer.layers.layer9_map.grid_visibility import LightSource, trace_visibility

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
        self.dl1_spatial = DL1SpatialRegistry()
        self.fog = FogOfWarStore()
        self.light_sources: dict[str, list[LightSource]] = {}

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
            graph.place(
                str(entity["entity_id"]),
                str(entity["zone"]),
                hidden=bool(entity.get("hidden", False)),
                concealed=bool(entity.get("concealed", False)),
            )
        self.public_maps.reveal_area(scene_id)
        self.fog.reveal(scene_id, scene_id, state="seen", note="scene entered")
        return graph

    def setup_scene_from_content(self, scene_content: dict, party_ids: list[str], scene_id: str | None = None):
        sid = scene_id or str(scene_content["scene_id"])
        graph = self.instantiate_scene_graph(sid, str(scene_content["map_template_id"]))
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

    def trace_visibility(self, request: dict | None = None) -> SpatialQueryResult:
        request = request or {}
        scene_id = str(request.get("scene_id", "DL1_EVENT_1_AMBUSH"))
        trace = trace_visibility(
            self.scene_graphs.get(scene_id),
            str(request.get("observer")),
            str(request.get("target")),
            self.light_sources.get(scene_id, []),
            bool(request.get("include_concealed", False)),
        )
        return SpatialQueryResult(status="ok", payload={
            "observer": trace.observer,
            "target": trace.target,
            "result": trace.result,
            "visible": trace.visible,
            "range_band": trace.range_band,
            "light": trace.light,
            "blockers": trace.blockers,
            "reason": trace.reason,
        })

    def add_light_source(self, scene_id: str, source_id: str, zone: str, carrier_id: str | None = None, bright_radius_ft: int = 20, dim_radius_ft: int = 40) -> dict[str, object]:
        src = LightSource(source_id=source_id, carrier_id=carrier_id, zone=zone, bright_radius_ft=bright_radius_ft, dim_radius_ft=dim_radius_ft)
        self.light_sources.setdefault(scene_id, []).append(src)
        return {"type": "light_source_added", "scene_id": scene_id, "source_id": source_id, "zone": zone}

    def query_reachability(self, request: dict | None = None) -> SpatialQueryResult:
        request = request or {}
        scene_id = str(request.get("scene_id", "DL1_EVENT_1_AMBUSH"))
        graph = self.scene_graphs.get(scene_id)
        reachable = False if graph is None else graph.reachable(str(request.get("actor")), str(request.get("target_zone")))
        reason = "reachable" if reachable else "not_connected"
        return SpatialQueryResult(status="ok", payload={"reachable": reachable, "reason": reason})

    def reveal_feature(self, scene_id: str, feature_id: str):
        self.public_maps.annotate(scene_id, f"revealed:{feature_id}")
        self.fog.reveal(scene_id, feature_id, state="seen", note="hidden feature discovered")
        return {"type": "hidden_feature_found", "scene_id": scene_id, "feature_id": feature_id}

    def reveal_area_on_public_map(self, map_id: str, area_id: str, state: str = "seen", note: str | None = None) -> dict[str, object]:
        self.public_maps.reveal_area(area_id)
        return self.fog.reveal(map_id, area_id, state=state, note=note)

    def public_fog_snapshot(self, map_id: str) -> dict[str, object]:
        return self.fog.get(map_id).public_snapshot()

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

    def dl1_spatial_summary(self) -> dict[str, object]:
        return self.dl1_spatial.spatial_summary()

    def load_xak_tsaroth_level(self, level: int) -> dict:
        return self.dl1_spatial.load_xak_level(level)

    def load_wilderness_spatial_manifest(self) -> dict:
        return self.dl1_spatial.load_wilderness_manifest()

    def validate_dl1_spatial_assets(self) -> dict[str, object]:
        return self.dl1_spatial.validate_assets_present()

    def v070_visibility_demo_state(self) -> dict[str, object]:
        scene_id = "V070_VISIBILITY_DEMO"
        if scene_id not in self.scene_graphs:
            graph = self.instantiate_scene_graph(scene_id, "AREA_44K_PLAZA_DEATH_MAP")
            graph.place("PC_TANIS", "swamp_entry")
            graph.place("KHISANTH_SHADOW", "great_well", concealed=True)
            self.add_light_source(scene_id, "torch_tanis", "swamp_entry", carrier_id="PC_TANIS")
        hidden_trace = self.trace_visibility({"scene_id": scene_id, "observer": "PC_TANIS", "target": "KHISANTH_SHADOW"}).payload
        reveal = self.reveal_entity(scene_id, "KHISANTH_SHADOW")
        revealed_trace = self.trace_visibility({"scene_id": scene_id, "observer": "PC_TANIS", "target": "KHISANTH_SHADOW"}).payload
        map_diff = self.reveal_area_on_public_map("DL1_XAK_TSAROTH_PUBLIC", "44k", state="explored", note="plaza entered")
        fog = self.public_fog_snapshot("DL1_XAK_TSAROTH_PUBLIC")
        return {"scene_id": scene_id, "hidden_trace": hidden_trace, "reveal": reveal, "revealed_trace": revealed_trace, "map_diff": map_diff, "fog": fog}
