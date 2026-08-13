# Roadmap

Build plan for the enterprise RAG backend. Status reflects the actual state of the code, checked against each phase — not just intent.

Guiding philosophy (keep following this): **don't build phases ahead of need.** Learn and implement just enough to complete the feature in front of you. While building uploads, don't discuss embeddings. While building embeddings, don't discuss Terraform. This is deliberate, to avoid overload — see the "Intentional design decisions" section in `CLAUDE.md` for a concrete example (empty interface files left empty until a second implementation actually needs them).

## Status

| Phase | Topic | Status |
|---|---|---|
| 1 | Backend Foundation (FastAPI, config, logging, Postgres, pgvector, SQLAlchemy, Alembic, Docker, repository/service pattern) | ✅ Done |
| 2 | Document Upload (multipart upload, MIME/size validation, SHA256 dedup, UUID storage) | ✅ Done |
| 3 | Document Processing / text extraction | 🟡 PDF (PyMuPDF) and webpage/HTML (BeautifulSoup, via `POST /document/ingest-url`) done. `Extractor` is now a real interface — see decisions log. DOCX/TXT/Markdown/CSV/Excel/OCR not started |
| 4 | Cleaning Pipeline | 🟡 Basic whitespace/control-char/line-ending cleanup done (source-agnostic, reused for both PDF and web). HTML-specific noise removal (nav/header/footer/cookie-banner) done, but lives in `WebPageExtractor` rather than the generic cleaner — see `CLAUDE.md` |
| 5 | Metadata Pipeline | 🟡 Minimal — `content_metadata` JSONB holds `page_number` (PDF) or `title` (web). `Document.source_type`/`source_url` added. Author/department/tags/version not modeled yet |
| 6 | Document Classification | ⬜ Not started |
| 7 | Chunking Engine | 🟡 One strategy done (`RecursiveChunker`), reused as-is for web content. Header-aware/HTML-aware/sentence/semantic/parent-child/adaptive not started. Chunker interface intentionally left undefined until a second chunker is built |
| 8 | Embeddings | 🟡 OpenAI (`text-embedding-3-small`) done — batched generation, stored in pgvector, versioned via `embedding_model` column. Other providers (Gemini, BGE, E5, Nomic, Sentence Transformers, Ollama) not started |
| 9 | Vector Storage | ✅ Done — `pgvector` column, `vector` extension migration, HNSW index (cosine ops) on `document_chunks.embedding` |
| 10 | Candidate Retrieval (vector search, BM25, hybrid, metadata/version/time filtering) | 🟡 Plain vector search done — `POST /search` embeds the query and returns the top-k nearest chunks by cosine distance. BM25, hybrid fusion, and metadata/version/time filtering not started |
| 11 | Query Intelligence (rewrite, multi-query, spell correction, intent/language detection) | ⬜ Not started |
| 12 | Ranking Pipeline (RRF, cross-encoder, MMR, context compression) | ⬜ Not started |
| 13 | Prompt Builder | ⬜ Not started |
| 14 | LLM Layer (OpenAI/Claude/Gemini/Azure/Ollama, streaming, fallback, retry, cost/token tracking) | ⬜ Not started |
| 15 | Citations & Memory | ⬜ Not started |
| 16 | AI Workflows / Agentic RAG (LangChain, LangGraph, tool calling, MCP) | ⬜ Not started — deliberately deferred until retrieval (10–12) and the LLM layer (14) work end-to-end, since agents need real tools to orchestrate |
| 17 | SaaS Features (auth, RBAC, multi-tenant, API keys, billing) | ⬜ Not started |
| 18 | DevOps & Cloud (Docker Compose, CI/CD, Terraform, AWS) | ⬜ Not started |
| 19 | Observability (structured logging, tracing, Prometheus/Grafana, Sentry) | ⬜ Not started |
| 20 | Scaling & Enterprise Connectors (Redis, workers, rate limiting, Notion/Slack/GitHub/Drive/etc. — MCP is a natural fit here) | ⬜ Not started |
| 21 | Evaluation (retrieval precision/recall/MRR/nDCG, faithfulness, hallucination rate, latency, cost) | ⬜ Not started |

## Immediate next candidates (in rough order)

1. BM25 / hybrid search and metadata filtering to round out Phase 10
2. A third document source (e.g. plain text/Markdown, or a real connector) — would be the trigger to reconsider `Cleaner`/`Chunker` interfaces if it needs source-specific handling
3. Query Intelligence (Phase 11) and Ranking Pipeline (Phase 12) once there's real retrieval traffic to tune against

## Decisions log

- **Embedding model is `text-embedding-3-small` (1536 dims), fixed.** Multi-model support later needs either separate vector columns/tables per dimension or a projection step — noted for when Phase 8's provider list expands.
- **`embedding_model` column added to `document_chunks`** ahead of needing multiple providers, specifically so vectors stay traceable to the model that produced them (cheap to add now, expensive to backfill later).
- **`CREATE EXTENSION vector` was missing from migrations** even though the `embedding` column already worked (it had been enabled manually on the dev database at some point). Added to the HNSW index migration so a fresh database built from migrations alone won't fail.
- **`POST /search` returns raw candidate chunks, no ranking/reranking yet.** This is intentionally the "candidate retrieval" stage only (Phase 10) — narrowing to the best few chunks is Phase 12's job (RRF, cross-encoder, MMR), not built yet.
- **`Extractor` is now a real ABC** (`app/pipeline/extractors/extractor.py`) now that webpage ingestion gave it a genuine second implementation (`PDFExtractor`, `WebPageExtractor`). Both now take raw `bytes` rather than a file path — `Cleaner`/`Chunker` stay concrete/undefined, still one implementation each.
- **Fixed a pre-existing bug** in `DocumentChunkService.chunk_document` (`page.cleaned_text`/`page.page_number` — neither attribute exists on `DocumentContent`, which has `clean_text`/`content_order`). This had never been exercised against a live DB, so it was silently broken since it was written; found while building web ingestion.
- **`UrlFetcher` (`app/pipeline/loaders/url_fetcher.py`) added with SSRF guards** for `ingest_url`: scheme allowlist, private/loopback/link-local/reserved IP rejection via DNS resolution, no redirect-following, streamed response with a size cap. Known residual gap: DNS-rebinding between the guard check and the actual connection — acceptable for now, flagged for before this handles untrusted multi-tenant traffic.
- **Webpage dedup is checksum-based, same as PDFs** — re-ingesting an unchanged URL conflicts (409). Detecting that a page's content *changed* since last crawl (versioning/re-crawl) is not built — out of scope for this pass.
