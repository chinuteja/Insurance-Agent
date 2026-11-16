
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

        # 1. Preserve missing claim errors.
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

        # 2. Check whether any agent execution failed.
        agent_errors = state.get("agent_errors") or []

        if agent_errors:
            error_details = "; ".join(
                f"{error.get('agent', 'Unknown agent')}: "
                f"{error.get('error', 'Unknown error')}"
                for error in agent_errors
            )

            return {
                "decision": "NEEDS_REVIEW",
                "decision_reason": (
                    "One or more claim analysis agents failed. "
                    "Automated assessment cannot be trusted. "
                    "Manual review is required. "
                    f"Errors: {error_details}"
                ),
            }

        # 3. Respect the human-review safeguard.
        if state.get("requires_human_review") is True:
            return {
                "decision": "NEEDS_REVIEW",
                "decision_reason": (
                    "The claim analysis workflow flagged this claim "
                    "for human review. Automated processing cannot "
                    "continue."
                ),
            }

        # 4. Verify that both analysis agents completed successfully.
        completed_agents = state.get("completed_agents") or []

        required_agents = {
            "document_verification",
            "fraud_detection",
        }

        missing_agents = required_agents - set(completed_agents)

        if missing_agents:
            return {
                "decision": "NEEDS_REVIEW",
                "decision_reason": (
                    "Required claim assessments were not completed: "
                    f"{', '.join(sorted(missing_agents))}. "
                    "Manual review is required."
                ),
            }

        # 5. Check document verification status.
        document_status = state.get(
            "document_verification_status"
        )

        missing_documents = (
            state.get("missing_documents") or []
        )

        inconsistencies = (
            state.get("document_inconsistencies") or []
        )

        if document_status is None:
            return {
                "decision": "NEEDS_REVIEW",
                "decision_reason": (
                    "Document verification status is unavailable. "
                    "Manual document review is required."
                ),
            }

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

        # 6. Validate fraud risk assessment.
        fraud_score = state.get("fraud_risk_score")
        fraud_level = state.get("fraud_risk_level")

        fraud_recommendation = (
            state.get("fraud_recommendation") or ""
        )

        if fraud_score is None or fraud_level is None:
            return {
                "decision": "NEEDS_REVIEW",
                "decision_reason": (
                    "Fraud risk assessment could not be completed. "
                    "Manual investigation is required."
                ),
            }

        if (
            not isinstance(fraud_score, int)
            or not 0 <= fraud_score <= 100
        ):
            return {
                "decision": "NEEDS_REVIEW",
                "decision_reason": (
                    "Fraud risk assessment returned an invalid score. "
                    "Manual investigation is required."
                ),
            }

        # 7. HIGH risk: escalate for human investigation.
        if fraud_level == "HIGH":
            return {
                "decision": "NEEDS_REVIEW",
                "decision_reason": (
                    f"High fraud risk detected "
                    f"(score: {fraud_score}/100). "
                    "Escalate this claim for human investigation. "
                    f"{fraud_recommendation}"
                ),
            }

        # 8. MEDIUM risk: additional investigation required.
        if fraud_level == "MEDIUM":
            return {
                "decision": "NEEDS_REVIEW",
                "decision_reason": (
                    f"Medium fraud risk detected "
                    f"(score: {fraud_score}/100). "
                    "Additional investigation is required. "
                    f"{fraud_recommendation}"
                ),
            }

        # 9. Only LOW risk proceeds to existing claim validation.
        if fraud_level != "LOW":
            return {
                "decision": "NEEDS_REVIEW",
                "decision_reason": (
                    f"Unrecognized fraud risk level: {fraud_level}. "
                    "Manual investigation is required."
                ),
            }

        # 10. Existing claim validation.
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
