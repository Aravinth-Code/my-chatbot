# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

FastAPI backend for an enterprise-grade RAG (Retrieval-Augmented Generation) system — the ingestion side of an AI customer support chatbot product that will eventually answer questions from a user's own documents (PDF, websites, text, etc.). See `ROADMAP.md` for the full build plan and current phase status.

## Commands

Setup:
- Python 3.12, virtualenv at `.venv/`, dependencies in `requirements.txt`
- `.venv/Scripts/activate` then `pip install -r requirements.txt`
- Copy `.env.example` to `.env` and fill in `DB_PASSWORD` and `OPENAI_API_KEY`

Run:
- `docker compose up -d` — starts Postgres with pgvector (`pgvector/pgvector:pg17`)
- `alembic upgrade head` — apply migrations
- `uvicorn app.main:app --reload` — run the API (also available as the "Debug FastAPI" launch config in `.vscode/launch.json`)
- `alembic revision --autogenerate -m "message"` — generate a new migration after changing a model in `app/models/`

There is no test suite yet (`tests/` exists but is currently empty).

## Architecture

Strict layering, each layer only talks to the one directly below it:

`app/api` (FastAPI routers) → `app/services` (business logic/orchestration) → `app/repositories` (SQLAlchemy queries) → `app/models` (ORM) → Postgres + pgvector

Dependency injection is manual, not a container: each router depends on a factory function in `app/dependencies/*.py` that constructs a service and wires up all of its repository/pipeline collaborators; FastAPI's `Depends` then injects it per-request. Follow the pattern in `app/dependencies/document.py` when wiring a new service.

### Document ingestion pipeline

`DocumentService.upload_document` (`app/services/document_service.py`) orchestrates the whole pipeline synchronously within one request, advancing `Document.status` (the `DocumentStatus` enum) at each stage and flipping to `FAILED` on any exception in that stage:

```
UPLOADED → PROCESSING → EXTRACTING → EXTRACTED → CHUNKING → EMBEDDING → PROCESSED
```

1. **Upload** — validates MIME type/size, SHA256-dedupes against existing documents (`documents.checksum` is unique), stores the file under `storage/uploads/<uuid>.<ext>`.
2. **Extract** (`app/pipeline/extractors/`) — `PDFExtractor` (PyMuPDF) pulls text per page into `DocumentContent` rows, one per page.
3. **Clean** (`app/pipeline/cleaners/`) — `TextCleaner` normalizes line endings/control characters/whitespace into `DocumentContent.clean_text`.
4. **Chunk** (`app/pipeline/chunkers/`, orchestrated by `DocumentChunkService`) — `RecursiveChunker` (LangChain's `RecursiveCharacterTextSplitter`) splits each page's clean text into `DocumentChunk` rows.
5. **Embed** (`app/pipeline/embeddings/`, orchestrated by `EmbeddingService`) — `OpenAIEmbeddings` batches chunk text to OpenAI and writes vectors back to `DocumentChunk.embedding` (pgvector, fixed at 1536 dims — tied to `text-embedding-3-small`), tagging `DocumentChunk.embedding_model` so every chunk stays traceable to the model that produced its vector.

### Data model

`Document` (1) → `DocumentContent` (many, one per page) and `Document` (1) → `DocumentChunk` (many, chunked from `DocumentContent`); both children cascade-delete with their parent. All models share `BaseModel` (`app/models/base_model.py`) for `id`/`created_at`/`updated_at`. Pipeline progress is tracked on two separate enums: `DocumentStatus` (document-level) and `ChunkStatus` (chunk-level).

### Intentional design decisions — don't "helpfully" undo these

- `app/pipeline/{chunkers,cleaners,extractors}/{chunker,cleaner,extractor}.py` are **empty interface files, left empty on purpose** (explicit YAGNI call). Each pipeline stage currently has exactly one concrete implementation, and the services that use them are typed against the concrete class, not an abstraction. Only define the real abstract base and retrofit the Strategy pattern once a *second* concrete implementation of that stage is actually being added (e.g. a second chunker) — don't add the abstraction speculatively ahead of that.
- Config is a single `Settings` singleton (`app/core/config.py`, pydantic-settings) loaded from `.env`. Add new config values there rather than reading `os.environ` directly.
