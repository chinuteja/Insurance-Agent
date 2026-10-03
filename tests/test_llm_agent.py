from datetime import date

from app.database.models import Claim, Customer, Policy
from app.repositories.claim_repository import ClaimRepository
from app.graph.llm_agent import create_llm_agent


def test_llm_agent_requests_get_claim(db):

    customer = Customer(
        customer_id="CUS_LLM_AGENT",
        name="LLM Agent Test Customer",
        email="llm_agent@example.com",
        phone="2222222222",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_LLM_AGENT",
        customer_id="CUS_LLM_AGENT",
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
        claim_id="CLM_LLM_AGENT",
        customer_id="CUS_LLM_AGENT",
        policy_id="POL_LLM_AGENT",
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
        "Get claim CLM_LLM_AGENT"
    )

    assert len(response.tool_calls) > 0

    assert response.tool_calls[0]["name"] == "get_claim"

    assert response.tool_calls[0]["args"]["claim_id"] == "CLM_LLM_AGENT"