from datetime import date

from app.database.models import Claim, Customer, Policy
from app.repositories.claim_repository import ClaimRepository
from app.graph.llm_agent import create_llm_agent
from app.graph.llm_tool_nodes import create_llm_tool_node


def test_llm_tool_node(db):

    customer = Customer(
        customer_id="CUS_TOOL_NODE",
        name="Tool Node Customer",
        email="tool_node@example.com",
        phone="2222222222",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_TOOL_NODE",
        customer_id="CUS_TOOL_NODE",
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
        claim_id="CLM_TOOL_NODE",
        customer_id="CUS_TOOL_NODE",
        policy_id="POL_TOOL_NODE",
        incident_date=date(2026, 8, 25),
        claim_date=date(2026, 8, 26),
        claim_type="ACCIDENT",
        description="Vehicle damaged in an accident",
        claim_amount=150000,
        status="SUBMITTED",
    )

    repository = ClaimRepository(db)
    repository.create(claim)

    agent = create_llm_agent(db)

    response = agent.invoke(
        "Get claim CLM_TOOL_NODE"
    )

    assert len(response.tool_calls) > 0

    tool_node = create_llm_tool_node(db)

    state = {
        "messages": [
            "Get claim CLM_TOOL_NODE",
            response,
        ]
    }

    result = tool_node(state)

    assert "messages" in result

    assert len(result["messages"]) == 3

    tool_message = result["messages"][-1]

    assert tool_message.tool_call_id == response.tool_calls[0]["id"]

    assert "CLM_TOOL_NODE" in tool_message.content