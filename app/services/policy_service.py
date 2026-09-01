from datetime import date

from sqlalchemy.orm import Session

from app.repositories.policy_repository import PolicyRepository


class PolicyService:

    def __init__(self, db: Session):
        self.repository = PolicyRepository(db)

    def get_policy(self, policy_id: str):
        return self.repository.get_by_id(policy_id)

    def is_policy_active(self, policy_id: str) -> bool:
        policy = self.repository.get_by_id(policy_id)

        if policy is None:
            return False

        return policy.status == "ACTIVE"

    def is_incident_covered(
        self,
        policy_id: str,
        incident_date: date,
    ) -> bool:
        policy = self.repository.get_by_id(policy_id)

        if policy is None:
            return False

        return policy.start_date <= incident_date <= policy.end_date