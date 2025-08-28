# Task List — Image-Based Product Search Engine


PHASE 1:












- [x] Worker: report/analytics (recall@K, latency, CTR).
- [x] Worker: export session (JSON, CSV).
- [x] Frontend: marketing site (landing page).
- [x] Frontend: auth pages (sign-in, register).

PHASE 2:
- [x] Frontend: dashboard shell.
- [x] Frontend: catalog import UI (feeds, connectors).
- [x] Frontend: search page (upload, crop, results, facets).
- [x] Frontend: collections/boards (save, share).
- [x] Frontend: reports dashboard (KPIs, charts).
- [x] Components: Upload, Cropper, ResultGrid, Facets, Compare, Collections, CatalogTable, Reports.
- [x] Implement websocket client for realtime search status.
- [x] Add CDN for image delivery; thumbnailing pipeline.
- [x] Add observability (OTel traces, Prometheus metrics, Sentry).
- [x] Implement NSFW/virus scanning for uploads.
- [x] Add audit logging across API/workers.

PHASE 3:
- [x] Setup billing (multi-tenant plans, usage-based add-ons).
- [x] Testing: unit (pHash, bbox math, CLIP encode wrapper, MMR diversity).
- [x] Testing: integration (feed → preprocess → detect → embed → index → search).
- [x] Testing: regression (recall@K guardrails, latency budgets).
- [x] Testing: E2E (import catalog → build index → upload image → crop → search → PDP).
- [x] Testing: load (search spikes, index rebuilds).
- [x] Testing: chaos (GPU node kill, Milvus pod restart, connector failures).
- [x] Testing: security (RLS, signed URL expiry, audit completeness).
