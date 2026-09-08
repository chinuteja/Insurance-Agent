from app.database.models import Customer, Policy, Claim
from app.graph.graph import create_claim_graph


def test_claim_graph(db):
    customer = Customer(
        customer_id="CUST_GRAPH_001",
        name="Graph Test Customer",
        email="graph@test.com",
        phone="8888888888",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_GRAPH_001",
        customer_id=customer.customer_id,
        policy_type="CAR",
        vehicle_number="TS10CD5678",
        start_date="2026-01-01",
        end_date="2026-12-31",
        premium=15000,
        coverage_amount=500000,
        status="ACTIVE",
    )

    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_GRAPH_001",
        customer_id=customer.customer_id,
        policy_id=policy.policy_id,
        incident_date="2026-06-01",
        claim_date="2026-06-02",
        claim_type="ACCIDENT",
        description="Vehicle accident",
        claim_amount=100000,
        status="SUBMITTED",
        fraud_score=None,
        decision=None,
    )

    db.add(claim)
    db.commit()

    graph = create_claim_graph(db)

    state = {
        "claim_id": "CLM_GRAPH_001",
        "claim_status": None,
        "policy_status": None,
        "covered": None,
        "documents_present": None,
        "decision": None,
    }

    result = graph.invoke(state)

    assert result["claim_id"] == "CLM_GRAPH_001"
    assert result["claim_status"] == "SUBMITTED"
def test_claim_graph_inactive_policy(db):
    customer = Customer(
        customer_id="CUST_GRAPH_002",
        name="Inactive Policy Customer",
        email="inactive@test.com",
        phone="7777777777",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_GRAPH_002",
        customer_id=customer.customer_id,
        policy_type="CAR",
        vehicle_number="TS10XY9999",
        start_date="2026-01-01",
        end_date="2026-12-31",
        premium=15000,
        coverage_amount=500000,
        status="INACTIVE",
    )

    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_GRAPH_002",
        customer_id=customer.customer_id,
        policy_id=policy.policy_id,
        incident_date="2026-06-01",
        claim_date="2026-06-02",
        claim_type="ACCIDENT",
        description="Vehicle accident",
        claim_amount=100000,
        status="SUBMITTED",
        fraud_score=None,
        decision=None,
    )

    db.add(claim)
    db.commit()

    graph = create_claim_graph(db)

    state = {
        "claim_id": "CLM_GRAPH_002",
        "claim_status": None,
        "policy_status": None,
        "covered": None,
        "documents_present": None,
        "decision": None,
    }

    result = graph.invoke(state)

    assert result["claim_id"] == "CLM_GRAPH_002"
    assert result["claim_status"] == "SUBMITTED"
    assert result["policy_status"] == "INACTIVE"
    assert result["decision"] == "REJECTED"