from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.graph.claim_agent_graph import create_claim_agent_graph


router = APIRouter(
    prefix="/ai/claims",
    tags=["AI Claim Agent"],
)


class ClaimAgentRequest(BaseModel):
    claim_id: str
    message: str


class ClaimAgentResponse(BaseModel):
    claim_id: str
    intent: str | None = None
    response: str
    decision: str | None = None
    decision_reason: str | None = None


@router.post("/analyze", response_model=ClaimAgentResponse)
def analyze_claim(
    request: ClaimAgentRequest,
    db: Session = Depends(get_db),
):
    try:
        graph = create_claim_agent_graph(db)

        initial_state = {
            "claim_id": request.claim_id,
            "messages": [request.message],
            "intent": None,
            "claim": None,
            "policy_active": None,
            "covered": None,
            "documents_present": None,
            "decision": None,
            "decision_reason": None,
        }

        result = graph.invoke(initial_state)

        final_message = result["messages"][-1]

        if isinstance(final_message, str):
            response_text = final_message
        else:
            response_text = final_message.content

        return ClaimAgentResponse(
            claim_id=request.claim_id,
            intent=result.get("intent"),
            response=response_text,
            decision=result.get("decision"),
            decision_reason=result.get("decision_reason"),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the claim request.",
        )