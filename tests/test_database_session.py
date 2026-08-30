from app.database.connection import SessionLocal


def test_database_session():
    db = SessionLocal()

    try:
        assert db is not None
    finally:
        db.close()