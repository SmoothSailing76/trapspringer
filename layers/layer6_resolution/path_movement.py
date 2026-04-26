from __future__ import annotations

from trapspringer.schemas.actions import Action
from trapspringer.schemas.paths import PathRecord
from trapspringer.schemas.resolution import PrivateOutcome, PublicOutcome, ResolutionResult


def resolve_move_along_path(action: Action, state: dict, map_service, path: PathRecord | dict | None) -> ResolutionResult:
    """Resolve movement by following a previously plotted path."""
    actor = state.get("characters", {}).get(action.actor_id)
    actor_name = getattr(actor, "name", action.actor_id)
    if path is None:
        return ResolutionResult(
            f"RES-{action.action_id}",
            "no_effect",
            PrivateOutcome({"reason": "movement_requires_plotted_path"}),
            PublicOutcome(f"{actor_name} cannot move because no valid path was plotted."),
        )
    pdata = path.as_dict() if hasattr(path, "as_dict") else dict(path)
    waypoints = list(pdata.get("waypoints", []))
    dest = waypoints[-1] if waypoints else pdata.get("goal_square") or pdata.get("target_area")
    scene_id = pdata.get("scene_id") or action.context.scene_id or "DL1_EVENT_1_AMBUSH"
    if map_service and dest:
        try:
            map_service.move_along_path(str(scene_id), action.actor_id, pdata.get("path_id"))
        except Exception:
            try:
                map_service.place_entity(str(scene_id), action.actor_id, str(dest))
            except Exception:
                pass
    mutations = []
    if dest:
        mutations.append({"path": f"characters.{action.actor_id}.location.zone", "value": dest})
    return ResolutionResult(
        f"RES-{action.action_id}",
        "resolved",
        PrivateOutcome({"path": pdata, "moved_to": dest}),
        PublicOutcome(f"{actor_name} follows {pdata.get('path_name', 'the plotted path')} to {str(dest).replace('_', ' ')}."),
        mutations,
    )
