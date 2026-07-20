from sqlalchemy import BigInteger, Enum, String

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base_model import BaseModel
from app.models.enums.document_status import DocumentStatus


class Document(Base, BaseModel):
    __tablename__ = "documents"

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    file_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    checksum: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True
    )

    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus),
        nullable=False,
        default=DocumentStatus.UPLOADED
    )