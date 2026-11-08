import pytest

from app.database.connection import SessionLocal
from app.database.models import Customer, Policy, Claim, Document
from tests.test_document_loader import create_sample_pdf

@pytest.fixture
def db():
    session = SessionLocal()

    try:
        yield session

    finally:
        session.query(Document).delete()
        session.query(Claim).delete()
        session.query(Policy).delete()
        session.query(Customer).delete()

        session.commit()
        session.close()
@pytest.fixture
def sample_policy_pdf(tmp_path):
    file_path = tmp_path / "sample_policy.pdf"

    create_sample_pdf(file_path)

    return str(file_path)