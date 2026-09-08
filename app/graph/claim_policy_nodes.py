from sqlalchemy.orm import Session

from app.graph.claim_state import ClaimState
from app.services.claim_service import ClaimService


def create_policy_node(db: Session):

    def check_policy_node(state: ClaimState) -> dict:
        service = ClaimService(db)

        claim = service.get_claim(state["claim_id"])

        policy = service.policy_repository.get_by_id(
            claim.policy_id
        )

        return {
            "policy_status": policy.status
        }

    return check_policy_node


def route_after_policy(state: ClaimState) -> str:
    if state["policy_status"] == "ACTIVE":
        return "check_coverage"

    return "make_decision"