from trapspringer.schemas.knowledge import CommunicationEvent
from trapspringer.layers.layer2_knowledge.facts import FactStore
from trapspringer.layers.layer2_knowledge.discovery import apply_discovery_to_fact


def propagate(store: FactStore, event: CommunicationEvent | dict) -> list[dict[str, object]]:
    if isinstance(event, dict):
        listeners = event.get("listeners", [])
        fact_ids = event.get("content_fact_ids", [])
    else:
        listeners = event.listeners
        fact_ids = event.content_fact_ids
    if listeners == "PARTY":
        listener_list = ["PARTY"]
        visibility = "party_known"
    elif isinstance(listeners, str):
        listener_list = [listeners]
        visibility = "actor_private"
    else:
        listener_list = list(listeners)
        visibility = "actor_private"
    changes = []
    for fact_id in fact_ids:
        fact = store.get(str(fact_id))
        if not fact:
            continue
        apply_discovery_to_fact(fact, listener_list, visibility_after=visibility)
        changes.append({"fact_id": fact_id, "known_by": listener_list, "visibility_after": fact.visibility_class})
    return changes
