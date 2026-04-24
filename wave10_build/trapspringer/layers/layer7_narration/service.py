from trapspringer.schemas.narration import NarrationRequest, NarrationResult
from trapspringer.layers.layer7_narration.prompts import render_prompt_text
from trapspringer.layers.layer7_narration.combat_text import render_combat_results, render_round_prompt, render_invalid_action
from trapspringer.schemas.resolution import ResolutionResult
from trapspringer.schemas.validation import ValidationResult

class NarrationService:
    def narrate(self, request: NarrationRequest) -> NarrationResult:
        return NarrationResult(narration_id=request.narration_id, spoken_text="Narration not yet implemented.")

    def prompt(self, request: NarrationRequest) -> NarrationResult:
        prompt = render_prompt_text(request)
        return NarrationResult(narration_id=request.narration_id, spoken_text=prompt, prompt=prompt)

    def recap(self, request: NarrationRequest) -> NarrationResult:
        return NarrationResult(narration_id=request.narration_id, spoken_text="Recap not yet implemented.")

    def narrate_event_1_open(self, scene_content: dict) -> NarrationResult:
        text = scene_content.get("read_aloud", "The road is suddenly blocked.")
        line = scene_content.get("toede_opening_line")
        exit_line = scene_content.get("toede_exit_line")
        spoken = f"{text}\n\nToede says, \"{line}\"\n{exit_line}"
        return NarrationResult(
            narration_id="NAR-DL1-EVENT1-OPEN",
            spoken_text=spoken,
            prompt="You are surrounded. Declare your first actions."
        )

    def narrate_scene_open(self, scene_content: dict) -> NarrationResult:
        sid = scene_content.get("scene_id", "SCENE")
        text = str(scene_content.get("read_aloud", "The scene opens."))
        if sid == "DL1_EVENT_2_GOLDMOON":
            line = scene_content.get("goldmoon_opening_line")
            spoken = f"{text}\n\nGoldmoon says, \"{line}\""
            return NarrationResult("NAR-DL1-EVENT2-OPEN", spoken_text=spoken, prompt="Do you invite Goldmoon and Riverwind to join the party?")
        if sid == "DL1_AREA_44F":
            return NarrationResult("NAR-DL1-44F-OPEN", spoken_text=text, prompt="The dragon shape, huts, cage, and bonfire are visible. What do you inspect?")
        if sid == "DL1_AREA_44K":
            return NarrationResult("NAR-DL1-44K-OPEN", spoken_text=text, prompt="The well, temple doors, and plaza are before you. What do you do?")
        return NarrationResult(f"NAR-{sid}-OPEN", spoken_text=text, prompt="What do you do?")

    def prompt_scene(self, frame, scene_content: dict | None = None) -> NarrationResult:
        if frame.scene_id == "DL1_EVENT_1_AMBUSH" and scene_content:
            return self.narrate_event_1_open(scene_content)
        if scene_content:
            return self.narrate_scene_open(scene_content)
        return NarrationResult(narration_id="NAR-PROMPT-000001", spoken_text=f"Mode: {frame.mode}.", prompt="What do you do?")

    def basic_acknowledgement(self, user_input: str) -> NarrationResult:
        return NarrationResult(narration_id="NAR-ACK-000001", spoken_text=f"Received: {user_input}", prompt="Continue.")

    def narrate_invalid_action(self, validation: ValidationResult) -> NarrationResult:
        text = render_invalid_action(validation.human_reason)
        return NarrationResult("NAR-INVALID-ACTION", spoken_text=text, prompt="Revise your action.")

    def narrate_resolution(self, result: ResolutionResult, prompt: str = "What do you do next?") -> NarrationResult:
        return NarrationResult(f"NAR-{result.resolution_id}", spoken_text=result.public_outcome.narration or "", prompt=prompt)

    def narrate_combat_results(self, results: list[ResolutionResult], round_no: int = 1, combat_done: bool = False) -> NarrationResult:
        text = render_combat_results(results)
        if combat_done:
            prompt = "The road falls quiet. What do you do next?"
        else:
            prompt = render_round_prompt(round_no + 1)
        return NarrationResult("NAR-COMBAT-RESULTS", spoken_text=text, prompt=prompt)
