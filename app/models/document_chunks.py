from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.base_model import BaseModel
from app.models.enums.chunk_status import ChunkStatus
from sqlalchemy import Enum as SQLEnum

if TYPE_CHECKING:
    from app.models.document import Document
    
class DocumentChunk(Base, BaseModel):
    __tablename__ = "document_chunks"

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    start_page: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    end_page: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    character_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    token_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(1536),
        nullable=True,
    )

    status: Mapped[ChunkStatus] = mapped_column(
        SQLEnum(
            ChunkStatus,
            name="chunk_status",
        ),
        default=ChunkStatus.CHUNKED,
        nullable=False,
    )

    document: Mapped["Document"] = relationship(
        back_populates="chunks",
    )