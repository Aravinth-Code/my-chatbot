from uuid import UUID

from sqlalchemy.orm import Session

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