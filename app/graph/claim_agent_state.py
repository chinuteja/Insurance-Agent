from typing import TypedDict


class ClaimAgentState(TypedDict):
    claim_id: str
    messages: list
    claim: dict | None
    policy_active: bool | None
    covered: bool | None
    documents_present: bool | None
    decision: str | None