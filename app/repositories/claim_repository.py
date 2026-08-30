from sqlalchemy.orm import Session

from app.database.models import Claim


class ClaimRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, claim: Claim) -> Claim:
        try:
            self.db.add(claim)
            self.db.commit()
            self.db.refresh(claim)

            return claim

        except Exception:
            self.db.rollback()
            raise

    def get_by_id(self, claim_id: str) -> Claim | None:
        return (
            self.db.query(Claim)
            .filter(Claim.claim_id == claim_id)
            .first()
        )