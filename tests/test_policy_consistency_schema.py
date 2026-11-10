
import pytest
from pydantic import ValidationError

from app.schemas.policy_consistency_schema import (
    PolicyConsistencyStatus,
    PolicyEvidence,
    PolicyConsistencyFinding,
    PolicyConsistencyResponse,
)


def test_policy_evidence_creation():

    evidence = PolicyEvidence(
        content="Accidental vehicle damage is covered.",
        source="sample_policy.pdf",
        page=1,
        relevance_score=0.45,
    )

    assert evidence.content == "Accidental vehicle damage is covered."
    assert evidence.source == "sample_policy.pdf"
    assert evidence.page == 1
    assert evidence.relevance_score == 0.45


def test_policy_finding_creation():

    finding = PolicyConsistencyFinding(
        finding="Accident damage coverage",
        explanation="The policy supports accidental vehicle damage.",
        status=PolicyConsistencyStatus.CONSISTENT,
    )

    assert finding.status == PolicyConsistencyStatus.CONSISTENT
    assert finding.evidence == []


def test_policy_finding_with_evidence():

    evidence = PolicyEvidence(
        content="Accidental damage is covered.",
        source="sample_policy.pdf",
        page=1,
        relevance_score=0.55,
    )

    finding = PolicyConsistencyFinding(
        finding="Accident damage",
        explanation="The submitted document is consistent with the policy.",
        status=PolicyConsistencyStatus.CONSISTENT,
        evidence=[evidence],
    )

    assert len(finding.evidence) == 1
    assert finding.evidence[0].source == "sample_policy.pdf"


def test_policy_consistency_response_creation():

    response = PolicyConsistencyResponse(
        document_type="REPAIR_ESTIMATE",
        overall_status=PolicyConsistencyStatus.CONSISTENT,
        recommendation="Proceed to the next verification stage.",
    )

    assert response.document_type == "REPAIR_ESTIMATE"
    assert response.overall_status == PolicyConsistencyStatus.CONSISTENT
    assert response.findings == []


def test_policy_consistency_response_with_findings():

    finding = PolicyConsistencyFinding(
        finding="Coverage check",
        explanation="The policy supports the submitted information.",
        status=PolicyConsistencyStatus.CONSISTENT,
    )

    response = PolicyConsistencyResponse(
        document_type="POLICE_REPORT",
        overall_status=PolicyConsistencyStatus.CONSISTENT,
        findings=[finding],
        recommendation="Continue verification.",
    )

    assert len(response.findings) == 1
    assert response.findings[0].finding == "Coverage check"


def test_invalid_policy_consistency_status():

    with pytest.raises(ValidationError):

        PolicyConsistencyResponse(
            document_type="POLICE_REPORT",
            overall_status="UNKNOWN_STATUS",
            recommendation="Review required.",
        )
