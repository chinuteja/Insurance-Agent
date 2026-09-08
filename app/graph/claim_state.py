from typing import TypedDict


class ClaimState(TypedDict):
    claim_id: str
    claim_status: str | None
    policy_status: str | None
    covered: bool | None
    documents_present: bool | None
    decision: str | None