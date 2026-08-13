from abc import ABC, abstractmethod
from uuid import UUID

from app.models.document_contents import DocumentContent


class Extractor(ABC):

    @abstractmethod
    def extract(self, document_id: UUID, content: bytes) -> list[DocumentContent]:
        ...
