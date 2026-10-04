from app.graph.claim_agent_state import ClaimAgentState


def build_claim_context(state: ClaimAgentState) -> str:
    claim = state["claim"]

    return f"""
Insurance Claim Analysis Context

Claim ID: {claim["claim_id"]}
Customer ID: {claim["customer_id"]}
Policy ID: {claim["policy_id"]}
Claim Type: {claim["claim_type"]}
Claim Amount: {claim["claim_amount"]}
Incident Date: {claim["incident_date"]}
Claim Date: {claim["claim_date"]}
Claim Status: {claim["status"]}
Description: {claim["description"]}

Policy Active: {state["policy_active"]}
Incident Covered: {state["covered"]}
Documents Present: {state["documents_present"]}

Eligibility Decision: {state["decision"]}
Decision Reason: {state["decision_reason"]}
""".strip()