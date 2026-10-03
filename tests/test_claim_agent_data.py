from datetime import date

from app.database.models import Customer, Policy, Claim, Document
from app.repositories.claim_repository import ClaimRepository
from app.graph.claim_agent_data import create_claim_data_node


def test_claim_data_node(db):
    customer = Customer(
        customer_id="CUST_DATA_NODE",
        name="Data Node Customer",
        email="data_node@test.com",
        phone="7777777777",
    )
    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_DATA_NODE",
        customer_id="CUST_DATA_NODE",
        policy_type="AUTO",
        vehicle_number="TS09DATA123",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=20000,
        coverage_amount=500000,
        status="ACTIVE",
    )
    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_DATA_NODE",
        customer_id="CUST_DATA_NODE",
        policy_id="POL_DATA_NODE",
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
        document_id="DOC_DATA_NODE",
        claim_id="CLM_DATA_NODE",
        document_type="ACCIDENT_REPORT",
        file_name="accident_report.pdf",
        storage_path="/documents/accident_report.pdf",
        verification_status="VERIFIED",
    )
    db.add(document)
    db.commit()

    data_node = create_claim_data_node(db)

    result = data_node(
        {
            "claim_id": "CLM_DATA_NODE",
            "messages": [],
            "claim": None,
            "policy_active": None,
            "covered": None,
            "documents_present": None,
            "decision": None,
            "decision_reason": None,
        }
    )

    assert result["claim"]["claim_id"] == "CLM_DATA_NODE"
    assert result["claim"]["policy_id"] == "POL_DATA_NODE"
    assert result["claim"]["claim_amount"] == 100000

    assert result["policy_active"] is True
    assert result["covered"] is True
    assert result["documents_present"] is True