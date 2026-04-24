from trapspringer.layers.layer2_knowledge.service import KnowledgeService
from trapspringer.schemas.knowledge import KnowledgeQuery


def test_dm_can_see_private_fact_but_players_cannot_until_discovered():
    svc = KnowledgeService()
    dm = svc.filter_for_recipient(KnowledgeQuery("KQ-DM", "dm", ["F-TOEDE-FLEES"]))
    players = svc.filter_for_recipient(KnowledgeQuery("KQ-P", "all_players", ["F-TOEDE-FLEES"]))
    assert len(dm.facts) == 1
    assert players.facts == []

    svc.apply_discovery({"fact_id": "F-TOEDE-FLEES", "discovered_by": "PARTY", "visibility_after": "party_known"})
    players2 = svc.filter_for_recipient(KnowledgeQuery("KQ-P2", "all_players", ["F-TOEDE-FLEES"]))
    assert len(players2.facts) == 1


def test_private_actor_fact_requires_actor_scope_or_communication():
    svc = KnowledgeService()
    svc.add_fact({"fact_id": "F-PRIVATE-CLUE", "proposition": "Tanis noticed a claw mark.", "visibility_class": "dm_private"})
    svc.apply_discovery({"fact_id": "F-PRIVATE-CLUE", "discovered_by": "PC_TANIS", "visibility_after": "actor_private"})
    tanis = svc.filter_for_recipient(KnowledgeQuery("KQ-T", "single_player", ["F-PRIVATE-CLUE"], actor_id="PC_TANIS"))
    public = svc.filter_for_recipient(KnowledgeQuery("KQ-P", "all_players", ["F-PRIVATE-CLUE"]))
    assert len(tanis.facts) == 1
    assert public.facts == []

    svc.propagate_communication({"speaker": "PC_TANIS", "listeners": "PARTY", "content_fact_ids": ["F-PRIVATE-CLUE"]})
    public2 = svc.filter_for_recipient(KnowledgeQuery("KQ-P2", "all_players", ["F-PRIVATE-CLUE"]))
    assert len(public2.facts) == 1
