from sqlalchemy.orm import Session

from app.repositories.claim_repository import ClaimRepository


class ClaimService:

    def __init__(self, db: Session):
        self.repository = ClaimRepository(db)

    def get_claim(self, claim_id: str):

        claim = self.repository.get_by_id(claim_id)
        if claim is None:
            return False
        return claim.status == "SUBMITTED"