from sqlalchemy.orm import Session
from langchain_core.tools import tool

from app.services.claim_service import ClaimService


def create_claim_tools(db: Session):

    @tool
    def get_claim(claim_id: str):
        """Retrieve an insurance claim using its claim ID."""

        service = ClaimService(db)

        claim = service.get_claim(claim_id)

        return {
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

    @tool
    def validate_claim(claim_id: str):
        """Validate an insurance claim against policy and document requirements."""

        service = ClaimService(db)

        return service.validate_claim(claim_id)

    return [get_claim, validate_claim]