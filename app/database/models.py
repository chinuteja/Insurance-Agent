from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Date, Float, ForeignKey, String
from datetime import date
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