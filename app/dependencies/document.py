from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.pipeline.chunkers.recursive_chunker import RecursiveChunker
from app.pipeline.embeddings.openai_embeddings import OpenAIEmbeddings
from app.pipeline.extractors.pdf_extractor import PDFExtractor
from app.pipeline.extractors.webpage_extractor import WebPageExtractor
from app.pipeline.cleaners.text_cleaner import TextCleaner
from app.pipeline.loaders.url_fetcher import UrlFetcher

from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_contents_repository import DocumentContentsRepository
from app.repositories.document_repository import DocumentRepository
from app.services.document_chunk_service import DocumentChunkService
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService


def get_document_service(
    db: Session = Depends(get_db),
) -> DocumentService:
    document_repository = DocumentRepository(db)
    document_contents_repository = DocumentContentsRepository(db)
    document_chunk_repository = DocumentChunkRepository(db)
    pdf_extractor = PDFExtractor()
    web_extractor = WebPageExtractor()
    url_fetcher = UrlFetcher()
    text_cleaner = TextCleaner()
    recursive_chunker = RecursiveChunker()
    openai_embeddings = OpenAIEmbeddings()

    chunk_service = DocumentChunkService(
        document_contents_repository=document_contents_repository,
        document_chunk_repository=document_chunk_repository,
        chunker=recursive_chunker,
    )

    embedding_service = EmbeddingService(
        document_chunk_repository=document_chunk_repository,
        embeddings=openai_embeddings,
    )

    return DocumentService(
        document_repository=document_repository,
        document_contents_repository=document_contents_repository,
        pdf_extractor=pdf_extractor,
        web_extractor=web_extractor,
        url_fetcher=url_fetcher,
        text_cleaner=text_cleaner,
        document_chunk_service=chunk_service,
        embedding_service=embedding_service,
    )
