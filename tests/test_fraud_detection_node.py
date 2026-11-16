from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

import app.graph.fraud_detection_node as fraud_node_module


def create_claim_state():
    return {
        "claim_id": "CLM_TEST_001",
        "claim": {
            "claim_id": "CLM_TEST_001",
            "customer_id": "CUS_TEST_001",
            "policy_id": "POL_TEST_001",
            "incident_date": "2026-01-10",
            "claim_date": "2026-01-11",
            "claim_type": "ACCIDENT",
            "description": "Vehicle collision with another car.",
            "claim_amount": 150000,
        },
    }


def setup_node_dependencies(monkeypatch):
    db = MagicMock()

    claim_repository = MagicMock()
    claim_repository.find_duplicate_claim.return_value = False
    claim_repository.count_recent_claims.return_value = 0

    policy_service = MagicMock()
    policy_service.get_policy.return_value = SimpleNamespace(
        start_date=date(2025, 1, 1)
    )

    document_service = MagicMock()
    document_service.get_documents_by_claim.return_value = [
        SimpleNamespace(
            file_name="police_report.txt",
            storage_path="fake/police_report.txt",
        )
    ]

    extraction_service = MagicMock()
    extraction_service.extract_text.return_value = {
        "content": "Police report: vehicle collision occurred."
    }

    fraud_service = MagicMock()
    fraud_service.detect_fraud.return_value = SimpleNamespace(
        risk_score=10,
        risk_level=SimpleNamespace(value="LOW"),
        findings=[],
        recommendation="Normal processing.",
    )

    monkeypatch.setattr(
        fraud_node_module,
        "ClaimRepository",
        lambda db: claim_repository,
    )
    monkeypatch.setattr(
        fraud_node_module,
        "PolicyService",
        lambda db: policy_service,
    )
    monkeypatch.setattr(
        fraud_node_module,
        "DocumentService",
        lambda db: document_service,
    )
    monkeypatch.setattr(
        fraud_node_module,
        "DocumentExtractionService",
        lambda: extraction_service,
    )
    monkeypatch.setattr(
        fraud_node_module,
        "FraudDetectionService",
        lambda: fraud_service,
    )

    node = fraud_node_module.create_fraud_detection_node(db)

    return (
        node,
        claim_repository,
        policy_service,
        document_service,
        extraction_service,
        fraud_service,
    )


def test_extraction_failure_returns_no_risk_score(monkeypatch):
    (
        node,
        _,
        _,
        _,
        extraction_service,
        fraud_service,
    ) = setup_node_dependencies(monkeypatch)

    extraction_service.extract_text.side_effect = Exception(
        "Unable to read document"
    )

    result = node(create_claim_state())

    assert result["fraud_risk_score"] is None
    assert result["fraud_risk_level"] is None
    assert result["fraud_findings"] == []
    assert "Manual document review is required" in (
        result["fraud_recommendation"]
    )

    # A failed assessment must not be marked as completed.
    assert "fraud_detection" not in (
        result.get("completed_agents") or []
    )

    # The failure must be recorded for supervisor handling.
    assert any(
        error["agent"] == "fraud_detection"
        for error in result["agent_errors"]
    )

    assert result["requires_human_review"] is True
    assert result["current_agent"] is None

    fraud_service.detect_fraud.assert_not_called()


def test_successful_extraction_runs_fraud_detection(monkeypatch):
    (
        node,
        _,
        _,
        _,
        _,
        fraud_service,
    ) = setup_node_dependencies(monkeypatch)

    result = node(create_claim_state())

    assert result["fraud_risk_score"] == 10
    assert result["fraud_risk_level"] == "LOW"
    assert result["fraud_findings"] == []
    assert result["fraud_recommendation"] == "Normal processing."

    # A successful assessment must be marked as completed.
    assert "fraud_detection" in result["completed_agents"]

    # A successful assessment must not record an execution error.
    assert not result.get("agent_errors")

    # This successful low-risk assessment does not itself require review.
    assert result.get("requires_human_review") is not True

    assert result["agent_results"]["fraud_detection"][
        "fraud_risk_score"
    ] == 10

    assert result["agent_results"]["fraud_detection"][
        "fraud_risk_level"
    ] == "LOW"

    assert result["current_agent"] is None

    fraud_service.detect_fraud.assert_called_once()


def test_missing_claim_stops_assessment(monkeypatch):
    node, _, _, _, _, fraud_service = setup_node_dependencies(
        monkeypatch
    )

    result = node({
        "claim_id": "CLM_MISSING",
        "claim": None,
    })

    assert result["fraud_risk_score"] is None
    assert result["fraud_risk_level"] is None
    assert "claim was not found" in result["fraud_recommendation"]

    assert "fraud_detection" not in (
        result.get("completed_agents") or []
    )
    assert result["requires_human_review"] is True
    assert any(
        error["agent"] == "fraud_detection"
        for error in result["agent_errors"]
    )

    fraud_service.detect_fraud.assert_not_called()


def test_missing_policy_stops_assessment(monkeypatch):
    (
        node,
        _,
        policy_service,
        _,
        _,
        fraud_service,
    ) = setup_node_dependencies(monkeypatch)

    policy_service.get_policy.return_value = None

    result = node(create_claim_state())

    assert result["fraud_risk_score"] is None
    assert result["fraud_risk_level"] is None
    assert "Manual review is required" in (
        result["fraud_recommendation"]
    )

    assert "fraud_detection" not in (
        result.get("completed_agents") or []
    )
    assert result["requires_human_review"] is True
    assert any(
        error["agent"] == "fraud_detection"
        for error in result["agent_errors"]
    )

    fraud_service.detect_fraud.assert_not_called()


