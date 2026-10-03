from datetime import date

from app.database.models import Claim, Customer, Policy
from app.repositories.claim_repository import ClaimRepository
from app.graph.llm_tool_loop import run_llm_tool_loop


def test_llm_can_execute_selected_tool(db):

    customer = Customer(
        customer_id="CUS_LOOP_TEST",
        name="LLM Loop Customer",
        email="llm_loop@example.com",
        phone="2222222222",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_LOOP_TEST",
        customer_id="CUS_LOOP_TEST",
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
        claim_id="CLM_LOOP_TEST",
        customer_id="CUS_LOOP_TEST",
        policy_id="POL_LOOP_TEST",
        incident_date=date(2026, 8, 25),
        claim_date=date(2026, 8, 26),
        claim_type="ACCIDENT",
        description="Vehicle damaged in an accident",
        claim_amount=150000,
        status="SUBMITTED",
    )

    repository = ClaimRepository(db)
    repository.create(claim)

    result = run_llm_tool_loop(
        db,
        "Get claim CLM_LOOP_TEST",
    )

    assert isinstance(result, str)

    assert len(result) > 0

    assert "CLM_LOOP_TEST" in result
