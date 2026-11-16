
from datetime import date

from app.database.models import Claim, Customer, Document, Policy
from app.graph.claim_agent_graph import create_claim_agent_graph


def setup_claim_data(db, claim_id):
    customer = Customer(
        customer_id=f"CUS_{claim_id}",
        name="Integration Test Customer",
        email=f"{claim_id.lower()}@test.com",
        phone="9999999999",
    )

    db.add(customer)
    db.flush()

    policy = Policy(
        policy_id=f"POL_{claim_id}",
        customer_id=customer.customer_id,
        policy_type="MOTOR",
        vehicle_number="TS09AB1234",
        start_date=date(2025, 1, 1),
        end_date=date(2027, 12, 31),
        premium=10000,
        coverage_amount=500000,
        status="ACTIVE",
    )

    db.add(policy)
    db.flush()

    claim = Claim(
        claim_id=claim_id,
        customer_id=customer.customer_id,
        policy_id=policy.policy_id,
        incident_date=date(2026, 5, 10),
        claim_date=date(2026, 5, 11),
        claim_type="ACCIDENT",
        description="Vehicle accident",
        claim_amount=50000,
        status="SUBMITTED",
        fraud_score=0,
        decision="PENDING",
    )

    db.add(claim)
    db.flush()

    document = Document(
        document_id=f"DOC_{claim_id}",
        claim_id=claim_id,
        document_type="ACCIDENT_REPORT",
        file_name="accident_report.pdf",
        storage_path="/test/accident_report.pdf",
        verification_status="VERIFIED",
    )

    db.add(document)
    db.commit()


def invoke_graph(db, claim_id, message):
    graph = create_claim_agent_graph(db)

    state = {
        "claim_id": claim_id,
        "messages": [message],
        "intent": None,
        "claim": None,
        "policy_active": None,
        "covered": None,
        "documents_present": None,
        "decision": None,
        "decision_reason": None,
    }

    return graph.invoke(state)


def test_status_intent_integration(db):
    setup_claim_data(db, "CLM_INT_STATUS")

    result = invoke_graph(
        db,
        "CLM_INT_STATUS",
        "What is the status of my claim?",
    )

    assert result["intent"] == "STATUS"
    assert result["claim"]["claim_id"] == "CLM_INT_STATUS"
    assert result["claim"]["status"] == "SUBMITTED"


def test_coverage_intent_integration(db):
    setup_claim_data(db, "CLM_INT_COVERAGE")

    result = invoke_graph(
        db,
        "CLM_INT_COVERAGE",
        "Is my accident covered by my policy?",
    )

    assert result["intent"] == "COVERAGE"
    assert result["policy_active"] is True
    assert result["covered"] is True
    assert len(result["messages"]) > 1


def test_analysis_intent_integration(db):
    setup_claim_data(db, "CLM_INT_ANALYSIS")

    result = invoke_graph(
        db,
        "CLM_INT_ANALYSIS",
        "Analyze my claim and tell me whether it is eligible for review.",
    )

    assert result["intent"] == "ANALYSIS"
    assert result["claim"]["claim_id"] == "CLM_INT_ANALYSIS"
    assert result["policy_active"] is True
    assert result["covered"] is True
    assert result["documents_present"] is True

    assert result["document_verification_status"] == "INCOMPLETE"
    assert result["decision"] == "NEEDS_REVIEW"

    assert len(result["missing_documents"]) == 6
    assert len(result["messages"]) > 1


def test_general_intent_integration(db):
    result = invoke_graph(
        db,
        "",
        "What documents are generally required for a motor insurance claim?",
    )

    assert result["intent"] == "GENERAL"
    assert len(result["messages"]) > 1
    assert isinstance(result["messages"][-1], str)
    assert len(result["messages"][-1]) > 0


