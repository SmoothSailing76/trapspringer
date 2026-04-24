from trapspringer.schemas.state import TimeState

def advance_time(time_state: TimeState, *, turns: int = 0, rounds: int = 0) -> TimeState:
    time_state.turn += turns
    time_state.round += rounds
    return time_state
