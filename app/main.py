from fastapi import FastAPI
from app.core.logging import setup_logging
from app.api.health import router as health_router
from app.api.document import router as document_router
from app.api.retrieval import router as retrieval_router

setup_logging()

app = FastAPI()

@app.get("/")
def root():
    return {"message": "RAG API Running"}

app.include_router(health_router)
app.include_router(document_router)
app.include_router(retrieval_router)