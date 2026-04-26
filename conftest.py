import importlib.util
import sys
from pathlib import Path

_worktree = Path(__file__).resolve().parent

if "trapspringer" not in sys.modules:
    spec = importlib.util.spec_from_file_location(
        "trapspringer",
        _worktree / "__init__.py",
        submodule_search_locations=[str(_worktree)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["trapspringer"] = module
    spec.loader.exec_module(module)
