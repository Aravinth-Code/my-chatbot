from functools import lru_cache

from fastapi import Depends

from app.dependencies.retrieval import get_retrieval_service
from app.pipeline.llm.openai_chat import OpenAIChat
from app.pipeline.prompting.prompt_builder import PromptBuilder
from app.services.chat_service import ChatService
from app.services.retrieval_service import RetrievalService


@lru_cache
def _get_prompt_builder() -> PromptBuilder:
    return PromptBuilder()


@lru_cache
def _get_llm() -> OpenAIChat:
    return OpenAIChat()


def get_chat_service(
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
) -> ChatService:
    return ChatService(
        retrieval_service=retrieval_service,
        prompt_builder=_get_prompt_builder(),
        llm=_get_llm(),
    )
