from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService


def get_document_service(
    db: Session = Depends(get_db),
) -> DocumentService:
    repository = DocumentRepository(db)
    return DocumentService(repository)