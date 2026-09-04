from datetime import date

from sqlalchemy.orm import Session
from langchain_core.tools import tool

from app.services.policy_service import PolicyService


def create_policy_tools(db: Session):

    @tool
    def get_policy(policy_id: str):
        """
        Retrieve an insurance policy using its policy ID.
        """
        service = PolicyService(db)

        return service.get_policy(policy_id)

    @tool
    def check_policy_active(policy_id: str):
        """
        Check whether an insurance policy is currently active.
        """
        service = PolicyService(db)

        return service.is_policy_active(policy_id)

    @tool
    def check_incident_coverage(
        policy_id: str,
        incident_date: date,
    ):
        """
        Check whether an incident date falls within the policy coverage period.
        """
        service = PolicyService(db)

        return service.is_incident_covered(
            policy_id,
            incident_date,
        )

    return [
        get_policy,
        check_policy_active,
        check_incident_coverage,
    ]