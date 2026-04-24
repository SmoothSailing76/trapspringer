from trapspringer.schemas.maps import TrueMap, HiddenFeature, HazardFootprint

class TrueMapStore:
    def __init__(self) -> None:
        self.map = TrueMap(map_id="TRUEMAP-DL1")
        self._seed_dl1_features()

    def _seed_dl1_features(self) -> None:
        self.map.hidden_features.append(HiddenFeature(
            feature_id="HID-69B-SECRET-WAY",
            feature_type="hidden_trapdoor_tunnel",
            area_id="69b",
            zone="center_floor",
            connects_to="70k",
            discovery_conditions=["check_floor", "pull_ring"],
        ))
        self.map.hazards.append(HazardFootprint(
            hazard_id="HAZ-70J-GONG-PLATE",
            hazard_type="pressure_plate",
            area_id="70j",
            zone="mid_hall_plate",
            visibility="dm_private",
        ))

    def get_hidden_feature(self, feature_id: str) -> HiddenFeature | None:
        for feature in self.map.hidden_features:
            if feature.feature_id == feature_id:
                return feature
        return None

    def discover_feature(self, feature_id: str) -> HiddenFeature | None:
        feature = self.get_hidden_feature(feature_id)
        if feature:
            feature.discovered = True
        return feature
