from trapspringer.layers.layer4_procedure.models import ProcedureFrame

def build_initial_frame() -> ProcedureFrame:
    return ProcedureFrame(frame_id="FRAME-000001", mode="setup", phase="prompt", scene_id=None)

def create_opening_frame(scene_id: str) -> ProcedureFrame:
    return ProcedureFrame(frame_id="FRAME-DL1-EVENT1", mode="combat_opening", phase="scene_entry", scene_id=scene_id)
