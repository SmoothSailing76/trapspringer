from __future__ import annotations

from typing import Any

from trapspringer.layers.layer1_authority.classifier import classify_question
from trapspringer.layers.layer1_authority.conflict_resolver import resolve_conflict
from trapspringer.layers.layer1_authority.models import CanonAnswer, CanonQuery, AuthorityTrace, RulingRecord
from trapspringer.layers.layer1_authority.precedence import choose_source_for_domain
from trapspringer.layers.layer1_authority.registry import build_default_registry
from trapspringer.layers.layer1_authority.ruling_ledger import RulingLedger
from trapspringer.rules.rule_queries import query_rule, RuleQueryResult
from trapspringer.rules.capabilities import default_rules_capability_registry


class AuthorityService:
    def __init__(self) -> None:
        self.registry = build_default_registry()
        self.rulings = RulingLedger()
        self.capabilities = default_rules_capability_registry()

    def query_authority(self, canon_query: CanonQuery) -> CanonAnswer:
        domain = classify_question(canon_query.question, canon_query.domain)
        selected = choose_source_for_domain(domain)
        selected, needs_ruling = resolve_conflict(selected, [])
        trace = AuthorityTrace(
            selected_source=selected,
            domain=domain,
            precedence_reason="route_by_domain_and_scope_owner",
        )
        return CanonAnswer(
            query_id=canon_query.query_id,
            status="binding" if not needs_ruling else "ruling_required",
            answer=None,
            authority_trace=trace,
            citations=[],
            requires_ruling=needs_ruling,
        )

    def capability_status(self, capability_id: str) -> str:
        return self.capabilities.status(capability_id)

    def require_capability(self, capability_id: str, *, allow_partial: bool = True):
        return self.capabilities.require(capability_id, allow_partial=allow_partial)

    def query_rule(self, name: str, **kwargs: Any) -> RuleQueryResult:
        """Event 1 MVP rule/query endpoint used by validation and resolution.

        Later waves should expand this into fully table-driven PHB/DMG/MM/DL1 lookups.
        """
        return query_rule(name, **kwargs)

    def attack_target_number(self, attacker: Any, target: Any) -> int:
        return int(self.query_rule("attack_matrix", attacker=attacker, target=target).answer)

    def weapon_damage_dice(self, actor: Any) -> str:
        return str(self.query_rule("damage_basis", actor=actor).answer)

    def event1_script(self, script_name: str) -> str | None:
        return self.query_rule(script_name).answer

    def register_ruling(self, ruling: RulingRecord) -> str:
        return self.rulings.add(ruling)
