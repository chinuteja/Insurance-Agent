from datetime import date

from app.database.models import Customer, Policy, Claim, Document
from app.repositories.claim_repository import ClaimRepository
from app.graph.claim_agent_decision import create_claim_decision_node


def test_claim_decision_eligible(db):
    customer = Customer(
        customer_id="CUST_DECISION",
        name="Decision Test Customer",
        email="decision@test.com",
        phone="9999999999",
    )
    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_DECISION",
        customer_id="CUST_DECISION",
        policy_type="AUTO",
        vehicle_number="TS09DEC123",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=20000,
        coverage_amount=500000,
        status="ACTIVE",
    )
    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_DECISION",
        customer_id="CUST_DECISION",
        policy_id="POL_DECISION",
        incident_date=date(2026, 6, 15),
        claim_date=date(2026, 6, 16),
        claim_type="ACCIDENT",
        description="Vehicle accident",
        claim_amount=100000,
        status="SUBMITTED",
    )

    repository = ClaimRepository(db)
    repository.create(claim)

    document = Document(
        document_id="DOC_DECISION",
        claim_id="CLM_DECISION",
        document_type="ACCIDENT_REPORT",
        file_name="accident_report.pdf",
        storage_path="/documents/accident_report.pdf",
        verification_status="VERIFIED",
    )
    db.add(document)
    db.commit()

    decision_node = create_claim_decision_node(db)

    result = decision_node(
        {
            "claim_id": "CLM_DECISION",
            "messages": [],
            "claim": None,
            "policy_active": None,
            "covered": None,
            "documents_present": None,
            "decision": None,
            "decision_reason": None,
        }
    )

    assert result["decision"] == "ELIGIBLE_FOR_REVIEW"