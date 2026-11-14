
from datetime import date

import pytest

from app.fraud_detection.fraud_rules import FraudRules
from app.schemas.fraud_detection_schema import (
    FraudFindingSource,
)


@pytest.fixture
def fraud_rules():
    return FraudRules()


def test_duplicate_claim_detected(fraud_rules):
    findings = fraud_rules.check_duplicate_claim(
        duplicate_found=True
    )

    assert len(findings) == 1
    assert findings[0].rule_id == "DUPLICATE_CLAIM"
    assert findings[0].risk_points == 40
    assert findings[0].source == FraudFindingSource.RULE_BASED


def test_no_duplicate_claim(fraud_rules):
    findings = fraud_rules.check_duplicate_claim(
        duplicate_found=False
    )

    assert findings == []


def test_recent_policy_detected(fraud_rules):
    findings = fraud_rules.check_recent_policy(
        policy_start_date=date(2026, 1, 1),
        incident_date=date(2026, 1, 15),
    )

    assert len(findings) == 1
    assert findings[0].rule_id == "RECENT_POLICY"
    assert findings[0].risk_points == 15


def test_old_policy_does_not_trigger(fraud_rules):
    findings = fraud_rules.check_recent_policy(
        policy_start_date=date(2026, 1, 1),
        incident_date=date(2026, 3, 1),
    )

    assert findings == []


def test_incident_before_policy_start_raises_error(fraud_rules):
    with pytest.raises(ValueError):
        fraud_rules.check_recent_policy(
            policy_start_date=date(2026, 2, 1),
            incident_date=date(2026, 1, 1),
        )


def test_multiple_recent_claims_detected(fraud_rules):
    findings = fraud_rules.check_multiple_recent_claims(
        recent_claim_count=4
    )

    assert len(findings) == 1
    assert findings[0].rule_id == "MULTIPLE_RECENT_CLAIMS"
    assert findings[0].risk_points == 20


def test_low_recent_claim_count_does_not_trigger(fraud_rules):
    findings = fraud_rules.check_multiple_recent_claims(
        recent_claim_count=2
    )

    assert findings == []


def test_negative_recent_claim_count_raises_error(fraud_rules):
    with pytest.raises(ValueError):
        fraud_rules.check_multiple_recent_claims(
            recent_claim_count=-1
        )


def test_high_claim_amount_detected(fraud_rules):
    findings = fraud_rules.check_high_claim_amount(
        claim_amount=300000
    )

    assert len(findings) == 1
    assert findings[0].rule_id == "HIGH_CLAIM_AMOUNT"
    assert findings[0].risk_points == 20


def test_normal_claim_amount_does_not_trigger(fraud_rules):
    findings = fraud_rules.check_high_claim_amount(
        claim_amount=150000
    )

    assert findings == []


def test_negative_claim_amount_raises_error(fraud_rules):
    with pytest.raises(ValueError):
        fraud_rules.check_high_claim_amount(
            claim_amount=-1000
        )
