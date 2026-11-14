
from datetime import date

from app.database.models import Customer, Policy, Claim, Document
from app.repositories.claim_repository import ClaimRepository
from app.graph.claim_agent_decision import create_claim_decision_node


def create_decision_state(
    fraud_risk_score=10,
    fraud_risk_level="LOW",
    fraud_recommendation="Normal processing.",
):
    return {
        "claim_id": "CLM_DECISION",
        "messages": [],
        "claim": None,
        "policy_active": None,
        "covered": None,
        "documents_present": None,
        "decision": None,
        "decision_reason": None,
        "fraud_risk_score": fraud_risk_score,
        "fraud_risk_level": fraud_risk_level,
        "fraud_findings": [],
        "fraud_recommendation": fraud_recommendation,
    }


def test_claim_decision_eligible(db):
    customer = Customer(
        customer_id="CUST_DECISION",
        name="Decision Test Customer",
        email="decision@test.com",
        phone="9999999999",
    )
    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_DECISION",
        customer_id="CUST_DECISION",
        policy_type="AUTO",
        vehicle_number="TS09DEC123",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=20000,
        coverage_amount=500000,
        status="ACTIVE",
    )
    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_DECISION",
        customer_id="CUST_DECISION",
        policy_id="POL_DECISION",
        incident_date=date(2026, 6, 15),
        claim_date=date(2026, 6, 16),
        claim_type="ACCIDENT",
        description="Vehicle accident",
        claim_amount=100000,
        status="SUBMITTED",
    )

    repository = ClaimRepository(db)
    repository.create(claim)

    document = Document(
        document_id="DOC_DECISION",
        claim_id="CLM_DECISION",
        document_type="ACCIDENT_REPORT",
        file_name="accident_report.pdf",
        storage_path="/documents/accident_report.pdf",
        verification_status="VERIFIED",
    )
    db.add(document)
    db.commit()

    decision_node = create_claim_decision_node(db)

    result = decision_node(create_decision_state())

    assert result["decision"] == "ELIGIBLE_FOR_REVIEW"


def test_medium_fraud_risk_requires_review(db):
    decision_node = create_claim_decision_node(db)

    state = create_decision_state(
        fraud_risk_score=45,
        fraud_risk_level="MEDIUM",
        fraud_recommendation="Additional investigation required.",
    )

    result = decision_node(state)

    assert result["decision"] == "NEEDS_REVIEW"
    assert "Medium fraud risk" in result["decision_reason"]
    assert "45/100" in result["decision_reason"]


def test_high_fraud_risk_requires_human_investigation(db):
    decision_node = create_claim_decision_node(db)

    state = create_decision_state(
        fraud_risk_score=85,
        fraud_risk_level="HIGH",
        fraud_recommendation="Escalate for investigation.",
    )

    result = decision_node(state)

    assert result["decision"] == "NEEDS_REVIEW"
    assert "High fraud risk" in result["decision_reason"]
    assert "human investigation" in result["decision_reason"]


def test_missing_fraud_assessment_requires_review(db):
    decision_node = create_claim_decision_node(db)

    state = create_decision_state(
        fraud_risk_score=None,
        fraud_risk_level=None,
        fraud_recommendation="",
    )

    result = decision_node(state)

    assert result["decision"] == "NEEDS_REVIEW"
    assert "could not be completed" in result["decision_reason"]
