from app.models.document_chunks import DocumentChunk
from app.pipeline.embeddings.openai_embeddings import OpenAIEmbeddings
from app.repositories.document_chunk_repository import DocumentChunkRepository


class RetrievalService:

    def __init__(
        self,
        document_chunk_repository: DocumentChunkRepository,
        embeddings: OpenAIEmbeddings,
    ):
        self.document_chunk_repository = document_chunk_repository
        self.embeddings = embeddings

    def retrieve_candidates(self, query: str, top_k: int) -> list[DocumentChunk]:
        query_embedding = self.embeddings.embed_texts([query])[0]
        return self.document_chunk_repository.search_by_embedding(query_embedding, top_k)
