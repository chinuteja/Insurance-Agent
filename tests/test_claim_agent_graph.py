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
            "decision_reason": None,
            "intent": None,
        }
    )

    assert "messages" in result
    assert len(result["messages"]) > 1

    final_message = result["messages"][-1]

    assert isinstance(final_message, str)
    assert "CLM_CLAIM_AGENT" in final_message
    assert "review" in final_message.lower()

        # Verify document verification ran
    assert "document_verification_status" in result
    assert result["document_verification_status"] == "INCOMPLETE"

    # Verify fraud detection ran
    assert "fraud_risk_score" in result
    assert "fraud_risk_level" in result
    assert "fraud_findings" in result
    assert "fraud_recommendation" in result

    # Verify supervisor execution tracking
    assert "agent_results" in result
    assert "completed_agents" in result

    # Claim data tracking
    assert "data" in result["completed_agents"]
    assert result["agent_results"]["data"]["claim"]["claim_id"] == (
        "CLM_CLAIM_AGENT"
    )

    # Document verification tracking
    assert "document_verification" in result["completed_agents"]
    assert (
        result["agent_results"]["document_verification"][
            "document_verification_status"
        ]
        == "INCOMPLETE"
    )

    # Fraud detection tracking
    assert "fraud_detection" in result["completed_agents"]
    assert (
        result["agent_results"]["fraud_detection"]["fraud_risk_score"]
        == result["fraud_risk_score"]
    )

    # All three components should have finished
    assert result["current_agent"] is None


    # Missing mandatory documents must prevent eligibility
    assert result["decision"] == "NEEDS_REVIEW"