
from datetime import date

from app.schemas.fraud_detection_schema import (
    FraudFinding,
    FraudFindingSource,
)


class FraudRules:

    DUPLICATE_CLAIM_POINTS = 40
    RECENT_POLICY_POINTS = 15
    MULTIPLE_RECENT_CLAIMS_POINTS = 20
    HIGH_CLAIM_AMOUNT_POINTS = 20

    def check_duplicate_claim(
        self,
        duplicate_found: bool,
    ) -> list[FraudFinding]:

        if not duplicate_found:
            return []

        return [
            FraudFinding(
                rule_id="DUPLICATE_CLAIM",
                description="Potential duplicate claim detected.",
                risk_points=self.DUPLICATE_CLAIM_POINTS,
                source=FraudFindingSource.RULE_BASED,
                evidence=["A matching claim was found."],
            )
        ]

    def check_recent_policy(
        self,
        policy_start_date: date,
        incident_date: date,
        threshold_days: int = 30,
    ) -> list[FraudFinding]:

        days_between = (
            incident_date - policy_start_date
        ).days

        if days_between < 0:
            raise ValueError(
                "Incident date cannot be before policy start date."
            )

        if days_between > threshold_days:
            return []

        return [
            FraudFinding(
                rule_id="RECENT_POLICY",
                description=(
                    "Incident occurred shortly after policy inception."
                ),
                risk_points=self.RECENT_POLICY_POINTS,
                source=FraudFindingSource.RULE_BASED,
                evidence=[
                    f"Incident occurred {days_between} days "
                    "after policy inception."
                ],
            )
        ]

    def check_multiple_recent_claims(
        self,
        recent_claim_count: int,
        threshold: int = 3,
    ) -> list[FraudFinding]:

        if recent_claim_count < 0:
            raise ValueError(
                "Recent claim count cannot be negative."
            )

        if recent_claim_count < threshold:
            return []

        return [
            FraudFinding(
                rule_id="MULTIPLE_RECENT_CLAIMS",
                description=(
                    "Multiple claims were submitted within "
                    "the configured review period."
                ),
                risk_points=self.MULTIPLE_RECENT_CLAIMS_POINTS,
                source=FraudFindingSource.RULE_BASED,
                evidence=[
                    f"Recent claim count: {recent_claim_count}."
                ],
            )
        ]

    def check_high_claim_amount(
        self,
        claim_amount: float,
        threshold_amount: float = 200000,
    ) -> list[FraudFinding]:

        if claim_amount < 0:
            raise ValueError(
                "Claim amount cannot be negative."
            )

        if claim_amount <= threshold_amount:
            return []

        return [
            FraudFinding(
                rule_id="HIGH_CLAIM_AMOUNT",
                description=(
                    "Claim amount exceeds the configured "
                    "review threshold."
                ),
                risk_points=self.HIGH_CLAIM_AMOUNT_POINTS,
                source=FraudFindingSource.RULE_BASED,
                evidence=[
                    f"Claim amount: {claim_amount}."
                ],
            )
        ]
