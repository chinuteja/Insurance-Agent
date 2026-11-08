from datetime import date

from app.database.connection import SessionLocal
from app.database.models import Customer, Policy, Claim, Document


def seed_data():
    db = SessionLocal()

    try:
        # 1. Insert Customer
        customer = Customer(
            customer_id="CUS_API_001",
            name="Rahul Sharma",
            email="rahul@example.com",
            phone="9876543210",
        )

        db.add(customer)
        db.flush()

        # 2. Insert Policy
        policy = Policy(
            policy_id="POL_API_001",
            customer_id="CUS_API_001",
            policy_type="COMPREHENSIVE",
            vehicle_number="TS09AB1234",
            start_date=date(2026, 1, 1),
            end_date=date(2027, 12, 31),
            premium=15000.0,
            coverage_amount=500000.0,
            status="ACTIVE",
        )

        db.add(policy)
        db.flush()

        # 3. Insert Claim
        claim = Claim(
            claim_id="CLM_API_001",
            customer_id="CUS_API_001",
            policy_id="POL_API_001",
            incident_date=date(2026, 10, 15),
            claim_date=date(2026, 10, 16),
            claim_type="ACCIDENT",
            description="Vehicle damaged in a road accident.",
            claim_amount=75000.0,
            status="SUBMITTED",
            fraud_score=None,
            decision=None,
        )

        db.add(claim)
        db.flush()

        # 4. Insert Document
        document = Document(
            document_id="DOC_API_001",
            claim_id="CLM_API_001",
            document_type="POLICE_REPORT",
            file_name="police_report.pdf",
            storage_path="sample_documents/police_report.pdf",
            verification_status="PENDING",
        )

        db.add(document)

        db.commit()

        print("Sample insurance data inserted successfully!")

    except Exception as exc:
        db.rollback()
        print(f"Error inserting sample data: {exc}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()