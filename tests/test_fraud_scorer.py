
import pytest

from app.fraud_detection.fraud_scorer import FraudScorer

from app.schemas.fraud_detection_schema import (
    FraudFinding,
    FraudFindingSource,
    FraudRiskLevel,
)


@pytest.fixture
def scorer():
    return FraudScorer()


def create_finding(rule_id, points):
    return FraudFinding(
        rule_id=rule_id,
        description=f"Test finding: {rule_id}",
        risk_points=points,
        source=FraudFindingSource.RULE_BASED,
        evidence=["Test evidence"],
    )


def test_calculate_empty_findings(scorer):
    assert scorer.calculate_score([]) == 0


def test_calculate_single_finding(scorer):
    findings = [
        create_finding("DUPLICATE_CLAIM", 40)
    ]

    assert scorer.calculate_score(findings) == 40


def test_calculate_multiple_findings(scorer):
    findings = [
        create_finding("DUPLICATE_CLAIM", 40),
        create_finding("RECENT_POLICY", 15),
        create_finding("HIGH_CLAIM_AMOUNT", 20),
    ]

    assert scorer.calculate_score(findings) == 75


def test_score_is_capped_at_100(scorer):
    findings = [
        create_finding("RULE_1", 60),
        create_finding("RULE_2", 60),
    ]

    assert scorer.calculate_score(findings) == 100


def test_duplicate_rule_counted_once(scorer):
    findings = [
        create_finding("DUPLICATE_CLAIM", 40),
        create_finding("DUPLICATE_CLAIM", 40),
    ]

    assert scorer.calculate_score(findings) == 40


@pytest.mark.parametrize(
    "score, expected_level",
    [
        (0, FraudRiskLevel.LOW),
        (29, FraudRiskLevel.LOW),
        (30, FraudRiskLevel.MEDIUM),
        (69, FraudRiskLevel.MEDIUM),
        (70, FraudRiskLevel.HIGH),
        (100, FraudRiskLevel.HIGH),
    ],
)
def test_determine_risk_level(
    scorer,
    score,
    expected_level,
):
    assert scorer.determine_risk_level(score) == expected_level


@pytest.mark.parametrize("score", [-1, 101])
def test_invalid_risk_score(scorer, score):
    with pytest.raises(ValueError):
        scorer.determine_risk_level(score)


def test_generate_low_risk_response(scorer):
    response = scorer.generate_response(
        claim_id="CLM_001",
        findings=[],
    )

    assert response.claim_id == "CLM_001"
    assert response.risk_score == 0
    assert response.risk_level == FraudRiskLevel.LOW
    assert len(response.findings) == 0


def test_generate_high_risk_response(scorer):
    findings = [
        create_finding("DUPLICATE_CLAIM", 40),
        create_finding("RECENT_POLICY", 15),
        create_finding("HIGH_CLAIM_AMOUNT", 20),
    ]

    response = scorer.generate_response(
        claim_id="CLM_002",
        findings=findings,
    )

    assert response.risk_score == 75
    assert response.risk_level == FraudRiskLevel.HIGH
    assert len(response.findings) == 3
    assert "human investigation" in response.recommendation
