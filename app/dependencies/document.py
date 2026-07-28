from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.ingestion.extractors.pdf_extractor import PDFExtractor
from app.repositories.document_contents_repository import DocumentContentsRepository
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService


def get_document_service(
    db: Session = Depends(get_db),
) -> DocumentService:
    document_repository = DocumentRepository(db)
    document_contents_repository = DocumentContentsRepository(db)
    pdf_extractor = PDFExtractor()
    
    return DocumentService(
        document_repository=document_repository,
        document_contents_repository=document_contents_repository,
        pdf_extractor=pdf_extractor,
    )