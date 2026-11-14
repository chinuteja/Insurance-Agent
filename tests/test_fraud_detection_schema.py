
import pytest
from pydantic import ValidationError

from app.schemas.fraud_detection_schema import (
    FraudRiskLevel,
    FraudFindingSource,
    FraudFinding,
    FraudDetectionResponse,
)


def test_fraud_risk_level():
    assert FraudRiskLevel.LOW == "LOW"
    assert FraudRiskLevel.MEDIUM == "MEDIUM"
    assert FraudRiskLevel.HIGH == "HIGH"


def test_fraud_finding_source():
    assert FraudFindingSource.RULE_BASED == "RULE_BASED"
    assert FraudFindingSource.AI_ANALYSIS == "AI_ANALYSIS"


def test_fraud_finding_creation():
    finding = FraudFinding(
        rule_id="DUPLICATE_CLAIM",
        description="Potential duplicate claim detected.",
        risk_points=40,
        source=FraudFindingSource.RULE_BASED,
        evidence=["Matching claim ID found."],
    )

    assert finding.rule_id == "DUPLICATE_CLAIM"
    assert finding.risk_points == 40
    assert finding.source == FraudFindingSource.RULE_BASED
    assert len(finding.evidence) == 1


def test_fraud_finding_default_evidence():
    finding = FraudFinding(
        rule_id="RECENT_POLICY",
        description="Policy was purchased shortly before incident.",
        risk_points=15,
        source=FraudFindingSource.RULE_BASED,
    )

    assert finding.evidence == []


def test_fraud_finding_rejects_invalid_risk_points():
    with pytest.raises(ValidationError):
        FraudFinding(
            rule_id="INVALID",
            description="Invalid risk points.",
            risk_points=150,
            source=FraudFindingSource.RULE_BASED,
        )


def test_fraud_detection_response_creation():
    response = FraudDetectionResponse(
        claim_id="CLM_FRAUD_001",
        risk_score=40,
        risk_level=FraudRiskLevel.MEDIUM,
        findings=[
            FraudFinding(
                rule_id="DUPLICATE_CLAIM",
                description="Potential duplicate claim detected.",
                risk_points=40,
                source=FraudFindingSource.RULE_BASED,
                evidence=["Similar claim found."],
            )
        ],
        recommendation="Send for manual investigation.",
    )

    assert response.claim_id == "CLM_FRAUD_001"
    assert response.risk_score == 40
    assert response.risk_level == FraudRiskLevel.MEDIUM
    assert len(response.findings) == 1


def test_fraud_detection_response_rejects_invalid_score():
    with pytest.raises(ValidationError):
        FraudDetectionResponse(
            claim_id="CLM_FRAUD_002",
            risk_score=120,
            risk_level=FraudRiskLevel.HIGH,
            recommendation="Manual review required.",
        )


def test_fraud_detection_response_default_findings():
    response = FraudDetectionResponse(
        claim_id="CLM_FRAUD_003",
        risk_score=0,
        risk_level=FraudRiskLevel.LOW,
        recommendation="No significant risk indicators found.",
    )

    assert response.findings == []
