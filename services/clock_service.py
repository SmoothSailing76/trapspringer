from trapspringer.schemas.state import TimeState

class ClockService:
    def advance_turn(self, time_state: TimeState, turns: int = 1) -> TimeState:
        time_state.turn += turns
        return time_state
