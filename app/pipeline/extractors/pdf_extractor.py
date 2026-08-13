from uuid import UUID

import fitz

from app.models.document_contents import DocumentContent
from app.pipeline.extractors.extractor import Extractor


class PDFExtractor(Extractor):

    def extract(self, document_id: UUID, content: bytes) -> list[DocumentContent]:
        contents: list[DocumentContent] = []
        with fitz.open(stream=content, filetype="pdf") as pdf:
            for page_number, page in enumerate(pdf, start=1):
                document_content = self._extract_page(
                    document_id=document_id,
                    page=page,
                    page_number=page_number,
                )

                contents.append(document_content)
        return contents

    def _extract_page(self, document_id: UUID, page: fitz.Page, page_number: int) -> DocumentContent:
        raw_text = page.get_text()
        return DocumentContent(
            document_id=document_id,
            content_order=page_number,
            raw_text=raw_text,
            content_metadata={
                "page_number": page_number,
            },
        )
