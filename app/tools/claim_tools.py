from sqlalchemy.orm import Session
from langchain_core.tools import tool

from app.services.claim_service import ClaimService


def create_claim_tools(db: Session):

    @tool
    def get_claim(claim_id: str):
        """
        Retrieve an insurance claim using its claim ID.
        """
        service = ClaimService(db)

        return service.get_claim(claim_id)

    @tool
    def validate_claim(claim_id: str):
        """
        Validate an insurance claim against policy and document requirements.
        """
        service = ClaimService(db)

        return service.validate_claim(claim_id)

    return [
        get_claim,
        validate_claim,
    ]