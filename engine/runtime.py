from dataclasses import dataclass, field
from typing import Any
from trapspringer.config.policies import ExecutionPolicies
from trapspringer.config.settings import EngineSettings
from trapspringer.config.feature_flags import FeatureFlags

@dataclass(slots=True)
class RuntimeContext:
    campaign_id: str
    module_id: str = "DL1_DRAGONS_OF_DESPAIR"
    active_scene_id: str | None = None
    current_snapshot_id: str | None = None
    current_frame_id: str | None = None

@dataclass(slots=True)
class RuntimeSession:
    context: RuntimeContext
    settings: EngineSettings
    policies: ExecutionPolicies
    feature_flags: FeatureFlags
    services: dict[str, Any] = field(default_factory=dict)
