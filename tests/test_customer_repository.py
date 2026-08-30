from app.database.models import Customer
from app.repositories.customer_repository import CustomerRepository


def test_create_and_get_customer(db):
    repository = CustomerRepository(db)

    customer = Customer(
        customer_id="CUS_TEST_001",
        name="Test Customer",
        email="test@example.com",
        phone="9999999999",
    )

    created_customer = repository.create(customer)

    assert created_customer.customer_id == "CUS_TEST_001"

    retrieved_customer = repository.get_by_id("CUS_TEST_001")

    assert retrieved_customer is not None
    assert retrieved_customer.customer_id == "CUS_TEST_001"
    assert retrieved_customer.name == "Test Customer"
    assert retrieved_customer.email == "test@example.com"