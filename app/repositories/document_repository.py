from sqlalchemy.orm import Session

from app.database.models import Document


class DocumentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, document: Document) -> Document:
        try:
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)

            return document

        except Exception:
            self.db.rollback()
            raise

    def get_by_id(self, document_id: str) -> Document | None:
        return (
            self.db.query(Document)
            .filter(Document.document_id == document_id)
            .first()
        )

    def get_by_claim_id(self, claim_id: str) -> list[Document]:
        return (
            self.db.query(Document)
            .filter(Document.claim_id == claim_id)
            .all()
        )


    def has_documents(self, claim_id: str) -> bool:
        documents = self.get_by_claim_id(claim_id)
        return len(documents) > 0