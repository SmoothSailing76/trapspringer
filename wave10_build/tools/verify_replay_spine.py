from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EXPECTED = [
    "start_of_event_1", "after_event_1", "goldmoon_joined", "arrival_xak_tsaroth", "after_44f",
    "after_44k_surface", "temple_mishakal", "staff_recharged", "descent_started", "lower_city",
    "secret_route_known", "before_70k", "staff_shattered", "collapse_escape", "epilogue_complete",
]


def main() -> int:
    from trapspringer.adapters.cli.session_runner import run_v020_main_path_demo
    demo = run_v020_main_path_demo()
    checkpoints = demo.orchestrator.layer10.checkpoint_ids()
    missing = [m for m in EXPECTED if m not in checkpoints]
    if missing:
        print("missing checkpoints:", missing)
        return 1
    for milestone in EXPECTED:
        snap = demo.orchestrator.layer10.get_snapshot(milestone)
        if not snap or not snap.get("state_hash"):
            print("bad checkpoint:", milestone)
            return 1
    print("Replay spine checkpoints verified:", len(EXPECTED))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
