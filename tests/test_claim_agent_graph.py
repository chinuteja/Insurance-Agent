from datetime import date

from app.database.models import Customer, Policy, Claim
from app.repositories.claim_repository import ClaimRepository
from app.graph.claim_agent_graph import create_claim_agent_graph


def test_claim_agent_graph(db):
    customer = Customer(
        customer_id="CUST_CLAIM_AGENT",
        name="Agent Test Customer",
        email="agent@test.com",
        phone="9999999999",
    )
    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_CLAIM_AGENT",
        customer_id="CUST_CLAIM_AGENT",
        policy_type="AUTO",
        vehicle_number="TS09AG1234",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=20000,
        coverage_amount=500000,
        status="ACTIVE",
    )
    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_CLAIM_AGENT",
        customer_id="CUST_CLAIM_AGENT",
        policy_id="POL_CLAIM_AGENT",
        incident_date=date(2026, 6, 15),
        claim_date=date(2026, 6, 16),
        claim_type="ACCIDENT",
        description="Vehicle accident",
        claim_amount=100000,
        status="SUBMITTED",
    )

    repository = ClaimRepository(db)
    repository.create(claim)

    graph = create_claim_agent_graph(db)

    result = graph.invoke(
        {
            "claim_id": "CLM_CLAIM_AGENT",
            "messages": [
                "Analyze claim CLM_CLAIM_AGENT and tell me whether it can be approved."
            ],
            "claim": None,
            "policy_active": None,
            "covered": None,
            "documents_present": None,
            "decision": None,
        }
    )

    assert "messages" in result
    assert len(result["messages"]) > 1

    final_message = result["messages"][-1]

    assert len(final_message.tool_calls) == 0
    assert "CLM_CLAIM_AGENT" in final_message.content