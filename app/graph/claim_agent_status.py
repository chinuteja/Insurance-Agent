from sqlalchemy.orm import Session

from app.graph.claim_agent_state import ClaimAgentState
from app.services.claim_service import ClaimService


def create_claim_status_node(db: Session):
    service = ClaimService(db)

    def claim_status_node(state: ClaimAgentState) -> dict:
        claim = service.get_claim(state["claim_id"])

        claim_data = {
            "claim_id": claim.claim_id,
            "customer_id": claim.customer_id,
            "policy_id": claim.policy_id,
            "claim_type": claim.claim_type,
            "claim_amount": claim.claim_amount,
            "status": claim.status,
            "incident_date": str(claim.incident_date),
            "claim_date": str(claim.claim_date),
        }

        return {
            "claim": claim_data,
        }

    return claim_status_node