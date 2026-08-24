from datetime import datetime
from uuid import UUID

from app.core.config import settings
from app.models.document_chunks import DocumentChunk
from app.pipeline.embeddings.openai_embeddings import OpenAIEmbeddings
from app.pipeline.reranking.cross_encoder_reranker import CrossEncoderReranker
from app.pipeline.reranking.mmr import MMRSelector
from app.repositories.document_chunk_repository import DocumentChunkRepository


class RetrievalService:

    def __init__(
        self,
        document_chunk_repository: DocumentChunkRepository,
        embeddings: OpenAIEmbeddings,
        reranker: CrossEncoderReranker,
        mmr_selector: MMRSelector,
    ):
        self.document_chunk_repository = document_chunk_repository
        self.embeddings = embeddings
        self.reranker = reranker
        self.mmr_selector = mmr_selector

    def retrieve_candidates(
        self,
        query: str,
        top_k: int,
        document_id: UUID | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> list[tuple[DocumentChunk, float]]:
        fetch_k = max(top_k, settings.retrieval_candidate_pool_size)
        query_embedding = self.embeddings.embed_texts([query])[0]

        vector_results = self.document_chunk_repository.search_by_embedding(
            query_embedding, fetch_k, document_id, created_after, created_before,
        )
        keyword_results = self.document_chunk_repository.search_by_keywords(
            query, fetch_k, document_id, created_after, created_before,
        )

        fused = self._fuse_rrf(vector_results, keyword_results, fetch_k)
        reranked = self._rerank(query, fused)
        return self.mmr_selector.select(query_embedding, reranked, top_k)

    def _fuse_rrf(
        self,
        vector_results: list[DocumentChunk],
        keyword_results: list[DocumentChunk],
        top_k: int,
    ) -> list[tuple[DocumentChunk, float]]:
        k = settings.rrf_k
        scores: dict[UUID, float] = {}
        chunks_by_id: dict[UUID, DocumentChunk] = {}

        for rank, chunk in enumerate(vector_results, start=1):
            scores[chunk.id] = scores.get(chunk.id, 0.0) + 1.0 / (k + rank)
            chunks_by_id[chunk.id] = chunk

        for rank, chunk in enumerate(keyword_results, start=1):
            scores[chunk.id] = scores.get(chunk.id, 0.0) + 1.0 / (k + rank)
            chunks_by_id.setdefault(chunk.id, chunk)

        ranked_ids = sorted(scores, key=lambda cid: scores[cid], reverse=True)[:top_k]
        return [(chunks_by_id[cid], scores[cid]) for cid in ranked_ids]

    def _rerank(
        self,
        query: str,
        candidates: list[tuple[DocumentChunk, float]],
    ) -> list[tuple[DocumentChunk, float]]:
        chunks = [chunk for chunk, _ in candidates]
        scores = self.reranker.score(query, [chunk.text for chunk in chunks])
        return sorted(zip(chunks, scores), key=lambda pair: pair[1], reverse=True)
