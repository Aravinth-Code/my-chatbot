from sqlalchemy import create_engine, URL
from app.core.config import settings
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True
)

def check_database_connection() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("DB Connection Works")
        return True

    except Exception as ex:
        logger.exception(f"DB Connection Failure: {ex}")
        return False