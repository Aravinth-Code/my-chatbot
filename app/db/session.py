from sqlalchemy.orm import sessionmaker

from app.db.connection import engine


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)