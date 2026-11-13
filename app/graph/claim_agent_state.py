
from typing import TypedDict


class ClaimAgentState(TypedDict):

    # Existing claim information
    claim_id: str
    messages: list
    intent: str | None

    # Existing policy and claim validation
    claim: dict | None
    policy_active: bool | None
    covered: bool | None
    documents_present: bool | None

    # Existing claim decision
    decision: str | None
    decision_reason: str | None

    # New document verification fields
    document_verification_status: str | None
    document_verification_results: list[dict] | None
    missing_documents: list[str] | None
    document_inconsistencies: list[str] | None
    document_recommendation: str | None
