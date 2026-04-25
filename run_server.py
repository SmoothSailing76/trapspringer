"""Bootstrap script for the Trapspringer Flask dev server.

Locates the trapspringer package root regardless of whether this is run from
the main checkout or a git worktree nested inside it, then starts Flask.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent

# Walk up the tree until we find a directory that contains the trapspringer package.
for _candidate in (_here, _here.parent, _here.parent.parent, _here.parent.parent.parent):
    if (_candidate / "trapspringer" / "__init__.py").exists():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break

from trapspringer.adapters.api.app import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
