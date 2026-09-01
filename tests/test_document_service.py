from datetime import date

from app.database.models import Claim, Customer, Document, Policy
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService


def test_get_document(db):
    customer = Customer(
        customer_id="CUS_DOCUMENT_SERVICE_TEST",
        name="Document Service Customer",
        email="documentservice@example.com",
        phone="1111111111",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_DOCUMENT_SERVICE_TEST",
        customer_id="CUS_DOCUMENT_SERVICE_TEST",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS15MN1234",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=28000,
        coverage_amount=900000,
        status="ACTIVE",
    )

    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_DOCUMENT_SERVICE_TEST",
        customer_id="CUS_DOCUMENT_SERVICE_TEST",
        policy_id="POL_DOCUMENT_SERVICE_TEST",
        incident_date=date(2026, 8, 27),
        claim_date=date(2026, 8, 28),
        claim_type="ACCIDENT",
        description="Vehicle damaged in an accident",
        claim_amount=120000,
        status="SUBMITTED",
    )

    db.add(claim)
    db.commit()

    document = Document(
        document_id="DOC_SERVICE_TEST",
        claim_id="CLM_DOCUMENT_SERVICE_TEST",
        document_type="POLICE_REPORT",
        file_name="police_report.pdf",
        storage_path="/documents/CLM_DOCUMENT_SERVICE_TEST/police_report.pdf",
        verification_status="PENDING",
    )

    repository = DocumentRepository(db)
    repository.create(document)

    service = DocumentService(db)

    result = service.get_document("DOC_SERVICE_TEST")

    assert result is not None
    assert result.document_id == "DOC_SERVICE_TEST"
    assert result.claim_id == "CLM_DOCUMENT_SERVICE_TEST"
    assert result.document_type == "POLICE_REPORT"
    assert result.file_name == "police_report.pdf"
    assert result.verification_status == "PENDING"


def test_has_documents_returns_true_when_documents_exist(db):
    customer = Customer(
        customer_id="CUS_HAS_DOC_TEST",
        name="Has Document Customer",
        email="hasdoc@example.com",
        phone="1111111112",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_HAS_DOC_TEST",
        customer_id="CUS_HAS_DOC_TEST",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS15MN5678",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=28000,
        coverage_amount=900000,
        status="ACTIVE",
    )

    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_HAS_DOC_TEST",
        customer_id="CUS_HAS_DOC_TEST",
        policy_id="POL_HAS_DOC_TEST",
        incident_date=date(2026, 8, 27),
        claim_date=date(2026, 8, 28),
        claim_type="ACCIDENT",
        description="Vehicle damaged",
        claim_amount=120000,
        status="SUBMITTED",
    )

    db.add(claim)
    db.commit()

    document = Document(
        document_id="DOC_HAS_DOC_TEST",
        claim_id="CLM_HAS_DOC_TEST",
        document_type="POLICE_REPORT",
        file_name="police_report.pdf",
        storage_path="/documents/police_report.pdf",
        verification_status="PENDING",
    )

    repository = DocumentRepository(db)
    repository.create(document)

    service = DocumentService(db)

    result = service.has_documents("CLM_HAS_DOC_TEST")

    assert result is True


def test_has_documents_returns_false_when_no_documents_exist(db):
    customer = Customer(
        customer_id="CUS_NO_DOC_TEST",
        name="No Document Customer",
        email="nodoc@example.com",
        phone="1111111113",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_NO_DOC_TEST",
        customer_id="CUS_NO_DOC_TEST",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS15MN9999",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=28000,
        coverage_amount=900000,
        status="ACTIVE",
    )

    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_NO_DOC_TEST",
        customer_id="CUS_NO_DOC_TEST",
        policy_id="POL_NO_DOC_TEST",
        incident_date=date(2026, 8, 27),
        claim_date=date(2026, 8, 28),
        claim_type="ACCIDENT",
        description="Vehicle damaged",
        claim_amount=120000,
        status="SUBMITTED",
    )

    db.add(claim)
    db.commit()

    service = DocumentService(db)

    result = service.has_documents("CLM_NO_DOC_TEST")

    assert result is False