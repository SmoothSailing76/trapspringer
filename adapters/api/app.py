"""FastAPI web adapter for Trapspringer.

Install dependencies: pip install fastapi uvicorn
Run: uvicorn trapspringer.adapters.api.app:app --reload
     (from the parent directory of the trapspringer package)
"""
from __future__ import annotations

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse
    _FASTAPI_AVAILABLE = True
except ImportError:
    _FASTAPI_AVAILABLE = False

from trapspringer.adapters.api.dto import TurnRequestDTO, TurnResponseDTO

_sessions: dict[str, object] = {}


def create_app():
    if not _FASTAPI_AVAILABLE:
        raise ImportError("FastAPI is required: pip install fastapi uvicorn")

    from trapspringer.api import create_api

    app = FastAPI(title="Trapspringer", description="AD&D 1e DL1 simulator API", version="1.0.0")

    @app.get("/", response_class=HTMLResponse)
    def root():
        return """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Trapspringer</title>
<style>
  body{font-family:Georgia,serif;background:#1a1a1a;color:#d4c9a8;max-width:800px;margin:40px auto;padding:20px}
  h1{color:#c8a44a;border-bottom:1px solid #444;padding-bottom:8px}
  .card{background:#252525;border:1px solid #444;border-radius:4px;padding:16px;margin:16px 0}
  .btn{background:#5a3e1b;color:#d4c9a8;border:1px solid #c8a44a;padding:8px 16px;cursor:pointer;font-size:1em;border-radius:3px}
  .btn:hover{background:#7a5a2b}
  #log{white-space:pre-wrap;font-size:.9em;background:#111;padding:12px;border-radius:3px;min-height:200px;max-height:500px;overflow-y:auto}
  input[type=text]{background:#111;color:#d4c9a8;border:1px solid #555;padding:6px 10px;width:calc(100% - 110px);font-size:1em}
  label{color:#a0906a;font-size:.85em}
</style>
</head>
<body>
<h1>⚔ Trapspringer — DL1: Dragons of Despair</h1>
<div class="card">
  <label>Character</label><br>
  <select id="charSel" style="background:#111;color:#d4c9a8;border:1px solid #555;padding:6px;margin:6px 0">
    <option value="PC_TANIS">Tanis Half-Elven (Fighter 5)</option>
    <option value="PC_CARAMON">Caramon (Fighter 6)</option>
    <option value="PC_RAISTLIN">Raistlin (Magic-User 3)</option>
    <option value="PC_GOLDMOON">Goldmoon (Cleric 5)</option>
    <option value="PC_STURM">Sturm (Fighter 6)</option>
    <option value="PC_FLINT">Flint (Fighter 4)</option>
    <option value="PC_TASSLEHOFF">Tasslehoff (Thief 4)</option>
  </select><br>
  <button class="btn" onclick="startCampaign()">Start Campaign</button>
</div>
<div class="card" id="actionCard" style="display:none">
  <label>Your action</label><br>
  <input type="text" id="actionInput" placeholder="I attack the nearest hobgoblin" onkeydown="if(event.key==='Enter')takeTurn()">
  <button class="btn" onclick="takeTurn()">Submit</button>
</div>
<div class="card">
  <div id="log">Welcome to Trapspringer. Start a campaign above.</div>
</div>
<script>
let sessionId = null;
async function startCampaign(){
  const char = document.getElementById('charSel').value;
  const r = await fetch('/sessions', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({character_id: char})});
  const d = await r.json();
  sessionId = d.session_id;
  document.getElementById('actionCard').style.display='block';
  appendLog('=== Campaign started (' + char + ') ===\\n' + (d.narration||''));
}
async function takeTurn(){
  if(!sessionId) return;
  const action = document.getElementById('actionInput').value.trim();
  if(!action) return;
  document.getElementById('actionInput').value='';
  appendLog('\\n> ' + action);
  const r = await fetch('/sessions/' + sessionId + '/turn', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({action})});
  const d = await r.json();
  appendLog((d.narration||'') + (d.prompt ? '\\n\\n' + d.prompt : ''));
}
function appendLog(text){
  const el = document.getElementById('log');
  el.textContent += '\\n' + text;
  el.scrollTop = el.scrollHeight;
}
</script>
</body>
</html>"""

    @app.post("/sessions")
    def start_session(body: dict):
        character_id = body.get("character_id", "PC_TANIS")
        api = create_api()
        session = api.start_campaign(character_id=character_id)
        session_id = session.session_id
        _sessions[session_id] = api
        state_view = api.get_state(session_id)
        return {
            "session_id": session_id,
            "character_id": character_id,
            "narration": state_view.scene_narration if state_view else "Campaign started.",
            "status": "ok",
        }

    @app.post("/sessions/{session_id}/turn")
    def take_turn(session_id: str, body: TurnRequestDTO):
        api = _sessions.get(session_id)
        if api is None:
            raise HTTPException(status_code=404, detail="Session not found.")
        action = body.get("action", "")
        result = api.take_turn(session_id, action)
        return TurnResponseDTO({
            "session_id": session_id,
            "narration": result.narration,
            "prompt": result.prompt,
            "status": result.status,
        })

    @app.get("/sessions/{session_id}")
    def get_session(session_id: str):
        api = _sessions.get(session_id)
        if api is None:
            raise HTTPException(status_code=404, detail="Session not found.")
        state_view = api.get_state(session_id)
        return {"session_id": session_id, "state": state_view.__dict__ if state_view else {}}

    @app.get("/sessions/{session_id}/party")
    def get_party(session_id: str):
        api = _sessions.get(session_id)
        if api is None:
            raise HTTPException(status_code=404, detail="Session not found.")
        state_view = api.get_state(session_id)
        return {"session_id": session_id, "party": state_view.party_summary if state_view else []}

    @app.delete("/sessions/{session_id}")
    def end_session(session_id: str):
        _sessions.pop(session_id, None)
        return {"session_id": session_id, "status": "ended"}

    return app


if _FASTAPI_AVAILABLE:
    app = create_app()
