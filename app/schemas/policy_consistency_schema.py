
from enum import Enum

from pydantic import BaseModel, Field


class PolicyConsistencyStatus(str, Enum):
    CONSISTENT = "CONSISTENT"
    INCONSISTENT = "INCONSISTENT"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class PolicyEvidence(BaseModel):
    content: str
    source: str | None = None
    page: int | None = None
    relevance_score: float | None = None


class PolicyConsistencyFinding(BaseModel):
    finding: str
    explanation: str
    status: PolicyConsistencyStatus
    evidence: list[PolicyEvidence] = Field(default_factory=list)


class PolicyConsistencyResponse(BaseModel):
    document_type: str
    overall_status: PolicyConsistencyStatus
    findings: list[PolicyConsistencyFinding] = Field(
        default_factory=list
    )
    recommendation: str
