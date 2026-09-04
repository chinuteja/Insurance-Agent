from datetime import date

from app.database.models import Customer, Policy
from app.tools.policy_tools import create_policy_tools


def create_test_data(db):
    customer = Customer(
        customer_id="CUS_TEST_TOOL",
        name="Tool Test Customer",
        email="tooltest@example.com",
        phone="5555555555",
    )

    policy = Policy(
        policy_id="POL_TEST_TOOL",
        customer_id="CUS_TEST_TOOL",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS99ZZ9999",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=25000.0,
        coverage_amount=1000000.0,
        status="ACTIVE",
    )

    db.add(customer)
    db.commit()

    db.add(policy)
    db.commit()


def test_get_policy_tool(db):
    create_test_data(db)

    tools = create_policy_tools(db)
    get_policy = tools[0]

    result = get_policy.invoke({
        "policy_id": "POL_TEST_TOOL"
    })

    assert result is not None
    assert result.policy_id == "POL_TEST_TOOL"
    assert result.customer_id == "CUS_TEST_TOOL"
    assert result.status == "ACTIVE"
def test_check_policy_active_tool(db):
    create_test_data(db)

    tools = create_policy_tools(db)
    check_policy_active = tools[1]

    result = check_policy_active.invoke({
        "policy_id": "POL_TEST_TOOL"
    })

    assert result is True

def test_check_incident_coverage_tool(db):
    create_test_data(db)

    tools = create_policy_tools(db)
    check_incident_coverage = tools[2]

    result = check_incident_coverage.invoke({
        "policy_id": "POL_TEST_TOOL",
        "incident_date": "2026-08-15",
    })

    assert result is True