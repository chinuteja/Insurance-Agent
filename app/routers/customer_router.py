from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import Customer
from app.database.connection import get_db
from app.services.customer_service import CustomerService


router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


@router.get("/{customer_id}", response_model=Customer)
def get_customer(
    customer_id: str,
    db: Session = Depends(get_db)
):
    service = CustomerService(db)

    customer = service.get_customer(customer_id)

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail=f"Customer with ID {customer_id} not found."
        )

    return customer