from dataclasses import dataclass

@dataclass(slots=True)
class ExecutionPolicies:
    mechanics_visibility: str = "hybrid"
    mapping_policy: str = "human_approximate"
    party_simulation_level: str = "full"
    roll_visibility: str = "hybrid"
