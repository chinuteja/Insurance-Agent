
from unittest.mock import MagicMock

import pytest

from app.services.ai_fraud_analysis_service import (
    AIFraudAnalysisService,
)

from app.schemas.ai_fraud_schema import (
    AIFraudSeverity,
    AIFraudFinding,
    AIFraudAnalysisResponse,
)


@pytest.fixture
def mock_llm():
    llm = MagicMock()
    structured_llm = MagicMock()

    llm.with_structured_output.return_value = structured_llm

    return llm, structured_llm


@pytest.fixture
def analysis_service(mock_llm):
    llm, structured_llm = mock_llm

    service = AIFraudAnalysisService(llm=llm)

    return service, structured_llm


def test_detect_suspicious_document_pattern(analysis_service):
    service, structured_llm = analysis_service

    structured_llm.invoke.return_value = AIFraudAnalysisResponse(
        claim_id="CLM_AI_001",
        suspicious_patterns=[
            AIFraudFinding(
                finding_type="DOCUMENT_INCONSISTENCY",
                description="Vehicle numbers differ.",
                severity=AIFraudSeverity.HIGH,
                evidence=[
                    "Police report: TS09AB1234",
                    "Repair estimate: TS09AB5678",
                ],
                confidence=0.95,
            )
        ],
        overall_assessment="Vehicle number inconsistency detected.",
        requires_human_review=True,
    )

    result = service.analyze_claim(
        claim_id="CLM_AI_001",
        claim_description="Vehicle accident claim.",
        document_texts=[
            "Police report: TS09AB1234",
            "Repair estimate: TS09AB5678",
        ],
    )

    assert result.claim_id == "CLM_AI_001"
    assert len(result.suspicious_patterns) == 1
    assert result.requires_human_review is True

    structured_llm.invoke.assert_called_once()


def test_no_suspicious_patterns(analysis_service):
    service, structured_llm = analysis_service

    structured_llm.invoke.return_value = AIFraudAnalysisResponse(
        claim_id="CLM_AI_002",
        suspicious_patterns=[],
        overall_assessment="No significant suspicious patterns found.",
        requires_human_review=False,
    )

    result = service.analyze_claim(
        claim_id="CLM_AI_002",
        claim_description="Normal vehicle accident.",
    )

    assert result.suspicious_patterns == []
    assert result.requires_human_review is False


def test_empty_claim_id_raises_error(analysis_service):
    service, structured_llm = analysis_service

    with pytest.raises(ValueError, match="Claim ID cannot be empty"):
        service.analyze_claim(
            claim_id=" ",
            claim_description="Vehicle accident.",
        )

    structured_llm.invoke.assert_not_called()


def test_empty_claim_description_raises_error(analysis_service):
    service, structured_llm = analysis_service

    with pytest.raises(
        ValueError,
        match="Claim description cannot be empty",
    ):
        service.analyze_claim(
            claim_id="CLM_AI_003",
            claim_description=" ",
        )

    structured_llm.invoke.assert_not_called()


def test_document_text_is_sent_to_llm(analysis_service):
    service, structured_llm = analysis_service

    structured_llm.invoke.return_value = AIFraudAnalysisResponse(
        claim_id="CLM_AI_004",
        suspicious_patterns=[],
        overall_assessment="No suspicious patterns identified.",
        requires_human_review=False,
    )

    service.analyze_claim(
        claim_id="CLM_AI_004",
        claim_description="Vehicle accident.",
        document_texts=[
            "Vehicle number: TS09AB1234",
        ],
    )

    messages = structured_llm.invoke.call_args.args[0]

    combined_message = "\n".join(
        str(message.content)
        for message in messages
    )

    assert "TS09AB1234" in combined_message


def test_service_uses_injected_llm(mock_llm):
    llm, structured_llm = mock_llm

    service = AIFraudAnalysisService(llm=llm)

    llm.with_structured_output.assert_called_once_with(
        AIFraudAnalysisResponse
    )


def test_response_claim_id_is_overridden(analysis_service):
    service, structured_llm = analysis_service

    structured_llm.invoke.return_value = AIFraudAnalysisResponse(
        claim_id="WRONG_ID",
        suspicious_patterns=[],
        overall_assessment="No suspicious patterns identified.",
        requires_human_review=False,
    )

    result = service.analyze_claim(
        claim_id="CLM_AI_005",
        claim_description="Vehicle accident.",
    )

    assert result.claim_id == "CLM_AI_005"
