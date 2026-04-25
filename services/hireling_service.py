"""Hireling and henchman economy service (DMG hireling rules)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trapspringer.rules import adnd1e_v04
from trapspringer.services.random_service import RandomService

# Daily pay rates in GP (DMG hireling tables, compact approximation).
HIRELING_PAY_RATES: dict[str, int] = {
    "torch_bearer": 1,
    "porter": 2,
    "linkboy": 1,
    "man_at_arms": 2,
    "archer": 4,
    "crossbowman": 3,
    "cavalry": 6,
    "sergeant": 10,
    "scout": 5,
    "sage": 100,
}

# Base morale scores for hireling types (2d6, lower = more reliable).
HIRELING_BASE_MORALE: dict[str, int] = {
    "torch_bearer": 6,
    "porter": 6,
    "linkboy": 5,
    "man_at_arms": 8,
    "archer": 8,
    "crossbowman": 7,
    "cavalry": 9,
    "sergeant": 9,
    "scout": 8,
    "sage": 7,
}


@dataclass
class Hireling:
    hireling_id: str
    hireling_type: str
    name: str
    morale: int
    pay_per_day: int
    days_employed: int = 0
    total_paid_gp: int = 0
    status: str = "active"
    notes: str = ""


@dataclass
class HirelingRoster:
    hirelings: dict[str, Hireling] = field(default_factory=dict)
    _next_id: int = field(default=1, repr=False)

    def add(self, hireling: Hireling) -> None:
        self.hirelings[hireling.hireling_id] = hireling

    def active(self) -> list[Hireling]:
        return [h for h in self.hirelings.values() if h.status == "active"]

    def next_id(self, prefix: str = "HIRE") -> str:
        hid = f"{prefix}-{self._next_id:03d}"
        self._next_id += 1
        return hid


class HirelingService:
    """Manages hireling recruitment, pay, and morale."""

    def __init__(self, rng: RandomService | None = None) -> None:
        self.rng = rng or RandomService(seed=1)
        self.roster = HirelingRoster()

    def recruit(self, hireling_type: str, name: str | None = None, leader_cha: int = 10) -> dict[str, Any]:
        """Attempt to recruit a hireling. Higher CHA improves the reaction roll."""
        htype = hireling_type.lower().replace(" ", "_")
        if htype not in HIRELING_PAY_RATES:
            return {"status": "failed", "reason": f"Unknown hireling type: {htype}"}
        cha_mod = max(0, (leader_cha - 12) // 2)
        reaction = adnd1e_v04.reaction_check(self.rng, modifier=cha_mod, npc_id=f"recruit_{htype}")
        if reaction.result in ("hostile", "unfriendly"):
            return {"status": "refused", "reason": "The hireling declined terms.", "reaction": reaction.result}
        hid = self.roster.next_id()
        base_morale = HIRELING_BASE_MORALE.get(htype, 7)
        morale_bonus = max(0, (leader_cha - 13))
        h = Hireling(
            hireling_id=hid,
            hireling_type=htype,
            name=name or f"{htype.replace('_', ' ').title()} {hid}",
            morale=min(12, base_morale + morale_bonus),
            pay_per_day=HIRELING_PAY_RATES[htype],
        )
        self.roster.add(h)
        return {"status": "recruited", "hireling_id": hid, "name": h.name, "pay_per_day": h.pay_per_day, "morale": h.morale, "reaction": reaction.result}

    def pay_daily(self, days: int = 1) -> dict[str, Any]:
        """Pay all active hirelings for a number of days. Returns total GP spent."""
        total = 0
        records = []
        for h in self.roster.active():
            cost = h.pay_per_day * days
            h.days_employed += days
            h.total_paid_gp += cost
            total += cost
            records.append({"hireling_id": h.hireling_id, "name": h.name, "cost": cost})
        return {"days": days, "total_gp": total, "payments": records}

    def morale_check(self, hireling_id: str, situation_modifier: int = 0) -> dict[str, Any]:
        """Check morale for a specific hireling. Negative modifier = bad situation."""
        h = self.roster.hirelings.get(hireling_id)
        if h is None:
            return {"status": "error", "reason": f"Hireling {hireling_id} not found."}
        check = adnd1e_v04.morale_check(self.rng, h.morale, situation_modifier, group_id=hireling_id)
        if not check.success:
            h.status = "fled"
            h.notes = f"Fled after morale failure (roll {check.roll}, modifier {situation_modifier})."
        return {"hireling_id": hireling_id, "name": h.name, "morale": h.morale, "result": check.result, "success": check.success, "roll": check.roll, "new_status": h.status}

    def check_all_morale_on_pc_death(self) -> list[dict[str, Any]]:
        """Trigger morale checks for all hirelings when a PC dies (DMG: -2 morale modifier)."""
        return [self.morale_check(h.hireling_id, situation_modifier=-2) for h in self.roster.active()]

    def dismiss(self, hireling_id: str) -> dict[str, Any]:
        h = self.roster.hirelings.get(hireling_id)
        if h is None:
            return {"status": "error", "reason": f"Hireling {hireling_id} not found."}
        h.status = "dismissed"
        return {"status": "dismissed", "hireling_id": hireling_id, "name": h.name, "total_days": h.days_employed, "total_paid_gp": h.total_paid_gp}

    def roster_summary(self) -> dict[str, Any]:
        active = self.roster.active()
        daily_cost = sum(h.pay_per_day for h in active)
        return {"active_count": len(active), "daily_cost_gp": daily_cost, "hirelings": [{"id": h.hireling_id, "name": h.name, "type": h.hireling_type, "morale": h.morale, "pay": h.pay_per_day, "status": h.status} for h in self.roster.hirelings.values()]}
