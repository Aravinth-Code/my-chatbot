import logging
from fastapi import APIRouter
from app.core.config import settings
from app.db.connection import check_database_connection

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
def health():
    logger.info("Health check endpoint called")
    return {
        "status": "UP",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }
    
@router.get("/health/db")
def database_health():
    logger.info("Database Health check endpoint called")
    if check_database_connection():
        return {
            "status": "UP"
        }
    return {
        "status": "DOWN"
    }