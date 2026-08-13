from uuid import UUID

from app.models.document_chunks import DocumentChunk
from app.pipeline.chunkers.recursive_chunker import RecursiveChunker
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_contents_repository import DocumentContentsRepository

class DocumentChunkService:
    def __init__(self, 
                 document_contents_repository: DocumentContentsRepository,
                 document_chunk_repository: DocumentChunkRepository,
                 chunker: RecursiveChunker):
        
        self.document_chunk_repository = document_chunk_repository
        self.document_contents_repository = document_contents_repository
        self.chunker = chunker
        
    def chunk_document(self, document_id: UUID) -> None:
        pages = self.document_contents_repository.get_documents_by_id(document_id)
        
        chunks = []
        chunk_index = 0
        for page in pages:
            page_chunks = self.chunker.split(page.clean_text)
            for chunk_text in page_chunks:

                chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=chunk_index,
                    text=chunk_text,
                    start_page=page.content_order,
                    end_page=page.content_order,
                    character_count=len(chunk_text),
                )

                chunks.append(chunk)

                chunk_index += 1

        self.document_chunk_repository.create_chunks(chunks)