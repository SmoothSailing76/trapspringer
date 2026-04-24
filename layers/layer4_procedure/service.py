from trapspringer.layers.layer4_procedure.frames import build_initial_frame, create_opening_frame
from trapspringer.layers.layer4_procedure.models import ProcedureFrame
from trapspringer.layers.layer4_procedure.transitions import switch_mode
from trapspringer.layers.layer4_procedure.combat import open_combat_frame, lock_declarations, advance_round, end_combat_if_done
from trapspringer.schemas.declarations import DeclarationSet

class ProcedureService:
    def __init__(self) -> None:
        self._frame = build_initial_frame()

    def current_frame(self) -> ProcedureFrame:
        return self._frame

    def create_opening_frame(self, scene_id: str) -> ProcedureFrame:
        self._frame = create_opening_frame(scene_id)
        return self._frame

    def trigger_opening_module_event(self, scene_id: str) -> ProcedureFrame:
        return self.create_opening_frame(scene_id)

    def switch_to_combat_opening_frame(self, scene_id: str) -> ProcedureFrame:
        return self.create_opening_frame(scene_id)

    def open_combat(self, scene_id: str, actor_order: list[str]) -> ProcedureFrame:
        self._frame = open_combat_frame(scene_id, actor_order)
        return self._frame

    def lock_declarations(self, declarations: DeclarationSet) -> ProcedureFrame:
        self._frame = lock_declarations(self._frame, declarations)
        return self._frame

    def advance_combat_round(self) -> ProcedureFrame:
        self._frame = advance_round(self._frame)
        return self._frame

    def end_combat_if_done(self, active_enemies: list[str]) -> ProcedureFrame:
        self._frame = end_combat_if_done(self._frame, active_enemies)
        return self._frame

    def advance_phase(self, context: dict | None = None):
        return self._frame

    def switch_mode(self, transition: dict) -> ProcedureFrame:
        self._frame = switch_mode(self._frame, transition["to_mode"], transition.get("reason"))
        return self._frame
