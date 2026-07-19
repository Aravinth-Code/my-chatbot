from sqlalchemy import create_engine, URL
from app.core.config import settings
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

database_url = URL.create(
    drivername="postgresql+psycopg",
    username=settings.db_user,
    password=settings.db_password,  # Can contain @, :, /, etc.
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
)

engine = create_engine(
    database_url,
    echo=False,
    pool_pre_ping=True
)

from sqlalchemy import text

def check_database_connection() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("DB Connection Works")
        return True

    except Exception as ex:
        logger.exception(f"DB Connection Failure: {ex}")
        return False