from datetime import datetime
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Query, Session

from app.models.document_chunks import DocumentChunk
from app.models.enums.chunk_status import ChunkStatus


class DocumentChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_chunks(self, chunks: list[DocumentChunk]) -> list[DocumentChunk] :
        self.db.add_all(chunks)
        self.db.commit()
        for chunk in chunks:
            self.db.refresh(chunk)
        return(chunks)

    def _apply_common_filters(
        self,
        query: Query[DocumentChunk],
        document_id: UUID | None,
        created_after: datetime | None,
        created_before: datetime | None,
    ) -> Query[DocumentChunk]:
        if document_id is not None:
            query = query.filter(DocumentChunk.document_id == document_id)
        if created_after is not None:
            query = query.filter(DocumentChunk.created_at >= created_after)
        if created_before is not None:
            query = query.filter(DocumentChunk.created_at <= created_before)
        return query

    def search_by_embedding(
        self,
        query_embedding: list[float],
        top_k: int,
        document_id: UUID | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> list[DocumentChunk]:
        query = self.db.query(DocumentChunk).filter(DocumentChunk.status == ChunkStatus.EMBEDDED)
        query = self._apply_common_filters(query, document_id, created_after, created_before)
        return (
            query.order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
            .all()
        )

    def search_by_keywords(
        self,
        query_text: str,
        top_k: int,
        document_id: UUID | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> list[DocumentChunk]:
        tsquery = func.websearch_to_tsquery("english", query_text)
        query = (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.status == ChunkStatus.EMBEDDED)
            .filter(DocumentChunk.search_vector.op("@@")(tsquery))
        )
        query = self._apply_common_filters(query, document_id, created_after, created_before)
        return (
            query.order_by(func.ts_rank(DocumentChunk.search_vector, tsquery).desc())
            .limit(top_k)
            .all()
        )

    def save_embeddings(self, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        self.db.add_all(chunks)
        self.db.commit()
        for chunk in chunks:
            self.db.refresh(chunk)
        return chunks

    def get_document_chunks(self, document_id: UUID) -> list[DocumentChunk] :
        return (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
            .all()
        )
        
    def delete_by_document_id(self, document_id: UUID) -> None:
        (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .delete()
        )
        self.db.commit()

    def update_status(
        self,
        document_id: UUID,
        status: ChunkStatus,
    ) -> None:
        (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .update({"status": status})
        )
        self.db.commit()