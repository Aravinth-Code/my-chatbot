import logging

from fastapi import APIRouter, Depends

from app.dependencies.retrieval import get_retrieval_service
from app.schemas.search import SearchRequest, SearchResult
from app.services.retrieval_service import RetrievalService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/search", response_model=list[SearchResult])
def search(
    request: SearchRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
) -> list[SearchResult]:
    chunks = retrieval_service.retrieve_candidates(request.query, request.top_k)
    return [SearchResult.model_validate(chunk) for chunk in chunks]
