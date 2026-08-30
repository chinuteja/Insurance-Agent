from datetime import date

from sqlalchemy import Date, Float, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

class Policy(Base):
    __tablename__ = "policies"

    policy_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.customer_id"),
        nullable=False
    )

    policy_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    vehicle_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    premium: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    coverage_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

class Claim(Base):
    __tablename__ = "claims"

    claim_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.customer_id"),
        nullable=False
    )

    policy_id: Mapped[str] = mapped_column(
        ForeignKey("policies.policy_id"),
        nullable=False
    )

    incident_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    claim_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    claim_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )

    claim_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    fraud_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    decision: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

class Document(Base):
    __tablename__ = "documents"

    document_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    claim_id: Mapped[str] = mapped_column(
        ForeignKey("claims.claim_id"),
        nullable=False
    )

    document_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    verification_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )