from sqlalchemy.orm import Session

from app.database.models import Customer


class CustomerRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, customer: Customer) -> Customer:
        try:
            self.db.add(customer)
            self.db.commit()
            self.db.refresh(customer)

            return customer
        except Exception:
            self.db.rollback()
            raise

 

    def get_by_id(self, customer_id: str) -> Customer | None:
        return (
            self.db.query(Customer)
            .filter(Customer.customer_id == customer_id)
            .first()
        )