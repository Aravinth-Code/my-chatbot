from uuid import UUID

from app.models.document_contents import DocumentContent
from app.pipeline.extractors.extractor import Extractor


class TextExtractor(Extractor):

    def extract(self, document_id: UUID, content: bytes) -> list[DocumentContent]:
        text = content.decode("utf-8")
        return [
            DocumentContent(
                document_id=document_id,
                content_order=1,
                raw_text=text,
                content_metadata={},
            )
        ]
