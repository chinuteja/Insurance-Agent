import pytest

from app.database.connection import SessionLocal
from app.database.models import Customer, Policy, Claim, Document


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