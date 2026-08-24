from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=10, ge=1, le=50)
    document_id: UUID | None = None
    created_after: AwareDatetime | None = None
    created_before: AwareDatetime | None = None


class ChatSource(BaseModel):
    chunk_id: UUID
    document_id: UUID
    start_page: int
    end_page: int
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]
