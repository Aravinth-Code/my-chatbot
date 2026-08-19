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
    results = retrieval_service.retrieve_candidates(
        request.query,
        request.top_k,
        request.document_id,
        request.created_after,
        request.created_before,
    )
    return [
        SearchResult(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            text=chunk.text,
            start_page=chunk.start_page,
            end_page=chunk.end_page,
            score=score,
        )
        for chunk, score in results
    ]
