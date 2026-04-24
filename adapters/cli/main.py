from __future__ import annotations

import argparse
from pathlib import Path

from trapspringer.adapters.cli.product_views import render_map_panel, render_party_panel, render_replay_view, render_save_list
from trapspringer.adapters.cli.renderers import render_turn_result, render_status
from trapspringer.adapters.cli.session_runner import run_event1_demo, run_wave6_story_demo, run_wave9_party_demo, run_wave11_quality_demo, run_v020_main_path_demo, run_v030_spatial_demo, run_v040_rules_demo
from trapspringer.services.persistence_service import SessionPersistenceService, SaveLoadError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="trapspringer", description="Trapspringer vertical-slice demos and Wave 10 product tools")
    parser.add_argument("--character", default="PC_TANIS", help="Human-controlled actor id, default PC_TANIS")
    parser.add_argument("--action", default="I attack the nearest hobgoblin", help="One round-one user declaration")
    parser.add_argument("--no-recap", action="store_true", help="Do not print audit recap")
    parser.add_argument("--wave6", action="store_true", help="Run the Wave 6 story demo after Event 1")
    parser.add_argument("--wave9", action="store_true", help="Run the Wave 9 deep party-simulation demo")
    parser.add_argument("--wave11", action="store_true", help="Run Wave 11 hardening/regression quality gates")
    parser.add_argument("--v020", action="store_true", help="Run the v0.2.0 playable DL1 main-path demo")
    parser.add_argument("--v030", action="store_true", help="Run the v0.3 DL1 spatial asset validation demo")
    parser.add_argument("--v040", action="store_true", help="Run the v0.4 AD&D rules coverage demo")
    parser.add_argument("--campaign", choices=["dl1"], default=None, help="Run the named campaign runner")
    parser.add_argument("--demo-main-path", action="store_true", help="Run the complete DL1 v0.2 main path through epilogue")
    parser.add_argument("--status", action="store_true", help="Print campaign status after the run")
    parser.add_argument("--compact", action="store_true", help="Reduce CLI output where supported")
    parser.add_argument("--verbose", action="store_true", help="Increase CLI output where supported")
    parser.add_argument("--save-dir", default=None, help="Directory for JSON save bundles")
    parser.add_argument("--save", action="store_true", help="Save the demo session to --save-dir")
    parser.add_argument("--save-label", default=None, help="Optional save label")
    parser.add_argument("--list-saves", action="store_true", help="List saves in --save-dir and exit")
    parser.add_argument("--load-save", default=None, help="Load and display a save bundle by id or path")
    parser.add_argument("--export-session", default=None, help="Export --load-save to the given JSON path")
    parser.add_argument("--show-party", action="store_true", help="Print a party panel after running or loading")
    parser.add_argument("--show-map", action="store_true", help="Print a map/scene panel after running or loading")
    parser.add_argument("--show-log", action="store_true", help="Print a replay/event-log panel after running or loading")
    parser.add_argument("--public-log", action="store_true", help="When showing log, only include public-table events")
    return parser


def _save_dir(args) -> str | None:
    if args.save or args.list_saves or args.load_save:
        return args.save_dir or "./saves"
    return args.save_dir


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    save_dir = _save_dir(args)
    store = SessionPersistenceService(save_dir or "./saves")

    if args.list_saves:
        print(render_save_list(store.list_saves()))
        return 0

    loaded_bundle = None
    if args.load_save:
        try:
            loaded_bundle = store.load_bundle(args.load_save)
            if args.export_session:
                path = store.export_session(args.load_save, Path(args.export_session))
                print(f"Exported session bundle to {path}")
        except (FileNotFoundError, SaveLoadError) as exc:
            print(f"Could not load save: {exc}")
            return 2
        print(f"Loaded save: {loaded_bundle.get('save_id')} | {loaded_bundle.get('label')} | scene={loaded_bundle.get('active_scene_id')}")
        if args.show_party:
            print("\n" + render_party_panel(loaded_bundle.get("state", {})))
        if args.show_map:
            print("\nMap / Scene")
            print(f"  Active scene: {loaded_bundle.get('active_scene_id')}")
        if args.show_log:
            print("\n" + render_replay_view(loaded_bundle.get("events", []), public_only=args.public_log))
        return 0

    if args.wave11:
        demo = run_wave11_quality_demo()
        print(demo.output)
        return 0
    if args.v030:
        demo = run_v030_spatial_demo()
        print(demo.output)
        return 0
    if args.v040:
        demo = run_v040_rules_demo()
        print(demo.output)
        return 0
    if args.campaign == "dl1" and args.demo_main_path:
        demo = run_v020_main_path_demo(user_character_id=args.character, save_dir=save_dir if args.save else None, save_label=args.save_label)
        for idx, result in enumerate(demo.outputs, start=1):
            if not args.compact:
                print(f"\n--- Main Path {idx} ---")
            print(render_turn_result(result))
    elif args.v020:
        demo = run_v020_main_path_demo(user_character_id=args.character, save_dir=save_dir if args.save else None, save_label=args.save_label)
        for idx, result in enumerate(demo.outputs, start=1):
            print(f"\n--- Main Path {idx} ---")
            print(render_turn_result(result))
    elif args.wave9:
        demo = run_wave9_party_demo(user_character_id=args.character, save_dir=save_dir if args.save else None, save_label=args.save_label)
        for idx, text in enumerate(demo.outputs, start=1):
            print(f"\n--- Party Simulation {idx} ---")
            print(text)
    elif args.wave6:
        demo = run_wave6_story_demo(user_character_id=args.character, save_dir=save_dir if args.save else None, save_label=args.save_label)
        for idx, result in enumerate(demo.outputs, start=1):
            print(f"\n--- Scene {idx} ---")
            print(render_turn_result(result))
    else:
        demo = run_event1_demo(user_input=args.action, user_character_id=args.character, save_dir=save_dir if args.save else None, save_label=args.save_label)
        print(render_turn_result(demo.opening))
        print("\n--- Round 1 ---")
        if demo.round_result:
            print(render_turn_result(demo.round_result))
    if args.status and getattr(demo, "orchestrator", None) is not None:
        print("\n--- Status ---")
        print(render_status(demo.orchestrator.main_path_status()))
    if demo.save_record:
        print("\n--- Saved ---")
        print(f"{demo.save_record['save_id']} -> {demo.save_record['path']}")
    if args.show_party and demo.state is not None:
        print("\n--- Party ---")
        print(render_party_panel(demo.state))
    if args.show_map and demo.orchestrator is not None:
        print("\n--- Map ---")
        print(render_map_panel(demo.orchestrator.layer9, demo.state))
    if args.show_log and demo.orchestrator is not None:
        print("\n--- Replay Log ---")
        print(render_replay_view(demo.orchestrator.layer10.event_log.events, public_only=args.public_log))
    if not args.no_recap:
        print("\n--- Audit recap ---")
        print(demo.recap or "No recap available.")
        print("\n--- Integrity ---")
        print(demo.integrity)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
