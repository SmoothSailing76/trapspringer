from dataclasses import dataclass

@dataclass(slots=True)
class FeatureFlags:
    enable_party_simulation: bool = True
    enable_replay: bool = True
    enable_integrity_checks: bool = True
    enable_cli_adapter: bool = True
