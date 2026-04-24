# Public API Facade Contract

## Methods

```python
start_campaign(content_pack_id: str, options: dict) -> CampaignHandle
step(campaign_id: str, input: dict | None = None) -> StepResult
submit_declaration(campaign_id: str, actor_id: str, declaration: str) -> StepResult
save(campaign_id: str, label: str | None = None) -> SaveResult
load(save_path: str) -> CampaignHandle
get_public_state(campaign_id: str) -> PublicStateView
get_actor_state(campaign_id: str, actor_id: str) -> ActorStateView
get_replay(campaign_id: str, scope: str = "public") -> ReplayView
```

## Error Format

```json
{
  "ok": false,
  "error": {
    "code": "UNSUPPORTED_RULE",
    "message": "Psionics are not supported in this build.",
    "details": {
      "rule_id": "psionics",
      "capability_status": "unsupported"
    }
  }
}
```

## Safety

Public output is filtered by Layer 2. Mutations go through orchestrator. Mutating calls create Layer 10 audit events.
