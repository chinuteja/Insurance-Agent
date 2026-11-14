
from datetime import date, timedelta

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

    def find_duplicate_claim(
        self,
        policy_id: str,
        incident_date: date,
        claim_type: str,
        exclude_claim_id: str | None = None,
    ) -> bool:
        """
        Check whether another claim exists with the same
        policy, incident date, and claim type.
        """

        query = self.db.query(Claim).filter(
            Claim.policy_id == policy_id,
            Claim.incident_date == incident_date,
            Claim.claim_type == claim_type,
        )

        if exclude_claim_id:
            query = query.filter(
                Claim.claim_id != exclude_claim_id
            )

        return query.first() is not None

    def count_recent_claims(
        self,
        customer_id: str,
        reference_date: date,
        window_days: int = 90,
        exclude_claim_id: str | None = None,
    ) -> int:
        """
        Count other claims submitted by the customer
        within the previous configured number of days.
        """

        if window_days <= 0:
            raise ValueError("Window days must be greater than zero.")

        start_date = reference_date - timedelta(days=window_days)

        query = self.db.query(Claim).filter(
            Claim.customer_id == customer_id,
            Claim.claim_date >= start_date,
            Claim.claim_date <= reference_date,
        )

        if exclude_claim_id:
            query = query.filter(
                Claim.claim_id != exclude_claim_id
            )

        return query.count()
