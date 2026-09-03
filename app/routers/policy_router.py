from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.schemas import Policy
from app.services.policy_service import PolicyService


router = APIRouter(
    prefix="/policies",
    tags=["Policies"]
)


@router.get("/{policy_id}", response_model=Policy)
def get_policy(
    policy_id: str,
    db: Session = Depends(get_db)
):
    service = PolicyService(db)

    policy = service.get_policy(policy_id)

    if policy is None:
        raise HTTPException(
            status_code=404,
            detail=f"Policy with ID {policy_id} not found."
        )

    return policy


@router.get("/{policy_id}/active")
def check_policy_active(
    policy_id: str,
    db: Session = Depends(get_db)
):
    service = PolicyService(db)

    policy = service.get_policy(policy_id)

    if policy is None:
        raise HTTPException(
            status_code=404,
            detail=f"Policy with ID {policy_id} not found."
        )

    return {
        "policy_id": policy_id,
        "active": service.is_policy_active(policy_id)
    }


@router.get("/{policy_id}/coverage")
def check_incident_coverage(
    policy_id: str,
    incident_date: date,
    db: Session = Depends(get_db)
):
    service = PolicyService(db)

    policy = service.get_policy(policy_id)

    if policy is None:
        raise HTTPException(
            status_code=404,
            detail=f"Policy with ID {policy_id} not found."
        )

    return {
        "policy_id": policy_id,
        "incident_date": incident_date,
        "covered": service.is_incident_covered(
            policy_id,
            incident_date
        )
    }