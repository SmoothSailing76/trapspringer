from trapspringer.rules.overrides import KRYNN_OVERRIDES

def get_override(name: str):
    return KRYNN_OVERRIDES.get(name)
