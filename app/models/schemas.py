from datetime import date
from enum import Enum

from pydantic import BaseModel, EmailStr


class PolicyType(str, Enum):
    COMPREHENSIVE = "COMPREHENSIVE"
    THIRD_PARTY = "THIRD_PARTY"


class ClaimType(str, Enum):
    ACCIDENT = "ACCIDENT"
    THEFT = "THEFT"
    NATURAL_DISASTER = "NATURAL_DISASTER"


class ClaimStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class Customer(BaseModel):
    customer_id: str
    name: str
    email: EmailStr
    phone: str


class Policy(BaseModel):
    policy_id: str
    customer_id: str
    policy_type: PolicyType
    vehicle_number: str
    start_date: date
    end_date: date
    premium: float
    coverage_amount: float
    status: str


class Claim(BaseModel):
    claim_id: str
    customer_id: str
    policy_id: str
    incident_date: date
    claim_date: date
    claim_type: ClaimType
    description: str
    claim_amount: float
    status: ClaimStatus
    fraud_score: float | None = None
    decision: str | None = None


class Document(BaseModel):
    document_id: str
    claim_id: str
    document_type: str
    file_name: str
    storage_path: str
    verification_status: str