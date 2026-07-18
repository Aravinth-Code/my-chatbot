from fastapi import APIRouter
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("/health")
def health():
    logger.info("Health check endpoint called")
    
    return {
        "status": "UP"
    }