from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.pipeline.embeddings.openai_embeddings import OpenAIEmbeddings
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.services.retrieval_service import RetrievalService


def get_retrieval_service(
    db: Session = Depends(get_db),
) -> RetrievalService:
    document_chunk_repository = DocumentChunkRepository(db)
    openai_embeddings = OpenAIEmbeddings()

    return RetrievalService(
        document_chunk_repository=document_chunk_repository,
        embeddings=openai_embeddings,
    )
