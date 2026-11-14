
from enum import Enum

from pydantic import BaseModel, Field


class FraudRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class FraudFindingSource(str, Enum):
    RULE_BASED = "RULE_BASED"
    AI_ANALYSIS = "AI_ANALYSIS"


class FraudFinding(BaseModel):
    rule_id: str
    description: str

    risk_points: int = Field(
        ge=0,
        le=100,
    )

    source: FraudFindingSource

    evidence: list[str] = Field(
        default_factory=list,
    )


class FraudDetectionResponse(BaseModel):
    claim_id: str

    risk_score: int = Field(
        ge=0,
        le=100,
    )

    risk_level: FraudRiskLevel

    findings: list[FraudFinding] = Field(
        default_factory=list,
    )

    recommendation: str
