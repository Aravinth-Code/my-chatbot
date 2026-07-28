from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from app.models.document_contents import DocumentContent


class DocumentContentsRepository:
    
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, document_content: DocumentContent) -> DocumentContent:
        self.db.add(document_content)
        self.db.commit()
        self.db.refresh(document_content)
        return document_content
    
    def create_many(self, document_contents: list[DocumentContent]) -> list[DocumentContent]:
        self.db.add_all(document_contents)
        self.db.commit()
        return document_contents
    
    def get_documents_by_id(self, document_id: UUID) -> list[DocumentContent]:
        statement = (select(DocumentContent)
                     .where(DocumentContent.document_id == document_id)
                     .order_by(DocumentContent.content_order)
                     )
        return list(self.db.scalars(statement).all())
    
    def delete_by_document_id(self,document_id: UUID) -> None:
        statement = (delete(DocumentContent)
                     .where(DocumentContent.document_id == document_id)
                     )
        self.db.execute(statement)
        self.db.commit()
        
    def count_by_document_id(self,document_id: UUID) -> int:
        statement = (select(DocumentContent)
                     .where(DocumentContent.document_id == document_id)
                     )
        return len(list(self.db.scalars(statement)))
        
    def exists(self, document_id: UUID) -> bool:
        statement = (select(DocumentContent)
                    .where(DocumentContent.document_id == document_id)
                    .limit(1)
                    )
        return self.db.scalar(statement) is not None