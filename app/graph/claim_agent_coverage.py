
from sqlalchemy.orm import Session

from app.graph.claim_agent_state import ClaimAgentState
from app.services.claim_service import ClaimService
from app.services.policy_service import PolicyService


def create_claim_coverage_node(db: Session):
    claim_service = ClaimService(db)
    policy_service = PolicyService(db)

    def claim_coverage_node(state: ClaimAgentState) -> dict:
        claim = claim_service.get_claim(state["claim_id"])

        policy = policy_service.get_policy(claim.policy_id)

        if policy is None:
            return {
                "claim": {
                    "claim_id": claim.claim_id,
                    "policy_id": claim.policy_id,
                },
                "policy_active": False,
                "covered": False,
                "decision_reason": (
                    f"Policy {claim.policy_id} was not found."
                ),
            }

        policy_active = policy_service.is_policy_active(
            claim.policy_id
        )

        covered = policy_service.is_incident_covered(
            claim.policy_id,
            claim.incident_date,
        )

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

        if not policy_active:
            reason = "The policy is not active."
        elif not covered:
            reason = (
                "The incident date falls outside the policy "
                "coverage period."
            )
        else:
            reason = (
                "The incident date falls within the policy "
                "coverage period. This does not guarantee "
                "final claim approval."
            )

        return {
            "claim": claim_data,
            "policy_active": policy_active,
            "covered": covered,
            "decision_reason": reason,
        }

    return claim_coverage_node
