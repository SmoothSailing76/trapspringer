from __future__ import annotations

import random
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class RollRecord:
    roll_id: str
    dice: str
    purpose: str
    raw: list[int]
    total: int
    modifiers: dict[str, int] = field(default_factory=dict)
    visibility: str = "dm_private"


class RandomService:
    """Deterministic RNG with optional replay stream support."""

    def __init__(self, seed: int | None = 1, replay_records: list[dict[str, Any]] | None = None) -> None:
        self.seed = seed
        self._rng = random.Random(seed)
        self._counter = 0
        self.rolls: list[RollRecord] = []
        self._replay_records = list(replay_records or [])
        self._replay_index = 0

    def roll(self, sides: int, purpose: str = "roll", visibility: str = "dm_private") -> int:
        return self.roll_dice(f"1d{sides}", purpose, visibility=visibility).total

    def roll_dice(self, dice: str, purpose: str = "roll", modifiers: dict[str, int] | None = None, visibility: str = "dm_private") -> RollRecord:
        modifiers = modifiers or {}
        if self._replay_index < len(self._replay_records):
            rec = self._from_replay_record(self._replay_records[self._replay_index])
            self._replay_index += 1
            self.rolls.append(rec)
            return rec
        count, sides = self._parse_dice(dice)
        raw = [self._rng.randint(1, sides) for _ in range(count)]
        total = sum(raw) + sum(modifiers.values())
        self._counter += 1
        rec = RollRecord(f"ROLL-{self._counter:06d}", dice, purpose, raw, total, modifiers, visibility)
        self.rolls.append(rec)
        return rec

    def drain_rolls(self) -> list[RollRecord]:
        records = list(self.rolls)
        self.rolls.clear()
        return records

    def export_rolls(self) -> list[dict[str, Any]]:
        return [asdict(r) for r in self.rolls]

    @staticmethod
    def _parse_dice(dice: str) -> tuple[int, int]:
        count_s, sides_s = dice.lower().split("d", 1)
        return int(count_s or "1"), int(sides_s)

    @staticmethod
    def _from_replay_record(data: dict[str, Any]) -> RollRecord:
        return RollRecord(
            roll_id=str(data.get("roll_id")),
            dice=str(data.get("dice")),
            purpose=str(data.get("purpose")),
            raw=[int(x) for x in data.get("raw", [])],
            total=int(data.get("total", 0)),
            modifiers={str(k): int(v) for k, v in (data.get("modifiers", {}) or {}).items()},
            visibility=str(data.get("visibility", "dm_private")),
        )
