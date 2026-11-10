
from enum import Enum
from pydantic import BaseModel, Field


class DocumentVerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    MISSING = "MISSING"
    INVALID = "INVALID"


class OverallVerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    INCOMPLETE = "INCOMPLETE"


class DocumentIssue(BaseModel):
    issue_type: str
    description: str


class DocumentVerificationResult(BaseModel):
    document_type: str
    status: DocumentVerificationStatus
    extracted_fields: dict = Field(default_factory=dict)
    issues: list[DocumentIssue] = Field(default_factory=list)


class ClaimDocumentVerificationResponse(BaseModel):
    claim_id: str
    overall_status: OverallVerificationStatus

    documents: list[DocumentVerificationResult] = Field(
        default_factory=list
    )

    missing_documents: list[str] = Field(
        default_factory=list
    )

    inconsistencies: list[str] = Field(
        default_factory=list
    )

    recommendation: str
