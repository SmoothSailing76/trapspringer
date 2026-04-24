def query_reachability(actor: str, destination: str, scene_id: str) -> dict[str, object]:
    return {"actor": actor, "destination": destination, "reachable": False}
