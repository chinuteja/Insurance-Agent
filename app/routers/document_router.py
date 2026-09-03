from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.schemas import Document
from app.services.document_service import DocumentService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.get("/{document_id}", response_model=Document)
def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    service = DocumentService(db)

    document = service.get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID {document_id} not found."
        )

    return document


@router.get("/claim/{claim_id}", response_model=list[Document])
def get_documents_by_claim(
    claim_id: str,
    db: Session = Depends(get_db)
):
    service = DocumentService(db)

    return service.get_documents_by_claim(claim_id)