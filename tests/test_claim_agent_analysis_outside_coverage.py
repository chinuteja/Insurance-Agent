
from datetime import date

from app.database.models import Customer, Policy, Claim, Document
from app.graph.claim_agent_graph import create_claim_agent_graph


def test_analysis_with_incident_outside_coverage(db):

    customer = Customer(
        customer_id="CUS_OUTSIDE_TEST",
        name="Outside Coverage Customer",
        email="outside@test.com",
        phone="9999999999",
    )
    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_OUTSIDE_TEST",
        customer_id="CUS_OUTSIDE_TEST",
        policy_type="AUTO",
        vehicle_number="TS09OUT123",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 5, 31),
        premium=20000,
        coverage_amount=500000,
        status="ACTIVE",
    )
    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_OUTSIDE_TEST",
        customer_id="CUS_OUTSIDE_TEST",
        policy_id="POL_OUTSIDE_TEST",
        incident_date=date(2026, 6, 15),
        claim_date=date(2026, 6, 16),
        claim_type="ACCIDENT",
        description="Vehicle accident",
        claim_amount=100000,
        status="SUBMITTED",
    )
    db.add(claim)
    db.commit()

    document = Document(
        document_id="DOC_OUTSIDE_TEST",
        claim_id="CLM_OUTSIDE_TEST",
        document_type="ACCIDENT_REPORT",
        file_name="accident_report.pdf",
        storage_path="/documents/accident_report.pdf",
        verification_status="VERIFIED",
    )
    db.add(document)
    db.commit()

    state = {
        "claim_id": "CLM_OUTSIDE_TEST",
        "messages": [
            "Analyze claim CLM_OUTSIDE_TEST and tell me whether it is eligible."
        ],
        "intent": None,
        "claim": None,
        "policy_active": None,
        "covered": None,
        "documents_present": None,
        "decision": None,
        "decision_reason": None,
    }

    graph = create_claim_agent_graph(db)
    result = graph.invoke(state)

    assert result["intent"] == "ANALYSIS"
    assert result["decision"] == "NEEDS_REVIEW"
    assert "outside" in result["messages"][-1].lower()
