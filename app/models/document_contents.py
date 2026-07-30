from typing import TYPE_CHECKING, Any
from uuid import UUID
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import JSONB

if TYPE_CHECKING:
    from app.models.document import Document

class DocumentContent(Base, BaseModel):
    __tablename__ = "document_contents"
    
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    content_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    raw_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    clean_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    content_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    document: Mapped["Document"] = relationship(
        back_populates="contents",
    )
    