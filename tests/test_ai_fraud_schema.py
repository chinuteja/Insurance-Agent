
import pytest
from pydantic import ValidationError

from app.schemas.ai_fraud_schema import (
    AIFraudSeverity,
    AIFraudFinding,
    AIFraudAnalysisResponse,
)


def test_ai_fraud_severity():
    assert AIFraudSeverity.LOW == "LOW"
    assert AIFraudSeverity.MEDIUM == "MEDIUM"
    assert AIFraudSeverity.HIGH == "HIGH"


def test_ai_fraud_finding_creation():
    finding = AIFraudFinding(
        finding_type="DOCUMENT_INCONSISTENCY",
        description="Vehicle number differs between documents.",
        severity=AIFraudSeverity.HIGH,
        evidence=[
            "Police report: TS09AB1234",
            "Repair estimate: TS09AB5678",
        ],
        confidence=0.90,
    )

    assert finding.finding_type == "DOCUMENT_INCONSISTENCY"
    assert finding.severity == AIFraudSeverity.HIGH
    assert finding.confidence == 0.90
    assert len(finding.evidence) == 2


def test_ai_fraud_finding_rejects_invalid_confidence():
    with pytest.raises(ValidationError):
        AIFraudFinding(
            finding_type="TEST",
            description="Test finding.",
            severity=AIFraudSeverity.LOW,
            evidence=["Test evidence"],
            confidence=1.5,
        )


def test_ai_fraud_finding_requires_evidence():
    with pytest.raises(ValidationError):
        AIFraudFinding(
            finding_type="TEST",
            description="Test finding.",
            severity=AIFraudSeverity.LOW,
            evidence=[],
            confidence=0.8,
        )


def test_ai_fraud_analysis_response():
    response = AIFraudAnalysisResponse(
        claim_id="CLM_AI_001",
        suspicious_patterns=[],
        overall_assessment="No significant suspicious patterns identified.",
        requires_human_review=False,
    )

    assert response.claim_id == "CLM_AI_001"
    assert response.suspicious_patterns == []
    assert response.requires_human_review is False


def test_ai_fraud_analysis_with_findings():
    response = AIFraudAnalysisResponse(
        claim_id="CLM_AI_002",
        suspicious_patterns=[
            AIFraudFinding(
                finding_type="TIMELINE_INCONSISTENCY",
                description="Incident dates differ across documents.",
                severity=AIFraudSeverity.MEDIUM,
                evidence=["Report A: 10 May", "Report B: 12 May"],
                confidence=0.85,
            )
        ],
        overall_assessment="Timeline inconsistency requires investigation.",
        requires_human_review=True,
    )

    assert len(response.suspicious_patterns) == 1
    assert response.requires_human_review is True


def test_ai_fraud_analysis_rejects_empty_assessment():
    with pytest.raises(ValidationError):
        AIFraudAnalysisResponse(
            claim_id="CLM_AI_003",
            overall_assessment="",
            requires_human_review=False,
        )
