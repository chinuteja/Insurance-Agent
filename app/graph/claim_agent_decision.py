
from sqlalchemy.orm import Session

from app.graph.claim_agent_state import ClaimAgentState
from app.services.claim_service import ClaimService
from app.exceptions.business_exceptions import (
    BusinessException,
    ClaimNotFoundException,
)


def create_claim_decision_node(db: Session):

    def claim_decision_node(state: ClaimAgentState) -> dict:

        claim_id = state["claim_id"]
        service = ClaimService(db)

        # Preserve missing claim errors.
        reason = state.get("decision_reason", "")

        if (
            state.get("claim") is None
            and reason
            and "couldn't find claim" in reason.lower()
        ):
            return {
                "decision": "NEEDS_REVIEW",
                "decision_reason": reason,
            }

        # Check document verification first.
        document_status = state.get(
            "document_verification_status"
        )

        missing_documents = state.get(
            "missing_documents"
        ) or []

        inconsistencies = state.get(
            "document_inconsistencies"
        ) or []

        if document_status == "INCOMPLETE":
            return {
                "decision": "NEEDS_REVIEW",
                "decision_reason": (
                    "Document verification is incomplete. "
                    "Missing required documents: "
                    f"{', '.join(missing_documents)}."
                ),
            }

        if inconsistencies:
            return {
                "decision": "NEEDS_REVIEW",
                "decision_reason": (
                    "Document inconsistencies were detected: "
                    f"{'; '.join(inconsistencies)}."
                ),
            }

        if document_status in ("NEEDS_REVIEW", "INVALID"):
            return {
                "decision": "NEEDS_REVIEW",
                "decision_reason": (
                    "Document verification requires manual review. "
                    f"{state.get('document_recommendation') or ''}"
                ),
            }

        # Fraud risk assessment.
        fraud_score = state.get("fraud_risk_score")
        fraud_level = state.get("fraud_risk_level")

        fraud_recommendation = (
            state.get("fraud_recommendation") or ""
        )

        # Do not proceed if fraud assessment is unavailable.
        if fraud_score is None or fraud_level is None:
            return {
                "decision": "NEEDS_REVIEW",
                "decision_reason": (
                    "Fraud risk assessment could not be completed. "
                    "Manual investigation is required."
                ),
            }

        if not isinstance(fraud_score, int) or not 0 <= fraud_score <= 100:
            return {
                "decision": "NEEDS_REVIEW",
                "decision_reason": (
                    "Fraud risk assessment returned an invalid score. "
                    "Manual investigation is required."
                ),
            }

        # HIGH risk: escalate for human investigation.
        if fraud_level == "HIGH":
            return {
                "decision": "NEEDS_REVIEW",
                "decision_reason": (
                    f"High fraud risk detected (score: {fraud_score}/100). "
                    "Escalate this claim for human investigation. "
                    f"{fraud_recommendation}"
                ),
            }

        # MEDIUM risk: additional investigation required.
        if fraud_level == "MEDIUM":
            return {
                "decision": "NEEDS_REVIEW",
                "decision_reason": (
                    f"Medium fraud risk detected (score: {fraud_score}/100). "
                    "Additional investigation is required. "
                    f"{fraud_recommendation}"
                ),
            }

        # Only LOW risk proceeds to existing claim validation.
        if fraud_level != "LOW":
            return {
                "decision": "NEEDS_REVIEW",
                "decision_reason": (
                    f"Unrecognized fraud risk level: {fraud_level}. "
                    "Manual investigation is required."
                ),
            }

        # Existing claim validation.
        try:
            is_valid = service.validate_claim(claim_id)

            if is_valid:
                decision = "ELIGIBLE_FOR_REVIEW"
                reason = (
                    "Claim validation passed. Policy is active, "
                    "incident is covered, and applicable document "
                    "requirements passed the current verification checks. "
                    f"Fraud risk is LOW ({fraud_score}/100)."
                )
            else:
                decision = "NEEDS_REVIEW"
                reason = (
                    "Claim validation did not pass. "
                    "Further review of policy and coverage conditions "
                    "is required."
                )

        except ClaimNotFoundException as exc:
            decision = "NEEDS_REVIEW"
            reason = str(exc)

        except BusinessException as exc:
            decision = "NEEDS_REVIEW"
            reason = str(exc)

        return {
            "decision": decision,
            "decision_reason": reason,
        }

    return claim_decision_node
