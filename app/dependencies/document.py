from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.pipeline.chunkers.recursive_chunker import RecursiveChunker
from app.pipeline.extractors.pdf_extractor import PDFExtractor
from app.pipeline.cleaners.text_cleaner import TextCleaner

from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_contents_repository import DocumentContentsRepository
from app.repositories.document_repository import DocumentRepository
from app.services.document_chunk_service import DocumentChunkService
from app.services.document_service import DocumentService


def get_document_service(
    db: Session = Depends(get_db),
) -> DocumentService:
    document_repository = DocumentRepository(db)
    document_contents_repository = DocumentContentsRepository(db)
    document_chunk_repository = DocumentChunkRepository(db)
    pdf_extractor = PDFExtractor()
    text_cleaner = TextCleaner()
    recursive_chunker = RecursiveChunker()
    
    chunk_service = DocumentChunkService(
        document_contents_repository=document_contents_repository,
        document_chunk_repository=document_chunk_repository,
        chunker=recursive_chunker,
    )
        
    return DocumentService(
        document_repository=document_repository,
        document_contents_repository=document_contents_repository,
        pdf_extractor=pdf_extractor,
        text_cleaner=text_cleaner,
        chunk_service = chunk_service
    )