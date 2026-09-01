from sqlalchemy.orm import Session

from app.repositories.customer_repository import CustomerRepository


class CustomerService:

    def __init__(self, db: Session):
        self.repository = CustomerRepository(db)

    def get_customer(self, customer_id: str):
        return self.repository.get_by_id(customer_id)

    def customer_exists(self, customer_id: str) -> bool:
        customer = self.repository.get_by_id(customer_id)

        return customer is not None