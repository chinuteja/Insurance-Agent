
from app.schemas.fraud_detection_schema import (
    FraudFinding,
    FraudRiskLevel,
    FraudDetectionResponse,
)


class FraudScorer:

    LOW_RISK_MAX = 29
    MEDIUM_RISK_MAX = 69

    def calculate_score(
        self,
        findings: list[FraudFinding],
    ) -> int:
        """
        Calculate the total fraud risk score.

        Duplicate rule IDs are counted only once.
        Final score is capped at 100.
        """

        unique_findings = {}
        
        for finding in findings:
            if finding.rule_id not in unique_findings:
                unique_findings[finding.rule_id] = finding

        total_score = sum(
            finding.risk_points
            for finding in unique_findings.values()
        )

        return min(total_score, 100)

    def determine_risk_level(
        self,
        risk_score: int,
    ) -> FraudRiskLevel:

        if not 0 <= risk_score <= 100:
            raise ValueError(
                "Risk score must be between 0 and 100."
            )

        if risk_score <= self.LOW_RISK_MAX:
            return FraudRiskLevel.LOW

        if risk_score <= self.MEDIUM_RISK_MAX:
            return FraudRiskLevel.MEDIUM

        return FraudRiskLevel.HIGH

    def generate_response(
        self,
        claim_id: str,
        findings: list[FraudFinding],
    ) -> FraudDetectionResponse:

        risk_score = self.calculate_score(findings)

        risk_level = self.determine_risk_level(
            risk_score
        )

        if risk_level == FraudRiskLevel.LOW:
            recommendation = (
                "No significant risk indicators detected. "
                "Continue with normal claim processing."
            )

        elif risk_level == FraudRiskLevel.MEDIUM:
            recommendation = (
                "Some suspicious indicators were detected. "
                "Additional investigation is recommended."
            )

        else:
            recommendation = (
                "Multiple or significant risk indicators were detected. "
                "Escalate this claim for human investigation."
            )

        return FraudDetectionResponse(
            claim_id=claim_id,
            risk_score=risk_score,
            risk_level=risk_level,
            findings=findings,
            recommendation=recommendation,
        )
