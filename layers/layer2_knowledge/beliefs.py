class BeliefStore:
    def __init__(self) -> None:
        self.beliefs: dict[str, list[dict[str, object]]] = {}
