from app.models.document_chunks import DocumentChunk

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions using only the provided context. "
    "If the context does not contain enough information to answer, say so instead of guessing. "
    "Cite sources using their [n] reference number."
)


class PromptBuilder:

    def build(self, query: str, chunks: list[DocumentChunk]) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": self._format_user_message(query, chunks)},
        ]

    def _format_user_message(self, query: str, chunks: list[DocumentChunk]) -> str:
        return f"Context:\n{self._format_context(chunks)}\n\nQuestion: {query}"

    def _format_context(self, chunks: list[DocumentChunk]) -> str:
        if not chunks:
            return "(no relevant context found)"
        return "\n\n".join(
            f"[{i}] (document {chunk.document_id}, page {chunk.start_page}) {chunk.text}"
            for i, chunk in enumerate(chunks, start=1)
        )