def test_high_fraud_risk_integration(db, monkeypatch):
    import app.graph.claim_agent_graph as graph_module

    setup_claim_data(db, "CLM_INT_HIGH_FRAUD")

    def mock_document_verification(db):
        def node(state):
            completed_agents = list(
                state.get("completed_agents") or []
            )
            if "document_verification" not in completed_agents:
                completed_agents.append("document_verification")

            return {
                "completed_agents": completed_agents,
                "document_verification_status": "VERIFIED",
                "document_verification_results": [],
                "missing_documents": [],
                "document_inconsistencies": [],
                "document_recommendation": "Documents verified.",
            }

        return node

    def mock_fraud_detection(db):
        def node(state):
            completed_agents = list(
                state.get("completed_agents") or []
            )
            if "fraud_detection" not in completed_agents:
                completed_agents.append("fraud_detection")

            return {
                "completed_agents": completed_agents,
                "fraud_risk_score": 85,
                "fraud_risk_level": "HIGH",
                "fraud_findings": [
                    {
                        "rule_id": "DUPLICATE_CLAIM",
                        "description": "Potential duplicate claim detected.",
                        "risk_points": 40,
                        "source": "RULE_BASED",
                        "evidence": ["A matching claim was found."],
                    }
                ],
                "fraud_recommendation": (
                    "Escalate for human investigation."
                ),
            }

        return node

    monkeypatch.setattr(
        graph_module,
        "create_document_verification_node",
        mock_document_verification,
    )

    monkeypatch.setattr(
        graph_module,
        "create_fraud_detection_node",
        mock_fraud_detection,
    )

    result = invoke_graph(
        db,
        "CLM_INT_HIGH_FRAUD",
        "Analyze my claim.",
    )

    assert result["fraud_risk_score"] == 85
    assert result["fraud_risk_level"] == "HIGH"
    assert result["decision"] == "NEEDS_REVIEW"

    assert "human investigation" in (
        result["decision_reason"].lower()
    )


def test_medium_fraud_risk_integration(db, monkeypatch):
    import app.graph.claim_agent_graph as graph_module

    setup_claim_data(db, "CLM_INT_MEDIUM_FRAUD")

    def mock_document_verification(db):
        def node(state):
            completed_agents = list(
                state.get("completed_agents") or []
            )
            if "document_verification" not in completed_agents:
                completed_agents.append("document_verification")

            return {
                "completed_agents": completed_agents,
                "document_verification_status": "VERIFIED",
                "document_verification_results": [],
                "missing_documents": [],
                "document_inconsistencies": [],
                "document_recommendation": "Documents verified.",
            }

        return node

    def mock_fraud_detection(db):
        def node(state):
            completed_agents = list(
                state.get("completed_agents") or []
            )
            if "fraud_detection" not in completed_agents:
                completed_agents.append("fraud_detection")

            return {
                "completed_agents": completed_agents,
                "fraud_risk_score": 45,
                "fraud_risk_level": "MEDIUM",
                "fraud_findings": [],
                "fraud_recommendation": (
                    "Additional investigation required."
                ),
            }

        return node

    monkeypatch.setattr(
        graph_module,
        "create_document_verification_node",
        mock_document_verification,
    )

    monkeypatch.setattr(
        graph_module,
        "create_fraud_detection_node",
        mock_fraud_detection,
    )

    result = invoke_graph(
        db,
        "CLM_INT_MEDIUM_FRAUD",
        "Analyze my claim.",
    )

    assert result["fraud_risk_score"] == 45
    assert result["fraud_risk_level"] == "MEDIUM"
    assert result["decision"] == "NEEDS_REVIEW"

    assert "additional investigation" in (
        result["decision_reason"].lower()
    )


