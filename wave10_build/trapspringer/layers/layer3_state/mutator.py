from typing import Any


def _get_child(container: Any, key: str) -> Any:
    if isinstance(container, dict):
        return container[key]
    return getattr(container, key)


def _set_child(container: Any, key: str, value: Any) -> Any:
    if isinstance(container, dict):
        old = container.get(key)
        container[key] = value
        return old
    old = getattr(container, key)
    setattr(container, key, value)
    return old


def apply_mutations(state: dict[str, object], mutation_set: list[dict[str, object]]):
    """Apply simple dotted-path mutations.

    Example: {"path": "characters.PC_TANIS.current_hp", "value": 27}
    """
    diffs = []
    for m in mutation_set:
        path = str(m.get("path", ""))
        if not path:
            continue
        value = m.get("value")
        parts = path.split(".")
        cursor: Any = state
        for part in parts[:-1]:
            cursor = _get_child(cursor, part)
        old = _set_child(cursor, parts[-1], value)
        diffs.append({"path": path, "old": old, "new": value})
    return {"status": "committed", "diffs": diffs}
