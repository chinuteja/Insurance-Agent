from datetime import date

from app.database.models import Claim, Customer, Policy
from app.repositories.claim_repository import ClaimRepository
from app.graph.agent_tool_nodes import create_agent_tool_node


def test_real_agent_tool_node(db):

    customer = Customer(
        customer_id="CUS_AGENT_TEST",
        name="Agent Test Customer",
        email="agent_test@example.com",
        phone="2222222222",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_AGENT_TEST",
        customer_id="CUS_AGENT_TEST",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS14KL1234",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=30000,
        coverage_amount=1000000,
        status="ACTIVE",
    )

    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_AGENT_TEST",
        customer_id="CUS_AGENT_TEST",
        policy_id="POL_AGENT_TEST",
        incident_date=date(2026, 8, 25),
        claim_date=date(2026, 8, 26),
        claim_type="ACCIDENT",
        description="Vehicle damaged in an accident",
        claim_amount=150000,
        status="SUBMITTED",
    )

    repository = ClaimRepository(db)
    repository.create(claim)

    tool_node = create_agent_tool_node(db)

    state = {
        "message": "Process claim CLM_AGENT_TEST",
        "tool_called": "get_claim",
        "tool_result": None,
        "response": None,
    }

    result = tool_node(state)

    assert result["tool_result"] is not None