def test_duplicate_claim_is_forwarded_to_fraud_service(monkeypatch):
    (
        node,
        claim_repository,
        _,
        _,
        _,
        fraud_service,
    ) = setup_node_dependencies(monkeypatch)

    claim_repository.find_duplicate_claim.return_value = True

    fraud_service.detect_fraud.return_value = SimpleNamespace(
        risk_score=40,
        risk_level=SimpleNamespace(value="MEDIUM"),
        findings=[],
        recommendation="Additional investigation required.",
    )

    result = node(create_claim_state())

    claim_repository.find_duplicate_claim.assert_called_once()
    fraud_service.detect_fraud.assert_called_once()

    call_arguments = fraud_service.detect_fraud.call_args.kwargs

    assert call_arguments["duplicate_found"] is True
    assert result["fraud_risk_score"] == 40
    assert result["fraud_risk_level"] == "MEDIUM"


def test_recent_policy_information_is_forwarded(monkeypatch):
    (
        node,
        _,
        policy_service,
        _,
        _,
        fraud_service,
    ) = setup_node_dependencies(monkeypatch)

    policy_service.get_policy.return_value = SimpleNamespace(
        start_date=date(2026, 1, 1)
    )

    fraud_service.detect_fraud.return_value = SimpleNamespace(
        risk_score=15,
        risk_level=SimpleNamespace(value="LOW"),
        findings=[],
        recommendation="Continue normal checks.",
    )

    result = node(create_claim_state())

    call_arguments = fraud_service.detect_fraud.call_args.kwargs

    assert call_arguments["policy_start_date"] == date(2026, 1, 1)
    assert call_arguments["incident_date"] == date(2026, 1, 10)
    assert result["fraud_risk_score"] == 15

    fraud_service.detect_fraud.assert_called_once()


def test_multiple_recent_claims_are_forwarded(monkeypatch):
    (
        node,
        claim_repository,
        _,
        _,
        _,
        fraud_service,
    ) = setup_node_dependencies(monkeypatch)

    claim_repository.count_recent_claims.return_value = 4

    fraud_service.detect_fraud.return_value = SimpleNamespace(
        risk_score=20,
        risk_level=SimpleNamespace(value="LOW"),
        findings=[],
        recommendation="Continue normal checks.",
    )

    result = node(create_claim_state())

    claim_repository.count_recent_claims.assert_called_once()

    call_arguments = fraud_service.detect_fraud.call_args.kwargs
    assert call_arguments["recent_claim_count"] == 4

    repository_arguments = (
        claim_repository.count_recent_claims.call_args.kwargs
    )
    assert repository_arguments["window_days"] == 90

    assert result["fraud_risk_score"] == 20
    fraud_service.detect_fraud.assert_called_once()


def test_high_claim_amount_is_forwarded(monkeypatch):
    (
        node,
        _,
        _,
        _,
        _,
        fraud_service,
    ) = setup_node_dependencies(monkeypatch)

    state = create_claim_state()
    state["claim"]["claim_amount"] = 350000

    fraud_service.detect_fraud.return_value = SimpleNamespace(
        risk_score=20,
        risk_level=SimpleNamespace(value="LOW"),
        findings=[],
        recommendation="Continue normal checks.",
    )

    result = node(state)

    call_arguments = fraud_service.detect_fraud.call_args.kwargs

    assert call_arguments["claim_amount"] == 350000
    assert result["fraud_risk_score"] == 20

    fraud_service.detect_fraud.assert_called_once()


def test_document_text_is_forwarded_to_fraud_service(monkeypatch):
    (
        node,
        _,
        _,
        _,
        extraction_service,
        fraud_service,
    ) = setup_node_dependencies(monkeypatch)

    suspicious_text = (
        "Police report states incident occurred on January 10. "
        "Repair estimate mentions January 15."
    )

    extraction_service.extract_text.return_value = {
        "content": suspicious_text
    }

    node(create_claim_state())

    call_arguments = fraud_service.detect_fraud.call_args.kwargs

    assert suspicious_text in call_arguments["document_texts"]
    fraud_service.detect_fraud.assert_called_once()


def test_ai_fraud_findings_are_returned_by_node(monkeypatch):
    (
        node,
        _,
        _,
        _,
        _,
        fraud_service,
    ) = setup_node_dependencies(monkeypatch)

    ai_finding = {
        "rule_id": "AI_DATE_INCONSISTENCY",
        "description": "Incident dates differ across submitted documents.",
        "risk_points": 20,
        "source": "AI_ANALYSIS",
        "evidence": [
            "Police report states January 10.",
            "Repair estimate states January 15.",
        ],
    }

    fraud_service.detect_fraud.return_value = SimpleNamespace(
        risk_score=20,
        risk_level=SimpleNamespace(value="LOW"),
        findings=[
            SimpleNamespace(
                model_dump=lambda mode: ai_finding
            )
        ],
        recommendation="Manual investigation recommended.",
    )

    result = node(create_claim_state())

    assert result["fraud_findings"] == [ai_finding]
    assert result["fraud_findings"][0]["source"] == "AI_ANALYSIS"
    assert result["fraud_risk_score"] == 20
    assert result["fraud_recommendation"] == (
        "Manual investigation recommended."
    )
