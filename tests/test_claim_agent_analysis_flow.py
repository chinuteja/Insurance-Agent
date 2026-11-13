
from datetime import date

from app.database.models import Customer, Policy, Claim, Document
from app.graph.claim_agent_graph import create_claim_agent_graph


def test_claim_agent_analysis_flow(db):
    customer = Customer(
        customer_id="CUS_ANALYSIS_E2E",
        name="Analysis Customer",
        email="analysis@test.com",
        phone="9999999993",
    )
    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_ANALYSIS_E2E",
        customer_id=customer.customer_id,
        policy_type="MOTOR",
        vehicle_number="TS09MN1234",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=15000,
        coverage_amount=500000,
        status="ACTIVE",
    )
    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_ANALYSIS_E2E",
        customer_id=customer.customer_id,
        policy_id=policy.policy_id,
        incident_date=date(2026, 9, 1),
        claim_date=date(2026, 9, 2),
        claim_type="ACCIDENT",
        description="Vehicle accident",
        claim_amount=100000,
        status="SUBMITTED",
        fraud_score=0.0,
        decision=None,
    )
    db.add(claim)
    db.commit()

    document = Document(
        document_id="DOC_ANALYSIS_E2E",
        claim_id=claim.claim_id,
        document_type="POLICE_REPORT",
        file_name="police_report.pdf",
        storage_path="documents/police_report.pdf",
        verification_status="VERIFIED",
    )
    db.add(document)
    db.commit()

    graph = create_claim_agent_graph(db)

    state = {
        "claim_id": claim.claim_id,
        "messages": [
            f"Analyze claim {claim.claim_id} and explain whether it is eligible for review."
        ],
        "intent": None,
        "claim": None,
        "policy_active": None,
        "covered": None,
        "documents_present": None,
        "decision": None,
        "decision_reason": None,
    }

    result = graph.invoke(state)

    assert result["intent"] == "ANALYSIS"
    assert result["claim"]["claim_id"] == claim.claim_id
    assert result["policy_active"] is True
    assert result["covered"] is True
    assert result["documents_present"] is True

    # Document verification must prevent premature eligibility.
    assert result["document_verification_status"] == "INCOMPLETE"
    assert result["decision"] == "NEEDS_REVIEW"

    assert len(result["missing_documents"]) == 5
    assert len(result["messages"]) > 1
