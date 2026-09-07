from datetime import date

from app.database.models import Customer, Policy, Claim, Document
from app.tools.document_tools import create_document_tools


def create_test_data(db):
    customer = Customer(
        customer_id="CUS_TEST_DOCUMENT_TOOL",
        name="Document Tool Test Customer",
        email="documenttool@example.com",
        phone="3333333333",
    )

    policy = Policy(
        policy_id="POL_TEST_DOCUMENT_TOOL",
        customer_id="CUS_TEST_DOCUMENT_TOOL",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS77XX7777",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=25000.0,
        coverage_amount=1000000.0,
        status="ACTIVE",
    )

    claim = Claim(
        claim_id="CLM_TEST_DOCUMENT_TOOL",
        customer_id="CUS_TEST_DOCUMENT_TOOL",
        policy_id="POL_TEST_DOCUMENT_TOOL",
        incident_date=date(2026, 8, 15),
        claim_date=date(2026, 8, 20),
        claim_type="ACCIDENT",
        description="Vehicle accident for document tool testing",
        claim_amount=150000.0,
        status="SUBMITTED",
        fraud_score=None,
        decision=None,
    )

    document = Document(
        document_id="DOC_TEST_TOOL",
        claim_id="CLM_TEST_DOCUMENT_TOOL",
        document_type="ACCIDENT_PHOTO",
        file_name="accident.jpg",
        storage_path="documents/CLM_TEST_DOCUMENT_TOOL/accident.jpg",
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


def test_get_document_tool(db):
    create_test_data(db)

    tools = create_document_tools(db)
    get_document = tools[0]

    result = get_document.invoke({
        "document_id": "DOC_TEST_TOOL"
    })

    assert result is not None
    assert result.document_id == "DOC_TEST_TOOL"
    assert result.claim_id == "CLM_TEST_DOCUMENT_TOOL"
    assert result.document_type == "ACCIDENT_PHOTO"
    assert result.verification_status == "PENDING"

def test_get_documents_by_claim_tool(db):
    create_test_data(db)

    tools = create_document_tools(db)
    get_documents_by_claim = tools[1]

    result = get_documents_by_claim.invoke({
        "claim_id": "CLM_TEST_DOCUMENT_TOOL"
    })

    assert len(result) == 1
    assert result[0].document_id == "DOC_TEST_TOOL"
    assert result[0].claim_id == "CLM_TEST_DOCUMENT_TOOL"