from trapspringer.schemas.declarations import DeclarationSet
from trapspringer.layers.layer4_procedure.models import ProcedureFrame


def open_combat_frame(scene_id: str, actor_order: list[str]) -> ProcedureFrame:
    return ProcedureFrame("FRAME-DL1-EVENT1-COMBAT", mode="combat", phase="declaration", scene_id=scene_id, active_actor_order=actor_order)


def lock_declarations(frame: ProcedureFrame, declarations: DeclarationSet) -> ProcedureFrame:
    frame.phase = "resolution"
    return frame


def advance_round(frame: ProcedureFrame) -> ProcedureFrame:
    frame.phase = "declaration"
    return frame


def end_combat_if_done(frame: ProcedureFrame, active_enemies: list[str]) -> ProcedureFrame:
    if not active_enemies:
        frame.mode = "travel"
        frame.phase = "aftermath"
    return frame


def next_combat_phase(current: str) -> str:
    if current == "declaration":
        return "resolution"
    if current == "resolution":
        return "round_end"
    return "declaration"
