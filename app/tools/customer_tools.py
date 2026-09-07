from sqlalchemy.orm import Session
from langchain_core.tools import tool

from app.services.customer_service import CustomerService


def create_customer_tools(db: Session):

    @tool
    def get_customer(customer_id: str):
        """
        Retrieve an insurance customer using their customer ID.
        """
        service = CustomerService(db)

        return service.get_customer(customer_id)

    return [
        get_customer,
    ]