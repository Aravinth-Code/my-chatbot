from sqlalchemy import BigInteger, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.base_model import BaseModel
from app.models.document_chunks import DocumentChunk
from app.models.document_contents import DocumentContent
from app.models.document_history import DocumentHistory
from app.models.enums.document_source_type import DocumentSourceType
from app.models.enums.document_status import DocumentStatus


class Document(Base, BaseModel):
    __tablename__ = "documents"

    original_file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    stored_file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    
    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )
    
    checksum: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True
    )

    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    status: Mapped[DocumentStatus] = mapped_column(
        SQLEnum(
            DocumentStatus,
            name="document_status",
        ),
        nullable=False,
        default=DocumentStatus.UPLOADED,
    )
    
    error_message: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    source_type: Mapped[DocumentSourceType] = mapped_column(
        SQLEnum(
            DocumentSourceType,
            name="document_source_type",
        ),
        nullable=False,
        default=DocumentSourceType.FILE,
    )

    source_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    contents: Mapped[list["DocumentContent"]] = relationship(
        "DocumentContent",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )

    history: Mapped[list["DocumentHistory"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )