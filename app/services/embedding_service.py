from uuid import UUID

from app.models.enums.chunk_status import ChunkStatus
from app.pipeline.embeddings.openai_embeddings import OpenAIEmbeddings
from app.repositories.document_chunk_repository import DocumentChunkRepository


class EmbeddingService:

    def __init__(
        self,
        document_chunk_repository: DocumentChunkRepository,
        embeddings: OpenAIEmbeddings,
    ):
        self.document_chunk_repository = document_chunk_repository
        self.embeddings = embeddings

    def embed_document(self, document_id: UUID) -> None:
        chunks = self.document_chunk_repository.get_document_chunks(document_id)
        if not chunks:
            return

        texts = [chunk.text for chunk in chunks]
        vectors = self.embeddings.embed_texts(texts)

        for chunk, vector in zip(chunks, vectors):
            chunk.embedding = vector
            chunk.embedding_model = self.embeddings.model
            chunk.status = ChunkStatus.EMBEDDED

        self.document_chunk_repository.save_embeddings(chunks)
