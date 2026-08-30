from app.database.models import Customer,Policy
from datetime import date


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

def test_policy_model():
    policy = Policy(
        policy_id="POL001",
        customer_id="CUS001",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS09AB1234",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=25000,
        coverage_amount=800000,
        status="ACTIVE",
    )

    assert policy.policy_id == "POL001"
    assert policy.customer_id == "CUS001"
    assert policy.policy_type == "COMPREHENSIVE"
    assert policy.vehicle_number == "TS09AB1234"
    assert policy.premium == 25000
    assert policy.coverage_amount == 800000
    assert policy.status == "ACTIVE"