def test_low_fraud_risk_integration(db, monkeypatch):
    import app.graph.claim_agent_graph as graph_module

    setup_claim_data(db, "CLM_INT_LOW_FRAUD")

    def mock_document_verification(db):
        def node(state):
            completed_agents = list(
                state.get("completed_agents") or []
            )
            if "document_verification" not in completed_agents:
                completed_agents.append("document_verification")

            return {
                "completed_agents": completed_agents,
                "document_verification_status": "VERIFIED",
                "document_verification_results": [],
                "missing_documents": [],
                "document_inconsistencies": [],
                "document_recommendation": "Documents verified.",
            }

        return node

    def mock_fraud_detection(db):
        def node(state):
            completed_agents = list(
                state.get("completed_agents") or []
            )
            if "fraud_detection" not in completed_agents:
                completed_agents.append("fraud_detection")

            return {
                "completed_agents": completed_agents,
                "fraud_risk_score": 10,
                "fraud_risk_level": "LOW",
                "fraud_findings": [],
                "fraud_recommendation": "Normal processing.",
            }

        return node

    monkeypatch.setattr(
        graph_module,
        "create_document_verification_node",
        mock_document_verification,
    )

    monkeypatch.setattr(
        graph_module,
        "create_fraud_detection_node",
        mock_fraud_detection,
    )

    result = invoke_graph(
        db,
        "CLM_INT_LOW_FRAUD",
        "Analyze my claim.",
    )

    assert result["fraud_risk_score"] == 10
    assert result["fraud_risk_level"] == "LOW"
    assert result["decision"] == "ELIGIBLE_FOR_REVIEW"

def test_document_verification_failure_routes_to_manual_review(
    db,
    monkeypatch,
):
    import app.graph.claim_agent_graph as graph_module

    claim_id = "CLM_INT_DOC_FAILURE"
    setup_claim_data(db, claim_id)

    execution_count = {
        "document_verification": 0,
        "fraud_detection": 0,
    }

    # Force the analysis intent so the test focuses on orchestration.
    def mock_intent_node(db):
        def node(state):
            return {"intent": "ANALYSIS"}

        return node

    # Simulate a document verification execution failure.
    def mock_document_verification(db):
        def node(state):
            execution_count["document_verification"] += 1

            errors = list(state.get("agent_errors") or [])
            errors.append({
                "agent": "document_verification",
                "error": "Simulated document extraction failure.",
            })

            return {
                "agent_errors": errors,
                "requires_human_review": True,
                "current_agent": None,
                "document_verification_status": "NEEDS_REVIEW",
                "document_recommendation": (
                    "Manual document verification is required."
                ),
            }

        return node

    # Fraud detection must not execute after the document agent fails.
    def mock_fraud_detection(db):
        def node(state):
            execution_count["fraud_detection"] += 1

            return {
                "completed_agents": ["fraud_detection"],
                "fraud_risk_score": 10,
                "fraud_risk_level": "LOW",
                "fraud_findings": [],
                "fraud_recommendation": "Normal processing.",
            }

        return node

    # Avoid invoking the actual LLM response during this test.
    def mock_llm_response(db):
        def node(state):
            return {
                "messages": state.get("messages", []) + [
                    "Claim requires manual review."
                ]
            }

        return node

    monkeypatch.setattr(
        graph_module,
        "create_claim_intent_node",
        mock_intent_node,
    )

    monkeypatch.setattr(
        graph_module,
        "create_document_verification_node",
        mock_document_verification,
    )

    monkeypatch.setattr(
        graph_module,
        "create_fraud_detection_node",
        mock_fraud_detection,
    )

    monkeypatch.setattr(
        graph_module,
        "create_claim_llm_response_node",
        mock_llm_response,
    )

    result = invoke_graph(
        db,
        claim_id,
        "Analyze my claim.",
    )

    # Document verification must execute exactly once.
    assert execution_count["document_verification"] == 1

    # Fraud detection must not execute after the failure.
    assert execution_count["fraud_detection"] == 0

    # The failure must be recorded.
    assert result["agent_errors"]
    assert (
        result["agent_errors"][0]["agent"]
        == "document_verification"
    )

    # Human review must be mandatory.
    assert result["requires_human_review"] is True

    # The decision node must prevent normal processing.
    assert result["decision"] == "NEEDS_REVIEW"
    assert "failed" in result["decision_reason"].lower()
    assert "manual review" in result["decision_reason"].lower()
