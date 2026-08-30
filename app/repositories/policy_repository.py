from sqlalchemy.orm import Session

from app.database.models import Policy


class PolicyRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, policy: Policy) -> Policy:
        try:
            self.db.add(policy)
            self.db.commit()
            self.db.refresh(policy)

            return policy
        except Exception:
            self.db.rollback()
            raise

    def get_by_id(self, policy_id: str) -> Policy | None:
        return (
            self.db.query(Policy)
            .filter(Policy.policy_id == policy_id)
            .first()
        )