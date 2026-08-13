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

`DocumentService` (`app/services/document_service.py`) has two entry points that both feed the same private `_process_document(document, content, extractor)` pipeline, advancing `Document.status` (the `DocumentStatus` enum) at each stage and flipping to `FAILED` on any exception in that stage:

```
UPLOADED → PROCESSING → EXTRACTING → EXTRACTED → CHUNKING → EMBEDDING → PROCESSED
```

- **`upload_document(file)`** — validates MIME type/size, SHA256-dedupes against existing documents (`documents.checksum` is unique), stores the file under `storage/uploads/<uuid>.<ext>`, `source_type=FILE`.
- **`ingest_url(url)`** — fetches the page via `UrlFetcher` (`app/pipeline/loaders/url_fetcher.py`, SSRF-guarded — see below), same dedup/storage mechanism, `source_type=URL`, `source_url` set, `original_file_name` holds the URL.

Both then run the same shared steps:

1. **Extract** (`app/pipeline/extractors/`) — `Extractor` is a real ABC (`extract(document_id, content: bytes) -> list[DocumentContent]`); `PDFExtractor` (PyMuPDF) and `WebPageExtractor` (BeautifulSoup, strips nav/header/footer/script/cookie-banner elements before extracting text) both implement it. Web pages produce a single `DocumentContent` row (`content_order=1`); PDFs produce one per page.
2. **Clean** (`app/pipeline/cleaners/`) — `TextCleaner` normalizes line endings/control characters/whitespace into `DocumentContent.clean_text`. Source-agnostic, reused as-is for both extractors.
3. **Chunk** (`app/pipeline/chunkers/`, orchestrated by `DocumentChunkService`) — `RecursiveChunker` (LangChain's `RecursiveCharacterTextSplitter`) splits each `DocumentContent.clean_text` into `DocumentChunk` rows. `start_page`/`end_page` are the source `content_order` (always `1` for web pages — there's no real pagination concept there, the column names are just PDF-era naming that wasn't worth a migration to rename).
4. **Embed** (`app/pipeline/embeddings/`, orchestrated by `EmbeddingService`) — `OpenAIEmbeddings` batches chunk text to OpenAI and writes vectors back to `DocumentChunk.embedding` (pgvector, fixed at 1536 dims — tied to `text-embedding-3-small`), tagging `DocumentChunk.embedding_model` so every chunk stays traceable to the model that produced its vector.

### Retrieval

`POST /search` (`app/api/retrieval.py` → `RetrievalService.retrieve_candidates`) embeds the query with the same `OpenAIEmbeddings` used at ingestion time, then does a plain pgvector cosine-distance search (`document_chunks` has an HNSW index, `vector_cosine_ops`) filtered to `ChunkStatus.EMBEDDED`. This is Phase 10 "candidate retrieval" only — no BM25/hybrid/reranking yet, see `ROADMAP.md`.

### Data model

`Document` (1) → `DocumentContent` (many, one per page/section) and `Document` (1) → `DocumentChunk` (many, chunked from `DocumentContent`); both children cascade-delete with their parent. All models share `BaseModel` (`app/models/base_model.py`) for `id`/`created_at`/`updated_at`. Pipeline progress is tracked on two separate enums: `DocumentStatus` (document-level) and `ChunkStatus` (chunk-level). `DocumentSourceType` (`FILE`/`URL`) on `Document` records where a document came from.

### Intentional design decisions — don't "helpfully" undo these

- `app/pipeline/{chunkers,cleaners}/{chunker,cleaner}.py` are **empty interface files, left empty on purpose** (explicit YAGNI call). Each of these stages currently has exactly one concrete implementation, and the services that use them are typed against the concrete class, not an abstraction. `Extractor` (`app/pipeline/extractors/extractor.py`) *was* one of these until webpage ingestion added a genuine second implementation — that's the trigger point for defining a real interface: wait for it, don't add it speculatively ahead of it.
- `UrlFetcher` (`app/pipeline/loaders/url_fetcher.py`) has SSRF guards (scheme allowlist, private/loopback/link-local IP rejection, no redirect-following, streamed size cap) since it fetches arbitrary user-supplied URLs server-side. Known residual gap documented in its docstring: DNS is resolved once for the guard check and again by `httpx` when connecting, so a DNS-rebinding attack could theoretically slip through between the two — acceptable for now, revisit before handling untrusted multi-tenant traffic at scale.
- Config is a single `Settings` singleton (`app/core/config.py`, pydantic-settings) loaded from `.env`. Add new config values there rather than reading `os.environ` directly.
