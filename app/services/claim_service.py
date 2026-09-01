from sqlalchemy.orm import Session

from app.exceptions.business_exceptions import ClaimNotFoundException
from app.repositories.claim_repository import ClaimRepository
from app.repositories.policy_repository import PolicyRepository
from app.exceptions.business_exceptions import (
    ClaimNotFoundException,
    ClaimNotSubmittedException,
    PolicyNotFoundException,
    PolicyNotActiveException,
)


class ClaimService:

    def __init__(self, db: Session):
        self.claim_repository = ClaimRepository(db)
        self.policy_repository = PolicyRepository(db)

    def get_claim(self, claim_id: str):
        claim = self.claim_repository.get_by_id(claim_id)

        if claim is None:
            raise ClaimNotFoundException(f"Claim with ID {claim_id} not found.")
        return claim

    def validate_claim(self, claim_id: str) -> bool:
        claim = self.claim_repository.get_by_id(claim_id)

        if claim is None:
            raise ClaimNotFoundException(
                f"Claim with ID {claim_id} not found."
            )

        if claim.status != "SUBMITTED":
            raise ClaimNotSubmittedException(
                f"Claim with ID {claim_id} is not submitted."
            )

        policy = self.policy_repository.get_by_id(claim.policy_id)

        if policy is None:
            raise PolicyNotFoundException(
                f"Policy with ID {claim.policy_id} not found."
            )

        if policy.status != "ACTIVE":
            raise PolicyNotActiveException(
                f"Policy with ID {claim.policy_id} is not active."
            )

        return True