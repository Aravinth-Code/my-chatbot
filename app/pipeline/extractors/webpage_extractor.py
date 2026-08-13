import re
from uuid import UUID

from bs4 import BeautifulSoup

from app.models.document_contents import DocumentContent
from app.pipeline.extractors.extractor import Extractor

NOISE_TAGS = ["script", "style", "nav", "header", "footer", "noscript", "aside", "form"]
NOISE_CLASS_PATTERN = re.compile(r"cookie|consent|banner|advert", re.IGNORECASE)


class WebPageExtractor(Extractor):

    def extract(self, document_id: UUID, content: bytes) -> list[DocumentContent]:
        soup = BeautifulSoup(content, "lxml")

        self._remove_noise(soup)

        text = soup.get_text(separator="\n")
        title = soup.title.string.strip() if soup.title and soup.title.string else None

        return [
            DocumentContent(
                document_id=document_id,
                content_order=1,
                raw_text=text,
                content_metadata={"title": title} if title else {},
            )
        ]

    def _remove_noise(self, soup: BeautifulSoup) -> None:
        for tag in soup(NOISE_TAGS):
            tag.decompose()

        for element in soup.find_all(class_=NOISE_CLASS_PATTERN):
            element.decompose()

        for element in soup.find_all(id=NOISE_CLASS_PATTERN):
            element.decompose()
