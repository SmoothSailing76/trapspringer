from trapspringer.layers.layer5_validation.service import ValidationService
from trapspringer.schemas.actions import Action, ActionContext
from trapspringer.schemas.validation import ValidationRequest

def test_validation_service_smoke():
    svc = ValidationService()
    action = Action(action_id="A1", actor_id="PC1", action_type="inspect", context=ActionContext(mode="exploration"))
    result = svc.validate_action(ValidationRequest(validation_id="V1", action=action))
    assert result.status == "valid"
