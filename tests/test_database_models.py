from app.database.models import Customer


def test_customer_model():
    customer = Customer(
        customer_id="CUS001",
        name="Rahul Sharma",
        email="rahul@example.com",
        phone="9876543210",
    )

    assert customer.customer_id == "CUS001"
    assert customer.name == "Rahul Sharma"
    assert customer.email == "rahul@example.com"
    assert customer.phone == "9876543210"