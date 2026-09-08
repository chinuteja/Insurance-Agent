from sqlalchemy.orm import Session

from app.graph.claim_state import ClaimState
from app.services.claim_service import ClaimService


def get_claim_node(
    state: ClaimState,
    db: Session,
) -> dict:
    service = ClaimService(db)

    claim = service.get_claim(state["claim_id"])

    return {
        "claim_status": claim.status
    }


def create_claim_nodes(db: Session):

    def claim_node(state: ClaimState) -> dict:
        return get_claim_node(state, db)

    return claim_node