
import pytest
from pydantic import ValidationError

from app.schemas.document_verification_schema import (
    DocumentVerificationStatus,
    OverallVerificationStatus,
    DocumentIssue,
    DocumentVerificationResult,
    ClaimDocumentVerificationResponse,
)


def test_document_verification_status():
    assert DocumentVerificationStatus.VERIFIED == "VERIFIED"
    assert DocumentVerificationStatus.MISSING == "MISSING"


def test_overall_verification_status():
    assert OverallVerificationStatus.INCOMPLETE == "INCOMPLETE"


def test_document_issue_schema():
    issue = DocumentIssue(
        issue_type="MISSING_FIELD",
        description="Incident date is missing",
    )

    assert issue.issue_type == "MISSING_FIELD"


def test_document_verification_result():
    result = DocumentVerificationResult(
        document_type="POLICE_REPORT",
        status=DocumentVerificationStatus.VERIFIED,
        extracted_fields={"incident_date": "2026-10-15"},
    )

    assert result.document_type == "POLICE_REPORT"
    assert result.status == "VERIFIED"
    assert result.issues == []


def test_claim_document_verification_response():
    response = ClaimDocumentVerificationResponse(
        claim_id="CLM_API_001",
        overall_status=OverallVerificationStatus.INCOMPLETE,
        missing_documents=["REPAIR_ESTIMATE"],
        recommendation="Request missing documents",
    )

    assert response.claim_id == "CLM_API_001"
    assert response.documents == []
    assert response.missing_documents == ["REPAIR_ESTIMATE"]


def test_invalid_document_status():
    with pytest.raises(ValidationError):
        DocumentVerificationResult(
            document_type="POLICE_REPORT",
            status="UNKNOWN",
        )
