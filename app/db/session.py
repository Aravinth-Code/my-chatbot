from sqlalchemy.orm import sessionmaker
from collections.abc import Generator
from sqlalchemy.orm import Session
from app.db.connection import engine

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()