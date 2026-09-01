from datetime import date

from app.database.models import Claim, Customer, Document, Policy
from app.exceptions.business_exceptions import ClaimNotSubmittedException, PolicyNotActiveException
from app.exceptions.business_exceptions import PolicyNotActiveException
from app.repositories.claim_repository import ClaimRepository
from app.repositories.document_repository import DocumentRepository
from app.services.claim_service import ClaimService


def create_test_claim(db, claim_id: str, claim_status: str, policy_status: str):
    customer = Customer(
        customer_id=f"CUS_{claim_id}",
        name="Validation Test Customer",
        email=f"{claim_id.lower()}@example.com",
        phone="2222222222",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id=f"POL_{claim_id}",
        customer_id=f"CUS_{claim_id}",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS14KL1234",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=30000,
        coverage_amount=1000000,
        status=policy_status,
    )

    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id=claim_id,
        customer_id=f"CUS_{claim_id}",
        policy_id=f"POL_{claim_id}",
        incident_date=date(2026, 8, 25),
        claim_date=date(2026, 8, 26),
        claim_type="ACCIDENT",
        description="Vehicle damaged in an accident",
        claim_amount=150000,
        status=claim_status,
    )

    repository = ClaimRepository(db)

    return repository.create(claim)


def test_submitted_claim_with_active_policy_is_valid(db):
    create_test_claim(
        db,
        "CLM_ACTIVE_POLICY",
        "SUBMITTED",
        "ACTIVE",
    )

    service = ClaimService(db)

    result = service.validate_claim("CLM_ACTIVE_POLICY")

    assert result is False


def test_submitted_claim_with_expired_policy_is_invalid(db):
    create_test_claim(
        db,
        "CLM_EXPIRED_POLICY",
        "SUBMITTED",
        "EXPIRED",
    )

    service = ClaimService(db)

    try:
        service.validate_claim("CLM_EXPIRED_POLICY")
        assert False, "Expected PolicyNotActiveException"
    except PolicyNotActiveException as exc:
        assert str(exc) == (
            "Policy with ID POL_CLM_EXPIRED_POLICY is not active."
        )


def test_rejected_claim_is_invalid(db):
    create_test_claim(
        db,
        "CLM_REJECTED",
        "REJECTED",
        "ACTIVE",
    )

    service = ClaimService(db)

    try:
        service.validate_claim("CLM_REJECTED")
        assert False, "Expected ClaimNotSubmittedException"
    except ClaimNotSubmittedException as exc:
        assert str(exc) == (
            "Claim with ID CLM_REJECTED is not submitted."
        )
def test_claim_with_incident_outside_policy_period_is_invalid(db):
    create_test_claim(
        db,
        "CLM_OUTSIDE_POLICY",
        "SUBMITTED",
        "ACTIVE",
    )

    # Get the claim and move its incident date
    repository = ClaimRepository(db)
    claim = repository.get_by_id("CLM_OUTSIDE_POLICY")

    claim.incident_date = date(2027, 1, 10)
    db.commit()

    service = ClaimService(db)

    result = service.validate_claim("CLM_OUTSIDE_POLICY")

    assert result is False

def test_claim_with_document_is_valid(db):
    create_test_claim(
        db,
        "CLM_WITH_DOCUMENT",
        "SUBMITTED",
        "ACTIVE",
    )

    document = Document(
        document_id="DOC_CLAIM_VALIDATION",
        claim_id="CLM_WITH_DOCUMENT",
        document_type="POLICE_REPORT",
        file_name="police_report.pdf",
        storage_path="/documents/police_report.pdf",
        verification_status="PENDING",
    )

    repository = DocumentRepository(db)
    repository.create(document)

    service = ClaimService(db)

    result = service.validate_claim("CLM_WITH_DOCUMENT")

    assert result is True


def test_claim_without_document_is_invalid(db):
    create_test_claim(
        db,
        "CLM_WITHOUT_DOCUMENT",
        "SUBMITTED",
        "ACTIVE",
    )

    service = ClaimService(db)

    result = service.validate_claim("CLM_WITHOUT_DOCUMENT")

    assert result is False