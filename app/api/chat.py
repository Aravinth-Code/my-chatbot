import logging

from fastapi import APIRouter, Depends

from app.dependencies.chat import get_chat_service
from app.schemas.chat import ChatRequest, ChatResponse, ChatSource
from app.services.chat_service import ChatService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    answer, results = chat_service.answer(
        request.query,
        request.top_k,
        request.document_id,
        request.created_after,
        request.created_before,
    )
    return ChatResponse(
        answer=answer,
        sources=[
            ChatSource(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                start_page=chunk.start_page,
                end_page=chunk.end_page,
                score=score,
            )
            for chunk, score in results
        ],
    )
