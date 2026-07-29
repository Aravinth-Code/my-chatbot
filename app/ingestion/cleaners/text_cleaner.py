import re

from app.models.document_contents import DocumentContent

class TextCleaner:
    
    def clean_document_content(self, docs: list[DocumentContent]) -> DocumentContent:
        for doc in docs:
            doc.clean_text = self.text_cleaner.clean(doc.raw_text)
        
        return docs
    
    def clean(self, text: str) -> str:
        text = self._normalize_line_endings(text)
        text = self._remove_control_characters(text)
        text = self._normalize_whitespace(text)
        text = self._remove_extra_blank_lines(text)

        return text.strip()

    def _normalize_line_endings(self, text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n")

    def _remove_control_characters(self, text: str) -> str:
        return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)

    def _normalize_whitespace(self, text: str) -> str:
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
        return "\n".join(lines)

    def _remove_extra_blank_lines(self, text: str) -> str:
        return re.sub(r"\n{3,}", "\n\n", text)