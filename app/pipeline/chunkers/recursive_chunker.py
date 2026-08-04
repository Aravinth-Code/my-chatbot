from langchain_text_splitters import RecursiveCharacterTextSplitter


class RecursiveChunker:
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                " ",
                "",
            ],
            keep_separator=True,
            is_separator_regex=False,
        )

    def split(self, text: str) -> list[str]:
        if not text:
            return []

        return self.text_splitter.split_text(text)