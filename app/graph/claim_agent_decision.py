
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

        # If the claim data node explicitly identified a missing claim,
        # preserve that error without performing another lookup.
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

        try:
            is_valid = service.validate_claim(claim_id)

            if is_valid:
                decision = "ELIGIBLE_FOR_REVIEW"
                reason = (
                    "Claim validation passed. "
                    "Policy is active, incident is covered, "
                    "and required documents are present."
                )
            else:
                decision = "NEEDS_REVIEW"
                reason = (
                    "Claim validation failed. "
                    "Incident coverage or required documents "
                    "may not satisfy the validation requirements."
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
