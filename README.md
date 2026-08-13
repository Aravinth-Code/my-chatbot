# my-chatbot

FastAPI backend for an enterprise-grade RAG (Retrieval-Augmented Generation) system — the ingestion and retrieval side of an AI customer support chatbot product that will eventually answer questions from a user's own documents (PDF, websites, text, etc.).

This repo is the Python RAG piece of a larger product; a separate .NET service handles UI + general API backend concerns.

See [ROADMAP.md](ROADMAP.md) for the full 21-phase build plan and current phase status, and [CLAUDE.md](CLAUDE.md) for architecture notes and intentional design decisions.

## Architecture

Strict layering, each layer only talks to the one directly below it:

```
app/api (FastAPI routers) → app/services (business logic) → app/repositories (SQLAlchemy queries) → app/models (ORM) → Postgres + pgvector
```

Dependency injection is manual: each router depends on a factory function in `app/dependencies/*.py` that constructs a service and wires up its repository/pipeline collaborators; FastAPI's `Depends` injects it per-request.

### Document ingestion pipeline

Documents move through `DocumentStatus`:

```
UPLOADED → PROCESSING → EXTRACTING → EXTRACTED → CHUNKING → EMBEDDING → PROCESSED
```

1. **Upload / fetch** — `POST /document/upload` (multipart file) or `POST /document/ingesturl` (fetches a URL via an SSRF-guarded `UrlFetcher`). Both dedupe by SHA256 checksum and store the source under `storage/uploads/`.
2. **Extract** (`app/pipeline/extractors/`) — `PDFExtractor` (PyMuPDF) or `WebPageExtractor` (BeautifulSoup) turn raw bytes into `DocumentContent` rows (one per PDF page, one per web page).
3. **Clean** (`app/pipeline/cleaners/`) — `TextCleaner` normalizes whitespace/line-endings/control characters.
4. **Chunk** (`app/pipeline/chunkers/`) — `RecursiveChunker` splits cleaned text into `DocumentChunk` rows.
5. **Embed** (`app/pipeline/embeddings/`) — `OpenAIEmbeddings` (`text-embedding-3-small`, 1536 dims) batches chunk text to OpenAI and writes vectors into pgvector.

### Retrieval

`POST /search` embeds the query with the same embedding model used at ingestion and runs a pgvector cosine-distance search (HNSW index) over embedded chunks. This is candidate retrieval only — no BM25/hybrid/reranking yet.

## Setup

- Python 3.12
- `python -m venv .venv`
- `.venv/Scripts/activate` (Windows) or `source .venv/bin/activate` (macOS/Linux)
- `pip install -r requirements.txt`
- Copy `.env.example` to `.env` and fill in `DB_PASSWORD` and `OPENAI_API_KEY`

## Running

```bash
docker compose up -d          # starts Postgres with pgvector
alembic upgrade head          # apply migrations
uvicorn app.main:app --reload # run the API
```

The API is served at `http://localhost:8000`. A "Debug FastAPI" launch config is also available in `.vscode/launch.json`.

When you change a model in `app/models/`, generate a migration with:

```bash
alembic revision --autogenerate -m "message"
```

## API

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health/root check |
| `/document/upload` | POST | Upload a file (multipart) for ingestion |
| `/document/ingesturl` | POST | Fetch and ingest a web page by URL |
| `/search` | POST | Embed a query and return top-k nearest chunks |

## Testing

There is no test suite yet (`tests/` exists but is currently empty).
