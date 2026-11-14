
from enum import Enum

from pydantic import BaseModel, Field


class AIFraudSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AIFraudFinding(BaseModel):
    finding_type: str = Field(
        min_length=1,
        description="Category of suspicious pattern detected.",
    )

    description: str = Field(
        min_length=1,
        description="Explanation of the suspicious pattern.",
    )

    severity: AIFraudSeverity

    evidence: list[str] = Field(
        min_length=1,
        description="Exact supporting details from the supplied claim data.",
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="LLM confidence in identifying this pattern.",
    )


class AIFraudAnalysisResponse(BaseModel):
    claim_id: str

    suspicious_patterns: list[AIFraudFinding] = Field(
        default_factory=list,
    )

    overall_assessment: str = Field(
        min_length=1,
    )

    requires_human_review: bool
