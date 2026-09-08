from app.database.models import Customer, Policy, Claim, Document
from app.graph.claim_document_nodes import create_document_node


def test_check_documents_node(db):
    customer = Customer(
        customer_id="CUST_DOCUMENT_NODE_001",
        name="Document Node Customer",
        email="document_node@test.com",
        phone="5555555555",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_DOCUMENT_NODE_001",
        customer_id=customer.customer_id,
        policy_type="CAR",
        vehicle_number="TS13IJ7890",
        start_date="2026-01-01",
        end_date="2026-12-31",
        premium=15000,
        coverage_amount=500000,
        status="ACTIVE",
    )

    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_DOCUMENT_NODE_001",
        customer_id=customer.customer_id,
        policy_id=policy.policy_id,
        incident_date="2026-06-01",
        claim_date="2026-06-02",
        claim_type="ACCIDENT",
        description="Vehicle accident",
        claim_amount=100000,
        status="SUBMITTED",
        fraud_score=None,
        decision=None,
    )

    db.add(claim)
    db.commit()

    document = Document(
        document_id="DOC_DOCUMENT_NODE_001",
        claim_id=claim.claim_id,
        document_type="POLICE_REPORT",
        file_name="police_report.pdf",
        storage_path="/documents/police_report.pdf",
        verification_status="VERIFIED",
    )

    db.add(document)
    db.commit()

    state = {
        "claim_id": "CLM_DOCUMENT_NODE_001",
        "claim_status": "SUBMITTED",
        "policy_status": "ACTIVE",
        "covered": True,
        "documents_present": None,
        "decision": None,
    }

    document_node = create_document_node(db)

    result = document_node(state)

    assert result == {
        "documents_present": True
    }