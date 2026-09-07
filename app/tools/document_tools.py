from sqlalchemy.orm import Session
from langchain_core.tools import tool

from app.services.document_service import DocumentService


def create_document_tools(db: Session):

    @tool
    def get_document(document_id: str):
        """
        Retrieve an insurance document using its document ID.
        """
        service = DocumentService(db)

        return service.get_document(document_id)

    @tool
    def get_documents_by_claim(claim_id: str):
        """
        Retrieve all documents associated with an insurance claim.
        """
        service = DocumentService(db)

        return service.get_documents_by_claim(claim_id)

    return [
        get_document,
        get_documents_by_claim,
    ]