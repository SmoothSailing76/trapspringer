from enum import Enum

class ProcedureMode(str, Enum):
    SETUP = "setup"
    TRAVEL = "travel"
    EXPLORATION = "exploration"
    CONVERSATION = "conversation"
    COMBAT = "combat"
    REST = "rest"
    ESCAPE = "escape"
    DOWNTIME = "downtime"
    MODULE_EVENT = "module_event"

class ValidationStatus(str, Enum):
    VALID = "valid"
    VALID_WITH_ASSUMPTIONS = "valid_with_assumptions"
    NEEDS_CLARIFICATION = "needs_clarification"
    INVALID = "invalid"
    IMPOSSIBLE = "impossible"
    BLOCKED_BY_KNOWLEDGE = "blocked_by_knowledge"
    BLOCKED_BY_PROCEDURE = "blocked_by_procedure"

class VisibilityClass(str, Enum):
    OBJECTIVE_TRUTH = "objective_truth"
    DM_PRIVATE = "dm_private"
    PUBLIC_TABLE = "public_table"
    PARTY_KNOWN = "party_known"
    ACTOR_PRIVATE = "actor_private"
    CONDITIONALLY_VISIBLE = "conditionally_visible"
    INFERRED_ONLY = "inferred_only"
    FALSE_BELIEF = "false_belief"
    FORGOTTEN = "forgotten"

class EventCategory(str, Enum):
    PROCEDURE = "procedure_event"
    DECLARATION = "declaration_event"
    VALIDATION = "validation_event"
    ROLL = "roll_event"
    RESOLUTION = "resolution_event"
    STATE_MUTATION = "state_mutation_event"
    MAP_MUTATION = "map_mutation_event"
    KNOWLEDGE = "knowledge_event"
    NARRATION = "narration_event"
    RULING = "ruling_event"
    MODULE = "module_event"
    SNAPSHOT = "snapshot_event"

class SceneType(str, Enum):
    TRAVEL = "travel"
    EXPLORATION = "exploration"
    COMBAT = "combat"
    SOCIAL = "social"
    REST = "rest"
    ESCAPE = "escape"
    DOWNTIME = "downtime"
    TRANSITION = "transition"

class ActorType(str, Enum):
    PC = "pc"
    NPC = "npc"
    MONSTER = "monster"
    HAZARD = "hazard"

class ToneTag(str, Enum):
    OMINOUS = "ominous"
    HEROIC = "heroic"
    MYSTERIOUS = "mysterious"
    GRIM = "grim"
    URGENT = "urgent"
    WONDROUS = "wondrous"
    QUIET = "quiet"
    TENSE = "tense"
    TRAGIC = "tragic"
    VICTORIOUS = "victorious"

class ConnectionType(str, Enum):
    OPEN_PASSAGE = "open_passage"
    DOOR = "door"
    BLOCKED_DOOR = "blocked_door"
    SECRET_DOOR = "secret_door"
    LADDER = "ladder"
    STAIRS = "stairs"
    SHAFT = "shaft"
    SEWER_TUNNEL = "sewer_tunnel"
    BRIDGE = "bridge"
    FORD = "ford"
    CLIMB_ROUTE = "climb_route"
    FLIGHT_ONLY_ROUTE = "flight_only_route"
    WATER_CHANNEL = "water_channel"
