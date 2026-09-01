from sqlalchemy.orm import Session

from app.repositories.policy_repository import PolicyRepository


class PolicyService:

    def __init__(self, db: Session):
        self.repository = PolicyRepository(db)

    def get_policy(self, policy_id: str):
        return self.repository.get_by_id(policy_id)