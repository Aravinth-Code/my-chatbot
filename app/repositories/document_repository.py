from uuid import UUID
from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.document_history import DocumentHistory
from app.models.enums.document_status import DocumentStatus

class DocumentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, document: Document) -> Document:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        self._record_history(document.id, document.status)
        return document
    
    def get_by_id(self, document_id: UUID) -> Document | None:
        return (
            self.db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )
    
    def get_by_checksum(self, checksum: str) -> Document | None:
        return (
            self.db.query(Document)
            .filter(Document.checksum == checksum)
            .first()
        )
    
    def update_status(
        self,
        document: Document,
        status: DocumentStatus,
        error_message: str | None = None,
    ) -> Document:
        document.status = status
        if error_message is not None:
            document.error_message = error_message
        self.db.commit()
        self.db.refresh(document)
        self._record_history(document.id, status, error_message)
        return document

    def _record_history(
        self,
        document_id: UUID,
        status: DocumentStatus,
        error_message: str | None = None,
    ) -> None:
        self.db.add(DocumentHistory(document_id=document_id, status=status, error_message=error_message))
        self.db.commit()

    def delete(self, document: Document) -> None:
        self.db.delete(document)
        self.db.commit()