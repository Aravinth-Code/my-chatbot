# Roadmap

Build plan for the enterprise RAG backend. Status reflects the actual state of the code, checked against each phase — not just intent.

Guiding philosophy (keep following this): **don't build phases ahead of need.** Learn and implement just enough to complete the feature in front of you. While building uploads, don't discuss embeddings. While building embeddings, don't discuss Terraform. This is deliberate, to avoid overload — see the "Intentional design decisions" section in `CLAUDE.md` for a concrete example (empty interface files left empty until a second implementation actually needs them).

## Status

| Phase | Topic | Status |
|---|---|---|
| 1 | Backend Foundation (FastAPI, config, logging, Postgres, pgvector, SQLAlchemy, Alembic, Docker, repository/service pattern) | ✅ Done |
| 2 | Document Upload (multipart upload, MIME/size validation, SHA256 dedup, UUID storage) | ✅ Done |
| 3 | Document Processing / text extraction | 🟡 PDF only (PyMuPDF). DOCX/TXT/Markdown/HTML/CSV/Excel/OCR not started |
| 4 | Cleaning Pipeline | 🟡 Basic whitespace/control-char/line-ending cleanup done. Header/footer/nav/cookie-banner removal not needed yet (no HTML source) |
| 5 | Metadata Pipeline | 🟡 Minimal — `content_metadata` JSONB currently only holds `page_number`. Title/author/department/tags/version not modeled yet |
| 6 | Document Classification | ⬜ Not started |
| 7 | Chunking Engine | 🟡 One strategy done (`RecursiveChunker`). Header-aware/HTML-aware/sentence/semantic/parent-child/adaptive not started. Chunker interface intentionally left undefined until a second chunker is built |
| 8 | Embeddings | 🟡 OpenAI (`text-embedding-3-small`) done — batched generation, stored in pgvector, versioned via `embedding_model` column. Other providers (Gemini, BGE, E5, Nomic, Sentence Transformers, Ollama) not started |
| 9 | Vector Storage | 🟡 `pgvector` column + migration in place. Index strategy (HNSW vs IVFFlat) not chosen yet — currently unindexed |
| 10 | Candidate Retrieval (vector search, BM25, hybrid, metadata/version/time filtering) | ⬜ Not started |
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

1. Vector index (HNSW) on `document_chunks.embedding` once query patterns exist to tune against
2. Retrieval (Phase 10) — the first point where the system can actually answer a question end-to-end
3. A second document source (e.g. website/HTML ingestion) — this is what would justify finally writing the `Extractor`/`Cleaner` interfaces

## Decisions log

- **Embedding model is `text-embedding-3-small` (1536 dims), fixed.** Multi-model support later needs either separate vector columns/tables per dimension or a projection step — noted for when Phase 8's provider list expands.
- **Interfaces for chunker/cleaner/extractor are intentionally empty files**, not missing work — see `CLAUDE.md`.
- **`embedding_model` column added to `document_chunks`** ahead of needing multiple providers, specifically so vectors stay traceable to the model that produced them (cheap to add now, expensive to backfill later).
