from sqlalchemy.orm import Session

from app.graph.claim_state import ClaimState
from app.services.claim_service import ClaimService


def create_coverage_node(db: Session):

    def check_coverage_node(state: ClaimState) -> dict:
        service = ClaimService(db)

        claim = service.get_claim(state["claim_id"])

        covered = service.policy_repository.get_by_id(
            claim.policy_id
        )

        if covered is None:
            return {
                "covered": False
            }

        return {
            "covered": (
                covered.start_date
                <= claim.incident_date
                <= covered.end_date
            )
        }

    return check_coverage_node