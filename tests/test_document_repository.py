from datetime import date

from app.database.models import Claim, Customer, Document, Policy
from app.repositories.document_repository import DocumentRepository


def test_create_and_get_document(db):
    # 1. Create customer
    customer = Customer(
        customer_id="CUS_DOCUMENT_TEST",
        name="Document Test Customer",
        email="documenttest@example.com",
        phone="6666666666",
    )

    db.add(customer)
    db.commit()

    # 2. Create policy
    policy = Policy(
        policy_id="POL_DOCUMENT_TEST",
        customer_id="CUS_DOCUMENT_TEST",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS11EF4567",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=28000,
        coverage_amount=900000,
        status="ACTIVE",
    )

    db.add(policy)
    db.commit()

    # 3. Create claim
    claim = Claim(
        claim_id="CLM_DOCUMENT_TEST",
        customer_id="CUS_DOCUMENT_TEST",
        policy_id="POL_DOCUMENT_TEST",
        incident_date=date(2026, 8, 22),
        claim_date=date(2026, 8, 23),
        claim_type="ACCIDENT",
        description="Vehicle damaged in an accident",
        claim_amount=120000,
        status="SUBMITTED",
    )

    db.add(claim)
    db.commit()

    # 4. Create repository
    repository = DocumentRepository(db)

    # 5. Create document
    document = Document(
        document_id="DOC_TEST_001",
        claim_id="CLM_DOCUMENT_TEST",
        document_type="POLICE_REPORT",
        file_name="police_report.pdf",
        storage_path="/documents/CLM_DOCUMENT_TEST/police_report.pdf",
        verification_status="PENDING",
    )

    created_document = repository.create(document)

    assert created_document.document_id == "DOC_TEST_001"
    assert created_document.claim_id == "CLM_DOCUMENT_TEST"

    # 6. Retrieve document
    retrieved_document = repository.get_by_id("DOC_TEST_001")

    assert retrieved_document is not None
    assert retrieved_document.document_id == "DOC_TEST_001"
    assert retrieved_document.claim_id == "CLM_DOCUMENT_TEST"
    assert retrieved_document.document_type == "POLICE_REPORT"
    assert retrieved_document.file_name == "police_report.pdf"
    assert retrieved_document.verification_status == "PENDING"