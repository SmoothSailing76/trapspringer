"""Local dev server bootstrap.

The repo root *is* the `trapspringer` package (the `__init__.py` lives at
the project root rather than inside a `trapspringer/` subdirectory). Flask
and other tools that resolve dotted paths can't import
`trapspringer.adapters.api.app` directly because there's no `trapspringer/`
subfolder on disk. This script registers the cwd as the `trapspringer`
package using the same importlib trick conftest.py uses for tests, then
launches the Flask app.

Run with:  python run_server.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent

if "trapspringer" not in sys.modules:
    spec = importlib.util.spec_from_file_location(
        "trapspringer",
        _root / "__init__.py",
        submodule_search_locations=[str(_root)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["trapspringer"] = module
    spec.loader.exec_module(module)

from trapspringer.adapters.api.app import create_app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
