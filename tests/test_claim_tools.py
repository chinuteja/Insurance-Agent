from datetime import date

from app.database.models import Customer, Policy, Claim
from app.tools.claim_tools import create_claim_tools

from app.database.models import Customer, Policy, Claim, Document
from tests.conftest import db
def create_test_data(db):
    customer = Customer(
        customer_id="CUS_TEST_CLAIM_TOOL",
        name="Claim Tool Test Customer",
        email="claimtool@example.com",
        phone="4444444444",
    )

    policy = Policy(
        policy_id="POL_TEST_CLAIM_TOOL",
        customer_id="CUS_TEST_CLAIM_TOOL",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS88YY8888",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=25000.0,
        coverage_amount=1000000.0,
        status="ACTIVE",
    )

    claim = Claim(
        claim_id="CLM_TEST_TOOL",
        customer_id="CUS_TEST_CLAIM_TOOL",
        policy_id="POL_TEST_CLAIM_TOOL",
        incident_date=date(2026, 8, 15),
        claim_date=date(2026, 8, 20),
        claim_type="ACCIDENT",
        description="Vehicle accident for tool testing",
        claim_amount=150000.0,
        status="SUBMITTED",
        fraud_score=None,
        decision=None,
    )
    document = Document(
    document_id="DOC_TEST_CLAIM_TOOL",
    claim_id="CLM_TEST_TOOL",
    document_type="ACCIDENT_PHOTO",
    file_name="accident.jpg",
    storage_path="documents/CLM_TEST_TOOL/accident.jpg",
    verification_status="PENDING",
)

    db.add(customer)
    db.commit()

    db.add(policy)
    db.commit()

    db.add(claim)
    db.commit()
    db.add(document)
    db.commit()


def test_get_claim_tool(db):
    create_test_data(db)

    tools = create_claim_tools(db)
    get_claim = tools[0]

    result = get_claim.invoke({
        "claim_id": "CLM_TEST_TOOL"
    })

    assert result is not None
    assert result.claim_id == "CLM_TEST_TOOL"
    assert result.customer_id == "CUS_TEST_CLAIM_TOOL"
    assert result.policy_id == "POL_TEST_CLAIM_TOOL"
    assert result.status == "SUBMITTED"

def test_validate_claim_tool(db):
    create_test_data(db)

    tools = create_claim_tools(db)
    validate_claim = tools[1]

    result = validate_claim.invoke({
        "claim_id": "CLM_TEST_TOOL"
    })

    assert result is True