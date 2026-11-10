
from unittest.mock import MagicMock

import pytest

from app.services.document_verification_service import (
    DocumentVerificationService,
)

from app.schemas.policy_consistency_schema import (
    PolicyConsistencyStatus,
    PolicyConsistencyResponse,
)

from app.schemas.document_verification_schema import (
    DocumentVerificationStatus,
    OverallVerificationStatus,
)

from tests.test_document_verification_service import create_claim


@pytest.fixture
def sample_claim_with_document(db, tmp_path):

    document_path = tmp_path / "police_report.txt"
    document_path.write_text(
        "Vehicle damaged in a road accident.",
        encoding="utf-8",
    )

    create_claim(
        db,
        "CLM_POLICY_INTEGRATION",
        documents=[
            {
                "document_id": "DOC_POLICY_INTEGRATION",
                "document_type": "POLICE_REPORT",
                "file_name": "police_report.txt",
                "storage_path": str(document_path),
            }
        ],
    )

    return "CLM_POLICY_INTEGRATION"


@pytest.fixture
def mock_policy_consistency_service():

    return MagicMock()


def test_consistent_policy_evidence(
    db,
    sample_claim_with_document,
    mock_policy_consistency_service,
):

    mock_policy_consistency_service.validate_document.return_value = (
        PolicyConsistencyResponse(
            document_type="POLICE_REPORT",
            overall_status=PolicyConsistencyStatus.CONSISTENT,
            recommendation="The document is consistent with policy evidence.",
        )
    )

    service = DocumentVerificationService(
        db,
        policy_consistency_service=mock_policy_consistency_service,
    )

    result = service.verify_claim_documents(
        sample_claim_with_document
    )

    police_report = next(
        document
        for document in result.documents
        if document.document_type == "POLICE_REPORT"
    )

    assert police_report.status == DocumentVerificationStatus.NEEDS_REVIEW

    assert (
        police_report.extracted_fields["policy_consistency"][
            "overall_status"
        ]
        == PolicyConsistencyStatus.CONSISTENT.value
    )

    assert not any(
        "Policy inconsistency detected" in item
        for item in result.inconsistencies
    )

    mock_policy_consistency_service.validate_document.assert_called_once()


def test_inconsistent_policy_evidence(
    db,
    sample_claim_with_document,
    mock_policy_consistency_service,
):

    mock_policy_consistency_service.validate_document.return_value = (
        PolicyConsistencyResponse(
            document_type="POLICE_REPORT",
            overall_status=PolicyConsistencyStatus.INCONSISTENT,
            recommendation="Potential contradiction with policy evidence.",
        )
    )

    service = DocumentVerificationService(
        db,
        policy_consistency_service=mock_policy_consistency_service,
    )

    result = service.verify_claim_documents(
        sample_claim_with_document
    )

    police_report = next(
        document
        for document in result.documents
        if document.document_type == "POLICE_REPORT"
    )

    assert police_report.status == DocumentVerificationStatus.NEEDS_REVIEW

    assert any(
        issue.issue_type == "POLICY_INCONSISTENCY"
        for issue in police_report.issues
    )

    assert any(
        "Policy inconsistency detected" in item
        for item in result.inconsistencies
    )


def test_insufficient_policy_evidence(
    db,
    sample_claim_with_document,
    mock_policy_consistency_service,
):

    mock_policy_consistency_service.validate_document.return_value = (
        PolicyConsistencyResponse(
            document_type="POLICE_REPORT",
            overall_status=(
                PolicyConsistencyStatus.INSUFFICIENT_EVIDENCE
            ),
            recommendation="Manual policy review is required.",
        )
    )

    service = DocumentVerificationService(
        db,
        policy_consistency_service=mock_policy_consistency_service,
    )

    result = service.verify_claim_documents(
        sample_claim_with_document
    )

    police_report = next(
        document
        for document in result.documents
        if document.document_type == "POLICE_REPORT"
    )

    assert any(
        issue.issue_type == "POLICY_REVIEW_REQUIRED"
        for issue in police_report.issues
    )

    assert not any(
        "Policy inconsistency detected" in item
        for item in result.inconsistencies
    )


def test_policy_consistency_service_failure(
    db,
    sample_claim_with_document,
    mock_policy_consistency_service,
):

    mock_policy_consistency_service.validate_document.side_effect = (
        RuntimeError("Policy validation service unavailable.")
    )

    service = DocumentVerificationService(
        db,
        policy_consistency_service=mock_policy_consistency_service,
    )

    result = service.verify_claim_documents(
        sample_claim_with_document
    )

    police_report = next(
        document
        for document in result.documents
        if document.document_type == "POLICE_REPORT"
    )

    assert police_report.status == DocumentVerificationStatus.INVALID

    assert police_report.issues[0].issue_type == "EXTRACTION_FAILED"

    assert "Policy validation service unavailable" in (
        police_report.issues[0].description
    )


def test_policy_service_not_provided(
    db,
    sample_claim_with_document,
):

    service = DocumentVerificationService(db)

    result = service.verify_claim_documents(
        sample_claim_with_document
    )

    police_report = next(
        document
        for document in result.documents
        if document.document_type == "POLICE_REPORT"
    )

    assert police_report.status == DocumentVerificationStatus.NEEDS_REVIEW

    assert "policy_consistency" not in police_report.extracted_fields

    assert not any(
        issue.issue_type == "POLICY_INCONSISTENCY"
        for issue in police_report.issues
    )
