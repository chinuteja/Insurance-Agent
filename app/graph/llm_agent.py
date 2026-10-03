from sqlalchemy.orm import Session

from app.llm import create_llm
from app.tools.claim_tools import create_claim_tools


def create_llm_agent(db: Session):

    llm = create_llm()

    tools = create_claim_tools(db)

    llm_with_tools = llm.bind_tools(tools)

    return llm_with_tools