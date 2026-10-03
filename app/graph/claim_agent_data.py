from sqlalchemy.orm import Session

from app.graph.claim_agent_state import ClaimAgentState
from app.services.claim_service import ClaimService
from app.services.policy_service import PolicyService
from app.services.document_service import DocumentService


def create_claim_data_node(db: Session):

    def claim_data_node(state: ClaimAgentState) -> dict:
        claim_id = state["claim_id"]

        claim_service = ClaimService(db)
        policy_service = PolicyService(db)
        document_service = DocumentService(db)

        claim = claim_service.get_claim(claim_id)

        policy_active = policy_service.is_policy_active(
            claim.policy_id
        )

        covered = policy_service.is_incident_covered(
            claim.policy_id,
            claim.incident_date,
        )

        documents_present = document_service.has_documents(
            claim_id
        )

        claim_data = {
            "claim_id": claim.claim_id,
            "customer_id": claim.customer_id,
            "policy_id": claim.policy_id,
            "incident_date": str(claim.incident_date),
            "claim_date": str(claim.claim_date),
            "claim_type": claim.claim_type,
            "description": claim.description,
            "claim_amount": claim.claim_amount,
            "status": claim.status,
        }

        return {
            "claim": claim_data,
            "policy_active": policy_active,
            "covered": covered,
            "documents_present": documents_present,
        }

    return claim_data_node