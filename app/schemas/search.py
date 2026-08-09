from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=10, ge=1, le=50)


class SearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    chunk_id: UUID = Field(validation_alias="id")
    document_id: UUID
    text: str
    start_page: int
    end_page: int
