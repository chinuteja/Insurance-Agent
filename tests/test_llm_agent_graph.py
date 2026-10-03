from datetime import date

from app.database.models import Claim, Customer, Policy
from app.repositories.claim_repository import ClaimRepository
from app.graph.llm_agent_graph import create_llm_agent_graph


def test_llm_agent_graph_end_to_end(db):

    customer = Customer(
        customer_id="CUS_FULL_AGENT",
        name="Full Agent Test Customer",
        email="full_agent@example.com",
        phone="2222222222",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_FULL_AGENT",
        customer_id="CUS_FULL_AGENT",
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
        claim_id="CLM_FULL_AGENT",
        customer_id="CUS_FULL_AGENT",
        policy_id="POL_FULL_AGENT",
        incident_date=date(2026, 8, 25),
        claim_date=date(2026, 8, 26),
        claim_type="ACCIDENT",
        description="Vehicle damaged in an accident",
        claim_amount=150000,
        status="SUBMITTED",
    )

    repository = ClaimRepository(db)
    repository.create(claim)

    graph = create_llm_agent_graph(db)

    state = {
        "messages": [
            "Get claim CLM_FULL_AGENT"
        ]
    }

    result = graph.invoke(state)

    assert "messages" in result

    assert len(result["messages"]) > 1

    final_message = result["messages"][-1]

    assert len(final_message.tool_calls) == 0

    assert "CLM_FULL_AGENT" in final_message.content