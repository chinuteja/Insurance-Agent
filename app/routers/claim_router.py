from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.schemas import Claim
from app.services.claim_service import ClaimService
from app.exceptions.business_exceptions import (
    ClaimNotFoundException,
    ClaimNotSubmittedException,
    PolicyNotFoundException,
    PolicyNotActiveException,
)


router = APIRouter(
    prefix="/claims",
    tags=["Claims"]
)


@router.get("/{claim_id}", response_model=Claim)
def get_claim(
    claim_id: str,
    db: Session = Depends(get_db)
):
    service = ClaimService(db)

    try:
        return service.get_claim(claim_id)

    except ClaimNotFoundException as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )


@router.get("/{claim_id}/validate")
def validate_claim(
    claim_id: str,
    db: Session = Depends(get_db)
):
    service = ClaimService(db)

    try:
        is_valid = service.validate_claim(claim_id)

        return {
            "claim_id": claim_id,
            "valid": is_valid
        }

    except ClaimNotFoundException as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

    except (
        ClaimNotSubmittedException,
        PolicyNotFoundException,
        PolicyNotActiveException,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )