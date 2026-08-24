from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.pipeline.embeddings.openai_embeddings import OpenAIEmbeddings
from app.pipeline.reranking.cross_encoder_reranker import CrossEncoderReranker
from app.pipeline.reranking.mmr import MMRSelector
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.services.retrieval_service import RetrievalService


@lru_cache
def _get_reranker() -> CrossEncoderReranker:
    return CrossEncoderReranker()


def get_retrieval_service(
    db: Session = Depends(get_db),
) -> RetrievalService:
    document_chunk_repository = DocumentChunkRepository(db)
    openai_embeddings = OpenAIEmbeddings()
    reranker = _get_reranker()
    mmr_selector = MMRSelector()

    return RetrievalService(
        document_chunk_repository=document_chunk_repository,
        embeddings=openai_embeddings,
        reranker=reranker,
        mmr_selector=mmr_selector,
    )
