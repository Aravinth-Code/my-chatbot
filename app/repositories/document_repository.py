from uuid import UUID
from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.enums.document_status import DocumentStatus

class DocumentRepository:

    def __init__(self, db: Session):
        self.db = db
        
    def create(self, document: Document) -> Document:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
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
    
    def update_status(self, document: Document, status: DocumentStatus) -> Document:
        document.status = status
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def delete(self, document: Document) -> None:
        self.db.delete(document)
        self.db.commit()