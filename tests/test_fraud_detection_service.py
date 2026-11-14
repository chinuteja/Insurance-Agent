
from datetime import date
from unittest.mock import MagicMock

import pytest

from app.services.fraud_detection_service import (
    FraudDetectionService,
)

from app.schemas.ai_fraud_schema import (
    AIFraudAnalysisResponse,
    AIFraudFinding,
    AIFraudSeverity,
)

from app.schemas.fraud_detection_schema import (
    FraudFinding,
    FraudFindingSource,
    FraudRiskLevel,
)


@pytest.fixture
def mock_dependencies():
    fraud_rules = MagicMock()
    fraud_scorer = MagicMock()
    ai_service = MagicMock()

    service = FraudDetectionService(
        fraud_rules=fraud_rules,
        fraud_scorer=fraud_scorer,
        ai_service=ai_service,
    )

    return service, fraud_rules, fraud_scorer, ai_service


def test_detect_fraud_combines_rule_and_ai_findings(
    mock_dependencies,
):
    service, rules, scorer, ai_service = mock_dependencies

    rule_finding = FraudFinding(
        rule_id="DUPLICATE_CLAIM",
        description="Duplicate claim detected.",
        risk_points=40,
        source=FraudFindingSource.RULE_BASED,
        evidence=["Matching claim found."],
    )

    rules.check_duplicate_claim.return_value = [rule_finding]
    rules.check_recent_policy.return_value = []
    rules.check_multiple_recent_claims.return_value = []
    rules.check_high_claim_amount.return_value = []

    ai_service.analyze_claim.return_value = AIFraudAnalysisResponse(
        claim_id="CLM_FD_001",
        suspicious_patterns=[
            AIFraudFinding(
                finding_type="DOCUMENT_INCONSISTENCY",
                description="Vehicle number differs.",
                severity=AIFraudSeverity.HIGH,
                evidence=["Vehicle number TS09AB1234"],
                confidence=0.90,
            )
        ],
        overall_assessment="Document inconsistency detected.",
        requires_human_review=True,
    )

    expected_response = MagicMock()
    scorer.generate_response.return_value = expected_response

    result = service.detect_fraud(
        claim_id="CLM_FD_001",
        claim_description="Vehicle number TS09AB1234",
        policy_start_date=date(2026, 1, 1),
        incident_date=date(2026, 2, 1),
        duplicate_found=True,
        recent_claim_count=0,
        claim_amount=100000,
    )

    assert result == expected_response

    passed_findings = scorer.generate_response.call_args.kwargs[
        "findings"
    ]

    assert len(passed_findings) == 2
    assert passed_findings[0].rule_id == "DUPLICATE_CLAIM"
    assert passed_findings[1].rule_id == "AI_DOCUMENT_INCONSISTENCY"


def test_ai_finding_without_matching_evidence_is_ignored(
    mock_dependencies,
):
    service, rules, scorer, ai_service = mock_dependencies

    rules.check_duplicate_claim.return_value = []
    rules.check_recent_policy.return_value = []
    rules.check_multiple_recent_claims.return_value = []
    rules.check_high_claim_amount.return_value = []

    ai_service.analyze_claim.return_value = AIFraudAnalysisResponse(
        claim_id="CLM_FD_002",
        suspicious_patterns=[
            AIFraudFinding(
                finding_type="DOCUMENT_INCONSISTENCY",
                description="Vehicle numbers differ.",
                severity=AIFraudSeverity.HIGH,
                evidence=["This text does not exist in the documents."],
                confidence=0.95,
            )
        ],
        overall_assessment="Potential inconsistency.",
        requires_human_review=True,
    )

    service.detect_fraud(
        claim_id="CLM_FD_002",
        claim_description="Vehicle accident.",
        policy_start_date=date(2026, 1, 1),
        incident_date=date(2026, 3, 1),
        duplicate_found=False,
        recent_claim_count=0,
        claim_amount=50000,
    )

    passed_findings = scorer.generate_response.call_args.kwargs[
        "findings"
    ]

    assert passed_findings == []


def test_low_confidence_ai_finding_is_ignored(
    mock_dependencies,
):
    service, rules, scorer, ai_service = mock_dependencies

    rules.check_duplicate_claim.return_value = []
    rules.check_recent_policy.return_value = []
    rules.check_multiple_recent_claims.return_value = []
    rules.check_high_claim_amount.return_value = []

    ai_service.analyze_claim.return_value = AIFraudAnalysisResponse(
        claim_id="CLM_FD_003",
        suspicious_patterns=[
            AIFraudFinding(
                finding_type="TIMELINE_INCONSISTENCY",
                description="Potential timeline issue.",
                severity=AIFraudSeverity.HIGH,
                evidence=["Vehicle accident reported."],
                confidence=0.50,
            )
        ],
        overall_assessment="Low confidence observation.",
        requires_human_review=False,
    )

    service.detect_fraud(
        claim_id="CLM_FD_003",
        claim_description="Vehicle accident reported.",
        policy_start_date=date(2026, 1, 1),
        incident_date=date(2026, 3, 1),
        duplicate_found=False,
        recent_claim_count=0,
        claim_amount=50000,
    )

    passed_findings = scorer.generate_response.call_args.kwargs[
        "findings"
    ]

    assert passed_findings == []


def test_duplicate_findings_are_removed(
    mock_dependencies,
):
    service, rules, scorer, ai_service = mock_dependencies

    finding = FraudFinding(
        rule_id="DUPLICATE_CLAIM",
        description="Duplicate claim detected.",
        risk_points=40,
        source=FraudFindingSource.RULE_BASED,
        evidence=["Matching claim found."],
    )

    rules.check_duplicate_claim.return_value = [finding]
    rules.check_recent_policy.return_value = [finding]
    rules.check_multiple_recent_claims.return_value = []
    rules.check_high_claim_amount.return_value = []

    ai_service.analyze_claim.return_value = AIFraudAnalysisResponse(
        claim_id="CLM_FD_004",
        suspicious_patterns=[],
        overall_assessment="No additional findings.",
        requires_human_review=False,
    )

    service.detect_fraud(
        claim_id="CLM_FD_004",
        claim_description="Vehicle accident.",
        policy_start_date=date(2026, 1, 1),
        incident_date=date(2026, 3, 1),
        duplicate_found=True,
        recent_claim_count=0,
        claim_amount=50000,
    )

    passed_findings = scorer.generate_response.call_args.kwargs[
        "findings"
    ]

    assert len(passed_findings) == 1


def test_empty_claim_id_raises_error(mock_dependencies):
    service, rules, scorer, ai_service = mock_dependencies

    with pytest.raises(ValueError, match="Claim ID cannot be empty"):
        service.detect_fraud(
            claim_id=" ",
            claim_description="Vehicle accident.",
            policy_start_date=date(2026, 1, 1),
            incident_date=date(2026, 3, 1),
            duplicate_found=False,
            recent_claim_count=0,
            claim_amount=50000,
        )

    ai_service.analyze_claim.assert_not_called()


def test_empty_claim_description_raises_error(mock_dependencies):
    service, rules, scorer, ai_service = mock_dependencies

    with pytest.raises(
        ValueError,
        match="Claim description cannot be empty",
    ):
        service.detect_fraud(
            claim_id="CLM_FD_005",
            claim_description=" ",
            policy_start_date=date(2026, 1, 1),
            incident_date=date(2026, 3, 1),
            duplicate_found=False,
            recent_claim_count=0,
            claim_amount=50000,
        )

    ai_service.analyze_claim.assert_not_called()
