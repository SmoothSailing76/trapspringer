from trapspringer.layers.layer1_authority.models import RulingRecord

class RulingLedger:
    def __init__(self) -> None:
        self._rulings: dict[str, RulingRecord] = {}

    def add(self, ruling: RulingRecord) -> str:
        self._rulings[ruling.ruling_id] = ruling
        return ruling.ruling_id

    def get(self, ruling_id: str) -> RulingRecord | None:
        return self._rulings.get(ruling_id)
