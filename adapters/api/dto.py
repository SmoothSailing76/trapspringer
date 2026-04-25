class TurnRequestDTO(dict):
    """Request body for POST /sessions/{id}/turn. Expected key: 'action' (str)."""

class TurnResponseDTO(dict):
    """Response body for turn results. Keys: session_id, narration, prompt, status."""
