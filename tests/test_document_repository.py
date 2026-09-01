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

def test_get_by_claim_id(db):
    customer = Customer(
        customer_id="CUS_DOC_REPO_TEST",
        name="Document Repository Customer",
        email="docrepo@example.com",
        phone="1111111111",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_DOC_REPO_TEST",
        customer_id="CUS_DOC_REPO_TEST",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS16OP1234",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=25000,
        coverage_amount=800000,
        status="ACTIVE",
    )

    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_DOC_REPO_TEST",
        customer_id="CUS_DOC_REPO_TEST",
        policy_id="POL_DOC_REPO_TEST",
        incident_date=date(2026, 8, 25),
        claim_date=date(2026, 8, 26),
        claim_type="ACCIDENT",
        description="Vehicle damaged",
        claim_amount=100000,
        status="SUBMITTED",
    )

    db.add(claim)
    db.commit()

    document1 = Document(
        document_id="DOC_REPO_TEST_1",
        claim_id="CLM_DOC_REPO_TEST",
        document_type="POLICE_REPORT",
        file_name="police_report.pdf",
        storage_path="/documents/police_report.pdf",
        verification_status="PENDING",
    )

    document2 = Document(
        document_id="DOC_REPO_TEST_2",
        claim_id="CLM_DOC_REPO_TEST",
        document_type="REPAIR_ESTIMATE",
        file_name="repair_estimate.pdf",
        storage_path="/documents/repair_estimate.pdf",
        verification_status="PENDING",
    )

    repository = DocumentRepository(db)

    repository.create(document1)
    repository.create(document2)

    documents = repository.get_by_claim_id("CLM_DOC_REPO_TEST")

    assert len(documents) == 2

    document_ids = {document.document_id for document in documents}

    assert "DOC_REPO_TEST_1" in document_ids
    assert "DOC_REPO_TEST_2" in document_ids