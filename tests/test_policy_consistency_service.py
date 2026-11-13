
from unittest.mock import MagicMock

import pytest

from app.services.policy_consistency_service import (
    PolicyConsistencyService,
)

from app.schemas.policy_consistency_schema import (
    PolicyConsistencyStatus,
    PolicyConsistencyResponse,
    PolicyConsistencyFinding,
    PolicyEvidence,
)


@pytest.fixture
def mock_retrieval_service():
    retrieval_service = MagicMock()

    retrieval_service.retrieve_policy_evidence.return_value = {
        "query": "accidental vehicle damage",
        "status": "SUCCESS",
        "message": "Relevant policy documents retrieved.",
        "results": [
            {
                "content": (
                    "The policy covers accidental damage "
                    "to the insured vehicle."
                ),
                "metadata": {
                    "source": "sample_policy.pdf",
                    "page": 1,
                },
                "score": 0.45,
            }
        ],
    }

    return retrieval_service


@pytest.fixture
def mock_llm():
    llm = MagicMock()
    structured_llm = MagicMock()

    llm.with_structured_output.return_value = structured_llm

    return llm, structured_llm


@pytest.fixture
def consistency_service(mock_retrieval_service, mock_llm):
    llm, structured_llm = mock_llm

    service = PolicyConsistencyService(
        retrieval_service=mock_retrieval_service,
        llm=llm,
    )

    return service, structured_llm


def test_consistent_document(
    consistency_service,
    mock_retrieval_service,
):
    service, structured_llm = consistency_service

    structured_llm.invoke.return_value = PolicyConsistencyResponse(
        document_type="REPAIR_ESTIMATE",
        overall_status=PolicyConsistencyStatus.CONSISTENT,
        findings=[
            PolicyConsistencyFinding(
                finding="Accidental damage coverage",
                explanation=(
                    "The policy supports accidental vehicle damage."
                ),
                status=PolicyConsistencyStatus.CONSISTENT,
                evidence=[
                    PolicyEvidence(
                        content=(
                            "The policy covers accidental damage "
                            "to the insured vehicle."
                        ),
                        source="sample_policy.pdf",
                        page=1,
                    )
                ],
            )
        ],
        recommendation="Continue with the next verification stage.",
    )

    result = service.validate_document(
        document_type="REPAIR_ESTIMATE",
        document_text="Vehicle damage occurred in an accident.",
    )

    assert result.overall_status == PolicyConsistencyStatus.CONSISTENT
    assert result.document_type == "REPAIR_ESTIMATE"
    assert len(result.findings) == 1

    mock_retrieval_service.retrieve_policy_evidence.assert_called_once()


def test_inconsistent_document(consistency_service):
    service, structured_llm = consistency_service

    structured_llm.invoke.return_value = PolicyConsistencyResponse(
        document_type="REPAIR_ESTIMATE",
        overall_status=PolicyConsistencyStatus.INCONSISTENT,
        findings=[
            PolicyConsistencyFinding(
                finding="Coverage contradiction",
                explanation=(
                    "The submitted information contradicts "
                    "the retrieved policy evidence."
                ),
                status=PolicyConsistencyStatus.INCONSISTENT,
            )
        ],
        recommendation="Send the finding for human review.",
    )

    result = service.validate_document(
        document_type="REPAIR_ESTIMATE",
        document_text="Submitted document information.",
    )

    assert result.overall_status == PolicyConsistencyStatus.INCONSISTENT
    assert result.findings[0].status == PolicyConsistencyStatus.INCONSISTENT


def test_needs_review_document(consistency_service):
    service, structured_llm = consistency_service

    structured_llm.invoke.return_value = PolicyConsistencyResponse(
        document_type="POLICE_REPORT",
        overall_status=PolicyConsistencyStatus.NEEDS_REVIEW,
        findings=[
            PolicyConsistencyFinding(
                finding="Unclear incident details",
                explanation="The available evidence is ambiguous.",
                status=PolicyConsistencyStatus.NEEDS_REVIEW,
            )
        ],
        recommendation="Manual verification is required.",
    )

    result = service.validate_document(
        document_type="POLICE_REPORT",
        document_text="Incident details are unclear.",
    )

    assert result.overall_status == PolicyConsistencyStatus.NEEDS_REVIEW


def test_insufficient_policy_evidence(
    consistency_service,
    mock_retrieval_service,
):
    service, structured_llm = consistency_service

    mock_retrieval_service.retrieve_policy_evidence.return_value = {
        "query": "policy query",
        "results": [],
        "status": "NO_RELEVANT_DOCUMENTS",
        "message": "No relevant policy information found.",
    }

    result = service.validate_document(
        document_type="REPAIR_ESTIMATE",
        document_text="Vehicle repair details.",
    )

    assert (
        result.overall_status
        == PolicyConsistencyStatus.INSUFFICIENT_EVIDENCE
    )

    assert result.findings == []

    # LLM should not be called without policy evidence.
    structured_llm.invoke.assert_not_called()


def test_empty_document_text(consistency_service):
    service, structured_llm = consistency_service

    with pytest.raises(ValueError, match="Document text cannot be empty"):
        service.validate_document(
            document_type="REPAIR_ESTIMATE",
            document_text="   ",
        )

    structured_llm.invoke.assert_not_called()


def test_empty_document_type(consistency_service):
    service, structured_llm = consistency_service

    with pytest.raises(ValueError, match="Document type cannot be empty"):
        service.validate_document(
            document_type="   ",
            document_text="Vehicle repair details.",
        )

    structured_llm.invoke.assert_not_called()


def test_invalid_k_value(consistency_service):
    service, structured_llm = consistency_service

    with pytest.raises(ValueError, match="k must be greater than zero"):
        service.validate_document(
            document_type="REPAIR_ESTIMATE",
            document_text="Vehicle repair details.",
            k=0,
        )

    structured_llm.invoke.assert_not_called()


def test_llm_receives_retrieved_policy_evidence(consistency_service):
    service, structured_llm = consistency_service

    structured_llm.invoke.return_value = PolicyConsistencyResponse(
        document_type="REPAIR_ESTIMATE",
        overall_status=PolicyConsistencyStatus.CONSISTENT,
        recommendation="Continue verification.",
    )

    service.validate_document(
        document_type="REPAIR_ESTIMATE",
        document_text="Accident vehicle damage.",
    )

    structured_llm.invoke.assert_called_once()

    messages = structured_llm.invoke.call_args.args[0]

    combined_message = "\n".join(
        str(message.content) for message in messages
    )

    assert "sample_policy.pdf" in combined_message
    assert "accidental damage" in combined_message.lower()
