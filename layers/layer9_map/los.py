
def query_los(graph, observer: str, target: str, include_concealed: bool = False) -> dict[str, object]:
    if graph is None:
        return {"visible": False, "result": "not_visible", "reason": "no_scene_graph"}
    return graph.visibility_detail(observer, target, include_concealed=include_concealed)
