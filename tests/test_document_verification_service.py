
from datetime import date

import pytest

from app.database.models import Customer, Policy, Claim, Document
from app.services.document_verification_service import (
    DocumentVerificationService,
)
from app.exceptions.business_exceptions import ClaimNotFoundException



def create_claim(db, claim_id, documents=None):

    customer_id = f"CUS_{claim_id}"
    policy_id = f"POL_{claim_id}"

    # Step 1: Create customer.
    customer = Customer(
        customer_id=customer_id,
        name="Verification Test Customer",
        email=f"{claim_id.lower()}@example.com",
        phone="1111111111",
    )

    db.add(customer)
    db.flush()

    # Step 2: Create policy.
    policy = Policy(
        policy_id=policy_id,
        customer_id=customer_id,
        policy_type="COMPREHENSIVE",
        vehicle_number="TS15MN1234",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=28000,
        coverage_amount=900000,
        status="ACTIVE",
    )

    db.add(policy)
    db.flush()

    # Step 3: Create claim.
    claim = Claim(
        claim_id=claim_id,
        customer_id=customer_id,
        policy_id=policy_id,
        incident_date=date(2026, 8, 27),
        claim_date=date(2026, 8, 28),
        claim_type="ACCIDENT",
        description="Vehicle damaged in an accident",
        claim_amount=120000,
        status="SUBMITTED",
    )

    db.add(claim)
    db.flush()

    # Step 4: Create submitted documents.
    if documents:
        for document in documents:
            db.add(
                Document(
                    document_id=document["document_id"],
                    claim_id=claim_id,
                    document_type=document["document_type"],
                    file_name=document["file_name"],
                    storage_path=document["storage_path"],
                    verification_status="PENDING",
                )
            )

        db.flush()

    db.commit()

    return claim


def test_claim_not_found(db):

    service = DocumentVerificationService(db)

    with pytest.raises(ClaimNotFoundException):
        service.verify_claim_documents("INVALID_CLAIM_ID")


def test_all_documents_missing(db):

    create_claim(
        db,
        "CLM_ALL_DOCS_MISSING",
    )

    service = DocumentVerificationService(db)

    result = service.verify_claim_documents(
        "CLM_ALL_DOCS_MISSING"
    )

    assert result.overall_status == "INCOMPLETE"
    assert len(result.missing_documents) == 6
    assert len(result.documents) == 6


def test_one_document_submitted_and_extracted(db, tmp_path):

    file_path = tmp_path / "police_report.txt"

    file_path.write_text(
        "Vehicle accident occurred on 27 August 2026.",
        encoding="utf-8",
    )

    create_claim(
        db,
        "CLM_ONE_DOCUMENT",
        documents=[
            {
                "document_id": "DOC_ONE_DOCUMENT",
                "document_type": "POLICE_REPORT",
                "file_name": "police_report.txt",
                "storage_path": str(file_path),
            }
        ],
    )

    service = DocumentVerificationService(db)

    result = service.verify_claim_documents(
        "CLM_ONE_DOCUMENT"
    )

    police_report = next(
        document
        for document in result.documents
        if document.document_type == "POLICE_REPORT"
    )

    assert police_report.status == "NEEDS_REVIEW"
    assert police_report.extracted_fields["file_type"] == "TXT"
    assert len(result.missing_documents) == 5
    assert result.overall_status == "INCOMPLETE"


def test_unsupported_document_type(db):

    file_path = "unused_document.txt"

    create_claim(
        db,
        "CLM_UNSUPPORTED_DOC",
        documents=[
            {
                "document_id": "DOC_UNSUPPORTED",
                "document_type": "UNKNOWN_DOCUMENT",
                "file_name": "unknown.txt",
                "storage_path": file_path,
            }
        ],
    )

    service = DocumentVerificationService(db)

    result = service.verify_claim_documents(
        "CLM_UNSUPPORTED_DOC"
    )

    unsupported_document = next(
        document
        for document in result.documents
        if document.document_type == "UNKNOWN_DOCUMENT"
    )

    assert unsupported_document.status == "NEEDS_REVIEW"
    assert result.overall_status == "INCOMPLETE"


def test_document_extraction_failure(db):

    create_claim(
        db,
        "CLM_EXTRACTION_FAILURE",
        documents=[
            {
                "document_id": "DOC_EXTRACTION_FAILURE",
                "document_type": "POLICE_REPORT",
                "file_name": "missing_report.txt",
                "storage_path": "non_existing_report.txt",
            }
        ],
    )

    service = DocumentVerificationService(db)

    result = service.verify_claim_documents(
        "CLM_EXTRACTION_FAILURE"
    )

    police_report = next(
        document
        for document in result.documents
        if document.document_type == "POLICE_REPORT"
    )

    assert police_report.status == "INVALID"
    assert police_report.issues[0].issue_type == "EXTRACTION_FAILED"
    assert result.inconsistencies


def test_all_documents_present_require_content_review(db, tmp_path):

    documents = []

    for index, document_type in enumerate(
        DocumentVerificationService.REQUIRED_DOCUMENTS,
        start=1,
    ):
        file_path = tmp_path / f"document_{index}.txt"

        file_path.write_text(
            f"Sample content for {document_type}",
            encoding="utf-8",
        )

        documents.append({
            "document_id": f"DOC_COMPLETE_{index}",
            "document_type": document_type,
            "file_name": file_path.name,
            "storage_path": str(file_path),
        })

    create_claim(
        db,
        "CLM_ALL_DOCS_PRESENT",
        documents=documents,
    )

    service = DocumentVerificationService(db)

    result = service.verify_claim_documents(
        "CLM_ALL_DOCS_PRESENT"
    )

    assert result.overall_status == "NEEDS_REVIEW"
    assert result.missing_documents == []
    assert len(result.documents) == 6
    assert all(
        document.status == "NEEDS_REVIEW"
        for document in result.documents
    )
