from fastapi.testclient import TestClient

from app.main import app
from app.database.models import Customer


client = TestClient(app)


def create_test_customer(db):
    customer = Customer(
        customer_id="CUS_TEST_API",
        name="Customer API Test",
        email="customer.api@example.com",
        phone="7777777777",
    )

    db.add(customer)
    db.commit()


def test_get_customer_success(db):
    create_test_customer(db)

    response = client.get("/customers/CUS_TEST_API")

    assert response.status_code == 200

    data = response.json()

    assert data["customer_id"] == "CUS_TEST_API"
    assert data["name"] == "Customer API Test"
    assert data["email"] == "customer.api@example.com"
    assert data["phone"] == "7777777777"


def test_get_customer_not_found():
    response = client.get("/customers/CUS_DOES_NOT_EXIST")

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == (
        "Customer with ID CUS_DOES_NOT_EXIST not found."
    )