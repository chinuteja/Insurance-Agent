
from datetime import date

from app.fraud_detection.fraud_rules import FraudRules
from app.fraud_detection.fraud_scorer import FraudScorer

from app.services.ai_fraud_analysis_service import (
    AIFraudAnalysisService,
)

from app.schemas.fraud_detection_schema import (
    FraudFinding,
    FraudFindingSource,
    FraudDetectionResponse,
)

from app.schemas.ai_fraud_schema import (
    AIFraudSeverity,
)


class FraudDetectionService:

    AI_SEVERITY_POINTS = {
        AIFraudSeverity.LOW: 5,
        AIFraudSeverity.MEDIUM: 10,
        AIFraudSeverity.HIGH: 20,
    }

    MIN_AI_CONFIDENCE = 0.70

    def __init__(
        self,
        fraud_rules=None,
        fraud_scorer=None,
        ai_service=None,
    ):
        self.fraud_rules = fraud_rules or FraudRules()
        self.fraud_scorer = fraud_scorer or FraudScorer()
        self.ai_service = ai_service or AIFraudAnalysisService()

    @staticmethod
    def _normalize_text(text: str) -> str:
        return " ".join(text.lower().split())

    def _validate_ai_evidence(
        self,
        evidence: list[str],
        source_texts: list[str],
    ) -> bool:
        """
        Accept an AI finding only if at least one evidence
        statement appears in the supplied source information.
        """

        normalized_sources = [
            self._normalize_text(text)
            for text in source_texts
            if text and text.strip()
        ]

        for item in evidence:
            normalized_evidence = self._normalize_text(item)

            if normalized_evidence and any(
                normalized_evidence in source
                for source in normalized_sources
            ):
                return True

        return False

    def _convert_ai_findings(
        self,
        ai_response,
        source_texts: list[str],
    ) -> list[FraudFinding]:

        findings = []

        for item in ai_response.suspicious_patterns:

            if item.confidence < self.MIN_AI_CONFIDENCE:
                continue

            if not self._validate_ai_evidence(
                evidence=item.evidence,
                source_texts=source_texts,
            ):
                continue

            risk_points = self.AI_SEVERITY_POINTS[item.severity]

            findings.append(
                FraudFinding(
                    rule_id=f"AI_{item.finding_type}",
                    description=item.description,
                    risk_points=risk_points,
                    source=FraudFindingSource.AI_ANALYSIS,
                    evidence=item.evidence,
                )
            )

        return findings

    @staticmethod
    def _deduplicate_findings(
        findings: list[FraudFinding],
    ) -> list[FraudFinding]:

        unique_findings = {}

        for finding in findings:
            if finding.rule_id not in unique_findings:
                unique_findings[finding.rule_id] = finding

        return list(unique_findings.values())

    def detect_fraud(
        self,
        claim_id: str,
        claim_description: str,
        policy_start_date: date,
        incident_date: date,
        duplicate_found: bool,
        recent_claim_count: int,
        claim_amount: float,
        document_texts: list[str] | None = None,
    ) -> FraudDetectionResponse:

        if not claim_id or not claim_id.strip():
            raise ValueError("Claim ID cannot be empty.")

        if not claim_description or not claim_description.strip():
            raise ValueError("Claim description cannot be empty.")

        document_texts = document_texts or []

        # Step 1: Run deterministic fraud rules.
        rule_findings = []

        rule_findings.extend(
            self.fraud_rules.check_duplicate_claim(
                duplicate_found=duplicate_found,
            )
        )

        rule_findings.extend(
            self.fraud_rules.check_recent_policy(
                policy_start_date=policy_start_date,
                incident_date=incident_date,
            )
        )

        rule_findings.extend(
            self.fraud_rules.check_multiple_recent_claims(
                recent_claim_count=recent_claim_count,
            )
        )

        rule_findings.extend(
            self.fraud_rules.check_high_claim_amount(
                claim_amount=claim_amount,
            )
        )

        # Step 2: Run AI-based fraud analysis.
        ai_response = self.ai_service.analyze_claim(
            claim_id=claim_id,
            claim_description=claim_description,
            document_texts=document_texts,
        )

        # Step 3: Validate and convert AI findings.
        source_texts = [
            claim_description,
            *document_texts,
        ]

        ai_findings = self._convert_ai_findings(
            ai_response=ai_response,
            source_texts=source_texts,
        )

        # Step 4: Combine and deduplicate findings.
        all_findings = self._deduplicate_findings(
            rule_findings + ai_findings
        )

        # Step 5: Calculate final fraud risk report.
        return self.fraud_scorer.generate_response(
            claim_id=claim_id,
            findings=all_findings,
        )
