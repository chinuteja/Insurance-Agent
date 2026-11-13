
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

        # Check document verification before claim validation.
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
                    f"Missing required documents: "
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

        try:
            is_valid = service.validate_claim(claim_id)

            if is_valid:
                decision = "ELIGIBLE_FOR_REVIEW"
                reason = (
                    "Claim validation passed. "
    "Policy is active, incident is covered, "
    "and applicable document requirements passed "
    "the current verification checks."
                )
            else:
                decision = "NEEDS_REVIEW"
                reason = (
                    "Claim validation passed. "
    "Policy is active, incident is covered, "
    "and applicable document requirements passed "
    "the current verification checks."
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
