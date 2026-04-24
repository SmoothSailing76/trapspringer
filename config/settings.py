from dataclasses import dataclass

@dataclass(slots=True)
class EngineSettings:
    campaign_id_prefix: str = "DL1"
    autosave_enabled: bool = True
    deterministic_seed: int | None = None
