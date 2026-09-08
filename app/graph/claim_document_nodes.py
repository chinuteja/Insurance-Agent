from sqlalchemy.orm import Session

from app.graph.claim_state import ClaimState
from app.services.document_service import DocumentService


def create_document_node(db: Session):

    def check_documents_node(state: ClaimState) -> dict:
        service = DocumentService(db)

        documents_present = service.has_documents(
            state["claim_id"]
        )

        return {
            "documents_present": documents_present
        }

    return check_documents_node