from __future__ import annotations

import compileall
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    ok = True
    print("Trapspringer release verification")
    print("- compile check", end=" ... ")
    compiled = compileall.compile_dir(str(ROOT / "trapspringer"), quiet=1)
    print("ok" if compiled else "failed")
    ok = ok and bool(compiled)

    print("- v0.2 main-path run", end=" ... ")
    try:
        from trapspringer.adapters.cli.session_runner import run_v020_main_path_demo
        demo = run_v020_main_path_demo()
        flags = demo.state["module"].world_flags
        qflags = demo.state["module"].quest_flags
        passed = bool(flags.get("epilogue_complete") and qflags.get("medallion_created") and qflags.get("disks_recovered"))
        print("ok" if passed else "failed")
        ok = ok and passed
    except Exception as exc:
        print(f"failed: {exc}")
        ok = False

    print("- integrity", end=" ... ")
    try:
        integrity = demo.integrity or {}
        passed = integrity.get("status") in {"ok", "warning"} and not [i for i in integrity.get("issues", []) if i.get("type") == "sequence_gap"]
        print("ok" if passed else f"issues: {integrity}")
        ok = ok and passed
    except Exception as exc:
        print(f"failed: {exc}")
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
