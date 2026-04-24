from trapspringer.schemas.validation import ValidationRequest, ValidationResult
from trapspringer.layers.layer5_validation.clarification import needs_clarification
from trapspringer.layers.layer5_validation.fictional_checks import check_fictional_legality
from trapspringer.layers.layer5_validation.parser import normalize_action
from trapspringer.layers.layer5_validation.procedural_checks import check_procedural_legality
from trapspringer.layers.layer5_validation.revision_guidance import build_revision_guidance
from trapspringer.layers.layer5_validation.rules_checks import check_rules_legality

class ValidationService:
    def validate_action(self, request: ValidationRequest) -> ValidationResult:
        action = normalize_action(request.action)

        ok, reason = check_procedural_legality(action, request.context)
        if not ok:
            return ValidationResult(request.validation_id, action.action_id, "blocked_by_procedure", human_reason=reason)

        clarify, prompt = needs_clarification(action, request.context)
        if clarify:
            from trapspringer.schemas.validation import ClarificationRequest
            return ValidationResult(
                request.validation_id,
                action.action_id,
                "needs_clarification",
                clarification=ClarificationRequest(clarification_prompt=prompt or "Clarify action."),
            )

        ok, reason = check_fictional_legality(action, request.context)
        if not ok:
            return ValidationResult(request.validation_id, action.action_id, "impossible", human_reason=reason, revision_guidance=build_revision_guidance())

        ok, reason = check_rules_legality(action, request.context)
        if not ok:
            return ValidationResult(request.validation_id, action.action_id, "invalid", human_reason=reason, revision_guidance=build_revision_guidance())

        return ValidationResult(request.validation_id, action.action_id, "valid")
