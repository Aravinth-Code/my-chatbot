from datetime import datetime
from uuid import UUID

from app.models.document_chunks import DocumentChunk
from app.pipeline.llm.openai_chat import OpenAIChat
from app.pipeline.prompting.prompt_builder import PromptBuilder
from app.services.retrieval_service import RetrievalService


class ChatService:

    def __init__(
        self,
        retrieval_service: RetrievalService,
        prompt_builder: PromptBuilder,
        llm: OpenAIChat,
    ):
        self.retrieval_service = retrieval_service
        self.prompt_builder = prompt_builder
        self.llm = llm

    def answer(
        self,
        query: str,
        top_k: int,
        document_id: UUID | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> tuple[str, list[tuple[DocumentChunk, float]]]:
        results = self.retrieval_service.retrieve_candidates(
            query, top_k, document_id, created_after, created_before,
        )
        chunks = [chunk for chunk, _ in results]

        messages = self.prompt_builder.build(query, chunks)
        answer = self.llm.complete(messages)

        return answer, results
