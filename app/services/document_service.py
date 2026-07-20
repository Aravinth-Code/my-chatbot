from uuid import UUID
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository

class DocumentService:

    def __init__(self, repository: DocumentRepository):
        self.document_repository = repository
        
        
    def create_document(self, document: Document) -> Document:
        return self.document_repository.create(document)
    
    def get_document(self, document_id: UUID) -> Document | None:
        return self.document_repository.get_by_id(document_id)