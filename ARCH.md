# Architecture Overview — Image-Based Product Search Engine

## High-Level Topology
- Frontend: Next.js 14 (React 18, TS, Blueprint.js + Tailwind) on Vercel.
- API Gateway: NestJS (REST /v1, OpenAPI, Zod validation, RBAC, RLS).
- Workers: Python (FastAPI microservices) for ingest, preprocess, detect, embed, index, search, report, export.
- Event Bus: NATS + Redis Streams; Celery/RQ orchestration.
- Datastores: Milvus (vectors), Postgres (catalog/auth), Redis (cache/session), S3/R2 (images/thumbnails), optional ClickHouse (analytics).
- Observability: OpenTelemetry → Prometheus/Grafana, Sentry.
- Secrets: Cloud Secrets Manager/KMS.

## Data Model (Postgres + Milvus metadata)
- orgs, users, memberships (RBAC, tenancy).
- products, variants, images (catalog).
- embeddings (maps IDs → Milvus vectors, level=image|region).
- regions (YOLO crops, bboxes, confidence).
- searches, results, feedback (query logs + signals).
- connectors, feeds (Shopify, BigCommerce, CSV, etc).
- audit_log (immutable access/actions).

## API Surface (REST /v1)
- Auth: login, refresh, me.
- Catalog: create/list products, variants, images; feed pulls.
- Indexing: build/rebuild index; status.
- Search: /search/image, /search/text, /search/multi; feedback.
- Reports/Exports: quality dashboards, session export JSON/CSV.
- Conventions: Idempotency-Key, Problem+JSON errors, cursor pagination.

## Pipelines
- Ingest: feed → normalize → download images → preprocess (resize, pHash) → detect objects → embed (CLIP) → upsert Milvus.
- Search: query embed → ANN retrieve → filter/rerank (MMR, business rules) → results stream.
- Learning: feedback incorporated into rerank weights; AB test variants.
- Reports: recall@K, latency, index health, CTR.

## Frontend (Next.js 14)
- Upload + cropper (React Image/Canvas).
- Result grid with facets (price, brand, size, color).
- Collections (boards, share links).
- Catalog import UI; reports dashboard.
- State: TanStack Query + Zustand.
- Realtime: WS for search progress; SSE fallback.

## DevOps & CI/CD
- GitHub Actions: lint, typecheck, unit/integration tests, docker builds, deploy.
- Terraform for Postgres, Redis, NATS, Milvus, buckets, secrets, DNS.
- Envs: dev/staging/prod; per-tenant Milvus collections.
- SLOs: search latency < 700ms p95, recall@20 ≥ 0.85, error <0.5%.
