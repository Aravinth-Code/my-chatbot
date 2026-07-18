from fastapi import FastAPI
from app.api.health import router as health_router

app = FastAPI()

@app.get("/")
def root():
    return {"message": "RAG API Running"}

app.include_router(health_router)