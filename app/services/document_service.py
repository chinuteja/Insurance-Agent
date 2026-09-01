from sqlalchemy.orm import Session

from app.repositories.document_repository import DocumentRepository


class DocumentService:

    def __init__(self, db: Session):
        self.repository = DocumentRepository(db)

    def get_document(self, document_id: str):
        return self.repository.get_by_id(document_id)