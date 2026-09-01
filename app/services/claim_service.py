from sqlalchemy.orm import Session

from app.repositories.claim_repository import ClaimRepository
from app.repositories.policy_repository import PolicyRepository


class ClaimService:

    def __init__(self, db: Session):
        self.claim_repository = ClaimRepository(db)
        self.policy_repository = PolicyRepository(db)

    def get_claim(self, claim_id: str):
        return self.claim_repository.get_by_id(claim_id)

    def validate_claim(self, claim_id: str) -> bool:
        claim = self.claim_repository.get_by_id(claim_id)

        if claim is None:
            return False

        if claim.status != "SUBMITTED":
            return False

        policy = self.policy_repository.get_by_id(claim.policy_id)

        if policy is None:
            return False

        return policy.status == "ACTIVE"