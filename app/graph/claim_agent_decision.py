
from sqlalchemy.orm import Session

from app.graph.claim_agent_state import ClaimAgentState
from app.services.claim_service import ClaimService
from app.exceptions.business_exceptions import BusinessException


def create_claim_decision_node(db: Session):

    def claim_decision_node(state: ClaimAgentState) -> dict:
        service = ClaimService(db)
        claim_id = state["claim_id"]

        try:
            is_valid = service.validate_claim(claim_id)

            if is_valid:
                decision = "ELIGIBLE_FOR_REVIEW"
            else:
                decision = "NEEDS_REVIEW"

        except BusinessException as exc:
            decision = "NEEDS_REVIEW"
            return {
                "decision": decision,
                "decision_reason": str(exc),
            }

        return {
            "decision": decision,
        }

    return claim_decision_node
