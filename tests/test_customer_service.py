from app.database.models import Customer
from app.repositories.customer_repository import CustomerRepository
from app.services.customer_service import CustomerService


def test_get_customer(db):
    customer = Customer(
        customer_id="CUS_SERVICE_TEST",
        name="Service Test Customer",
        email="servicetest@example.com",
        phone="5555555555",
    )

    repository = CustomerRepository(db)
    repository.create(customer)

    service = CustomerService(db)

    result = service.get_customer("CUS_SERVICE_TEST")

    assert result is not None
    assert result.customer_id == "CUS_SERVICE_TEST"
    assert result.name == "Service Test Customer"
    assert result.email == "servicetest@example.com"