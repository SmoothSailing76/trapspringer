from __future__ import annotations

import secrets
from typing import Any

from flask import Flask, jsonify, render_template, request, session

from trapspringer.api import create_api

# Server-side session store: sid -> {"api": TrapspringerAPI, "history": list}
_sessions: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------

def _serialize_character(state: dict, actor_id: str) -> dict[str, Any]:
    char = state["characters"].get(actor_id)
    if char is None:
        return {}
    loc = char.location
    return {
        "actor_id": char.actor_id,
        "name": char.name,
        "character_class": char.character_class or "Unknown",
        "level": char.level,
        "current_hp": char.current_hp,
        "max_hp": char.max_hp,
        "ac": char.ac,
        "alignment": char.alignment or "",
        "movement": char.movement,
        "damage": char.damage,
        "inventory": list(char.inventory),
        "spells": list(char.spells),
        "conditions": list(char.conditions),
        "status": char.status,
        "zone": loc.zone if loc else None,
        "area": loc.area_id if loc else None,
    }


def _serialize_party(state: dict) -> list[dict[str, Any]]:
    party = state["party"]
    chars = state["characters"]
    result = []
    for aid in party.member_ids:
        char = chars.get(aid)
        if char is None:
            continue
        result.append({
            "actor_id": char.actor_id,
            "name": char.name,
            "character_class": char.character_class or "?",
            "current_hp": char.current_hp,
            "max_hp": char.max_hp,
            "status": char.status,
        })
    return result


def _serialize_map(api, scene_id: str, state: dict) -> dict[str, Any]:
    graph = api.orchestrator.layer9.scene_graphs.get(scene_id)
    if graph is None:
        return {"scene_id": scene_id, "zones": [], "connections": [], "positions": {}, "teams": {}, "names": {}}
    chars = state.get("characters", {})
    visible_positions = {
        eid: zone
        for eid, zone in graph.positions.items()
        if eid not in graph.hidden_entities
    }
    teams = {eid: getattr(chars.get(eid), "team", "unknown") for eid in visible_positions}
    names = {eid: getattr(chars.get(eid), "name", eid) for eid in visible_positions}
    return {
        "scene_id": graph.scene_id,
        "zones": list(graph.zones),
        "connections": list(graph.connections),
        "positions": visible_positions,
        "teams": teams,
        "names": names,
    }


def _full_response(sid: str) -> dict[str, Any]:
    entry = _sessions[sid]
    api = entry["api"]
    state = api.orchestrator.layer3.read_state()
    scene_id = state["campaign"].active_scene_id
    user_id = api.orchestrator._user_actor_id()
    last = entry["history"][-1] if entry["history"] else {}
    return {
        "narration": last.get("narration"),
        "prompt": last.get("prompt"),
        "character": _serialize_character(state, user_id),
        "party": _serialize_party(state),
        "map": _serialize_map(api, scene_id, state),
        "status": api.status(),
        "history": entry["history"],
        "started": True,
    }


# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------

def register_routes(app: Flask) -> None:

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/start", methods=["POST"])
    def start():
        sid = secrets.token_hex(8)
        session["sid"] = sid
        api = create_api()
        _sessions[sid] = {"api": api, "history": []}
        api.start_campaign("dl1")
        opening = api.step()
        entry = _sessions[sid]
        entry["history"].append({
            "narration": opening.narration,
            "prompt": opening.prompt,
        })
        return jsonify(_full_response(sid))

    @app.route("/api/step", methods=["POST"])
    def step():
        sid = session.get("sid")
        if not sid or sid not in _sessions:
            return jsonify({"error": "No active session. Click 'New Game' to begin."}), 400
        data = request.get_json(silent=True) or {}
        declaration = (data.get("declaration") or "").strip() or None
        api = _sessions[sid]["api"]
        result = api.step(declaration)
        _sessions[sid]["history"].append({
            "narration": result.narration,
            "prompt": result.prompt,
        })
        return jsonify(_full_response(sid))

    @app.route("/api/state")
    def get_state():
        sid = session.get("sid")
        if not sid or sid not in _sessions:
            return jsonify({"started": False})
        return jsonify(_full_response(sid))
