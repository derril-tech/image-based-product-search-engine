# IMAGE‑BASED PRODUCT SEARCH ENGINE — END‑TO‑END PRODUCT BLUEPRINT

*(React 18 + Next.js 14 App Router; **Blueprint.js** + Tailwind utilities; TypeScript‑first contracts; Node/NestJS API gateway; Python CV/ML workers (PyTorch, torchvision/CLIP, OpenCV, YOLOv8/Detectron2 optional); **Milvus** (or Qdrant) for vector search; Postgres 16 for catalog & auth; Redis; S3/R2 for images/thumbnails; NATS event bus; optional ClickHouse for analytics; multi‑tenant; seats + usage‑based billing.)*

---

## 1) Product Description & Presentation

**One‑liner**
“Upload a photo and instantly find visually similar products — with filters, brands, and availability — across your entire catalog.”

**What it produces**

* **Visual search results**: ranked products with similarity score, variant swatches, price/availability, and facet filters.
* **Region crop & detect**: user can crop an area (e.g., the shoe in a lifestyle photo) or auto‑detect objects to search on the selected region.
* **Query‑by‑image + text**: combine an image with text attributes (e.g., “leather brown tote under \$200”).
* **Embeddings & analytics**: product and query embeddings, recall\@K metrics, and failure buckets.
* **Exports**: search session JSON, CSV of matched SKUs, and offline re‑ranking reports.

**Scope/Safety**

* Public image uploads are scanned (virus/NSFW) and rate‑limited.
* No face recognition or person re‑identification; product‑only detection by design.
* Clear disclaimers when exact item cannot be found (show visually closest alternatives).

---

## 2) Target User

* E‑commerce merchants (fashion, furniture, decor, auto parts).
* Marketplaces aggregating multiple vendors.
* Visual search for internal teams (buyers, merchandisers) and consumer apps.

---

## 3) Features & Functionalities (Extensive)

### Catalog & Connectors

* **Imports**: Shopify, BigCommerce, WooCommerce, CSV/JSON feed, Google Merchant feed, custom REST/GraphQL.
* **Variants**: color/size/material; parent/child SKU support; per‑region price & stock.
* **Images**: multiple views per SKU; auto‑background removal optional for cleaner embeddings.
* **Metadata**: brand, category tree, attributes, labels (sale/new), compliance tags.

### Ingestion & Embeddings

* **Preprocessing**: resize, center‑crop, background neutralization (optional), pHash for duplicates.
* **Feature extraction**: CLIP ViT‑B/32 baseline (image encoder) → 512‑D; fallback ResNet50; custom fine‑tuning hooks.
* **Object crops**: YOLOv8 detects product region(s); store region‑level embeddings alongside whole‑image embeddings.
* **Vector store**: Milvus IVF\_FLAT/HNSW index per tenant, partitioned by category; metadata kept in Postgres.

### Query Types

* **Image‑only**: upload or paste URL; choose region or whole image.
* **Image + text**: augment visual vector with CLIP text embedding (weighted fusion).
* **Text‑only**: CLIP text embedding search over product image vectors (zero‑shot baseline).
* **Multi‑example**: average of multiple query images to refine style.

### Retrieval & Ranking

* **ANN retrieval** from Milvus (k=200) → **attribute filter** (brand/category/price/size) → **re‑rank** with cross‑modal CLIP similarity and color/material heuristics.
* **Diversity** control (MMR) to avoid near duplicates in top results.
* **Business rules**: in‑stock boost, margin boost, new arrivals; per‑tenant re‑rank plugin.

### UX & Tools

* **Smart crop** with auto‑suggested boxes; hover highlight on detected objects.
* **Facet filters**: price range, brand, size, color, material, vendor; availability and shipping.
* **Compare view** and **related variants** (colorway thumbnails).
* **Feedback**: thumbs up/down, “more like this,” hide vendor.
* **Collections**: save search boards; shareable links for buyers/teams.

### Analytics & Quality

* **Dashboards**: recall\@K from labeled sets, click‑through, conversion proxy (click→add‑to‑cart webhook), latency percentiles, index health.
* **Diagnostics**: failure buckets (bad crop, wrong category, OOS), embedding drift monitor, cold‑start items coverage.
* **AB testing**: model/re‑rank variants on traffic slices.

### Integrations

* **Storefront**: JavaScript SDK and REST; Shopify app snippet; headless storefronts (Next.js Commerce).
* **PIM/ERP**: product attribute sync; stock/price webhooks.
* **CDN/Media**: Cloudfront/Cloudflare for images; on‑the‑fly thumbnailing.

---

## 4) Backend Architecture (Extremely Detailed & Deployment‑Ready)

### 4.1 Topology

* **Frontend/BFF:** Next.js 14 (Vercel). Server Actions for presigned uploads, share link creation; SSR/ISR for public result pages.
* **API Gateway:** **NestJS (Node 20)** — REST `/v1` (OpenAPI 3.1), Zod validation, Problem+JSON, RBAC (Casbin), RLS, rate limits, Idempotency‑Key, Request‑ID (ULID).
* **Workers (Python 3.11 + FastAPI control):**
  `ingest-worker` (feeds/connectors), `media-worker` (preprocess, pHash, BG removal), `embed-worker` (CLIP/ResNet), `detect-worker` (YOLOv8), `index-worker` (Milvus ops), `search-worker` (re‑rank, MMR), `report-worker` (quality/AB), `export-worker`.
* **Event Bus/Queues:** NATS (subjects: `feed.pull`, `media.process`, `embed.run`, `detect.run`, `index.upsert`, `search.query`, `report.make`) + Redis Streams; Celery/RQ orchestration.
* **Datastores:** **Milvus** (vectors), **Postgres 16** (catalog, tenants, auth, results), **S3/R2** (images/thumbnails/exports), **Redis** (cache/session), optional **ClickHouse** (metrics).
* **Observability:** OpenTelemetry traces/logs/metrics; Prometheus/Grafana; Sentry.
* **Secrets:** Cloud Secrets Manager/KMS.

### 4.2 Data Model (Postgres + Milvus metadata)

```sql
-- Tenancy & Identity
CREATE TABLE orgs (id UUID PRIMARY KEY, name TEXT NOT NULL, plan TEXT DEFAULT 'pro', region TEXT, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE users (id UUID PRIMARY KEY, org_id UUID REFERENCES orgs(id) ON DELETE CASCADE, email CITEXT UNIQUE NOT NULL, name TEXT, role TEXT DEFAULT 'editor', tz TEXT, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE memberships (user_id UUID, org_id UUID, role TEXT CHECK (role IN ('owner','admin','editor','viewer')), PRIMARY KEY (user_id, org_id));

-- Catalog
CREATE TABLE products (
  id UUID PRIMARY KEY, org_id UUID, sku TEXT, title TEXT, brand TEXT, category_path TEXT[], price NUMERIC, currency TEXT,
  description TEXT, attributes JSONB, status TEXT CHECK (status IN ('active','draft','archived')) DEFAULT 'active',
  stock INT, vendor TEXT, created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE variants (
  id UUID PRIMARY KEY, product_id UUID REFERENCES products(id) ON DELETE CASCADE,
  sku TEXT, attrs JSONB, price NUMERIC, stock INT, created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE images (
  id UUID PRIMARY KEY, product_id UUID, variant_id UUID, url TEXT, s3_key TEXT, width INT, height INT, phash TEXT, meta JSONB
);

-- Embeddings & Detection (Milvus holds vectors; Postgres maps ids)
CREATE TABLE embeddings (
  id UUID PRIMARY KEY, org_id UUID, product_id UUID, variant_id UUID, image_id UUID,
  level TEXT CHECK (level IN ('image','region')), detector JSONB, vector_id BIGINT, dims INT, model TEXT, created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE regions (
  id UUID PRIMARY KEY, image_id UUID, bbox JSONB, label TEXT, confidence NUMERIC, created_at TIMESTAMPTZ DEFAULT now()
);

-- Search & Feedback
CREATE TABLE searches (
  id UUID PRIMARY KEY, org_id UUID, user_id UUID, mode TEXT, text_query TEXT, filters JSONB, top_k INT, latency_ms INT,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE results (
  id UUID PRIMARY KEY, search_id UUID REFERENCES searches(id) ON DELETE CASCADE, product_id UUID, variant_id UUID,
  score NUMERIC, rank INT, reason JSONB
);
CREATE TABLE feedback (
  id UUID PRIMARY KEY, search_id UUID, product_id UUID, signal TEXT CHECK (signal IN ('up','down','hide','save','cart')), created_at TIMESTAMPTZ DEFAULT now()
);

-- Connectors & Feeds
CREATE TABLE connectors (id UUID PRIMARY KEY, org_id UUID, kind TEXT, config JSONB, enabled BOOLEAN DEFAULT TRUE);
CREATE TABLE feeds (id UUID PRIMARY KEY, org_id UUID, source TEXT, last_pull TIMESTAMPTZ, status TEXT, stats JSONB);

-- Audit
CREATE TABLE audit_log (id BIGSERIAL PRIMARY KEY, org_id UUID, user_id UUID, action TEXT, target TEXT, meta JSONB, created_at TIMESTAMPTZ DEFAULT now());
```

**Invariants**

* RLS by `org_id`; per‑tenant Milvus collections/partitions.
* `images.phash` used for duplicate suppression; unique constraint optional per tenant.
* Embedding `vector_id` maps to Milvus primary key; `level` indicates whole‑image vs region.

### 4.3 API Surface (REST `/v1`, OpenAPI)

**Auth/Orgs/Users**

* `POST /auth/login`, `POST /auth/refresh`, `GET /me`.

**Catalog**

* `POST /products` `{sku,title,brand,price,category_path,attributes}`
* `POST /products/:id/images` → upload URL
* `POST /feeds/pull` `{connector}`
* `GET /products/:id|/variants|/images`

**Indexing**

* `POST /index/build` `{product_ids?}`
* `POST /index/rebuild` `{model}`
* `GET /index/status`

**Search**

* `POST /search/image` `{image_url|upload, bbox?, text?, filters?, top_k?}`
* `POST /search/text` `{q, filters?, top_k?}`
* `POST /search/multi` `{images:[...], weights?, text?}`
* `POST /feedback` `{search_id, product_id, signal}`

**Reports/Exports**

* `GET /reports/quality?from&to`
* `POST /exports/session` `{search_id}` → JSON/CSV

**Conventions**

* Idempotency‑Key on mutations; Problem+JSON errors; cursor pagination; rate limits and image size caps.

### 4.4 Pipelines & Workers

**Ingest**

1. Pull catalog via connector/feed → normalize products/variants → download images → pHash → enqueue `media.process`.

**Media & Detect**
2\) Preprocess (resize, bg remove?) → run YOLOv8 to detect product regions → write `regions` → enqueue `embed.run` for image + regions.

**Embed & Index**
3\) CLIP encoder → vectors (image and each region) → upsert into Milvus with metadata; write `embeddings` mapping.

**Search**
4\) On query: build vector(s) (image/text), ANN search in relevant partitions (by category if filters) → attribute gating → re‑rank (CLIP sim + color/material heuristics + business rules) → diversity (MMR) → return.

**Learning**
5\) Incorporate feedback to adjust re‑rank weights; track AB test variants; schedule periodic fine‑tuning (optional) with triplet loss on labeled pairs.

**Reports**
6\) Aggregate metrics (recall\@K on labeled set, latency, CTR) → generate dashboards and CSV/PDF.

### 4.5 Realtime

* WebSocket: `search:{id}:tokens` for progressive result reveal; `index:{org}:status` for indexing progress.
* SSE fallback for search token stream and long index jobs.

### 4.6 Caching & Performance

* Redis caches for popular queries, color histograms, attribute dictionaries, CDN image heads.
* Milvus HNSW tuned per partition; warm caches on startup; parallel embeds with GPU pool.
* Thumbnails via on‑the‑fly resizing (Thumbor/imgproxy) with CDN.

### 4.7 Observability

* OTel spans: `feed.pull`, `media.preprocess`, `detect.run`, `embed.run`, `index.upsert`, `search.ann`, `rerank`, `diversify`.
* Metrics: p50/p95 search latency, recall\@K, duplicate rate via pHash, index build times, GPU utilization, error rates.
* Alerts: ANN latency spikes, index corruption, connector failures.

### 4.8 Security & Compliance

* TLS/HSTS/CSP; signed S3 URLs; per‑tenant bucket prefixes.
* NSFW/virus scan for uploads; content policy enforcement.
* SSO/SAML/OIDC; SCIM; RLS; immutable `audit_log`.
* DSR endpoints; retention windows; PII minimization (no faces/person IDs stored).

---

## 5) Frontend Architecture (React 18 + Next.js 14)

### 5.1 Tech Choices

* **UI:** Blueprint.js (Navbar, Tabs, Dialog, Drawer, Table/HTMLTable, Slider, MultiSelect) + Tailwind for layout.
* **Viewer:** React‑Image/Canvas for region crop & overlay; color picker histogram.
* **State/Data:** TanStack Query; Zustand for editor/search UI; URL‑synced filters.
* **Realtime:** WS client; SSE fallback.
* **i18n/A11y:** next‑intl; screen‑reader labels for results and crop tool; keyboard shortcuts.

### 5.2 App Structure

```
/app
  /(marketing)/page.tsx
  /(auth)/sign-in/page.tsx
  /(app)/dashboard/page.tsx
  /(app)/catalog/page.tsx
  /(app)/search/page.tsx
  /(app)/collections/page.tsx
  /(app)/reports/page.tsx
  /(app)/connectors/page.tsx
  /(app)/settings/page.tsx
/components
  Upload/*           // DropZone, UrlPaste, ImageSanity
  Cropper/*          // RegionSelector, BoxList
  ResultGrid/*       // ProductCard, VariantSwatches, ScoreBadge
  Facets/*           // Brand, Price, Size, Color, Material
  Compare/*          // SideBySide, SimilarCarousel
  Collections/*      // Board, ShareLink
  Catalog/*          // ImportTable, ImageHealth
  Reports/*          // KPIs, Charts
  Connectors/*       // Shopify, BigCommerce, Woo forms
/lib
  api-client.ts
  ws-client.ts
  zod-schemas.ts
  rbac.ts
/store
  useSearchStore.ts
  useCatalogStore.ts
  useFilterStore.ts
```

### 5.3 Key Pages & UX Flows

**Search**

* Upload image or paste URL → auto‑detect objects → pick region or draw box → optional text (“brown leather tote under \$200”) → results stream in with facet filters; drag slider to trade off strict visual match vs broader style.

**Catalog**

* Import products; view image quality checks; reindex selected SKUs; inspect embeddings and detected regions.

**Collections**

* Save favorite results to boards; share link; comments for merchandisers.

**Reports**

* Recall\@K over labeled set; latency distributions; duplicates; CTR by category; export CSV.

**Connectors**

* OAuth for Shopify/BigCommerce/Woo; map attribute fields; schedule sync.

### 5.4 Component Breakdown (Selected)

* **Cropper/RegionSelector.tsx**
  Props: `{ image, detections, onChange }`
  Draw/resize boxes; snap to detected regions; keyboard nudge; emits bbox.

* **ResultGrid/ProductCard.tsx**
  Props: `{ product, score, variants }`
  Shows hero and swatches; hover reveals alt views; quick add to collection.

* **Facets/ColorFacet.tsx**
  Props: `{ palette, onSelect }`
  Picks dominant colors from query; filters results by color distance.

* **Compare/SimilarCarousel.tsx**
  Props: `{ seedProductId }`
  Shows visually similar SKUs; supports “more like this” feedback.

### 5.5 Data Fetching & Caching

* Server Components for catalog and report snapshots.
* TanStack Query with background refetch; optimistic updates for feedback and board saves.
* Prefetch: catalog → index status → search.

### 5.6 Validation & Error Handling

* Zod schemas; Problem+JSON renderer (oversized image, unsupported format, NSFW flag).
* Guards: search disabled if index not built; connectors require attribute mapping validation.

### 5.7 Accessibility & i18n

* Keyboard crop controls; labels for similarity scores; high‑contrast; RTL; localized currencies.

---

## 6) SDKs & Integration Contracts

**JavaScript Web SDK (minimal)**

```ts
import { VisualSearch } from '@vizsearch/sdk';
const client = new VisualSearch({ apiKey: 'pub_xxx' });
const res = await client.searchImage({ imageUrl, text: 'brown leather tote', filters: { priceLt: 200 } });
```

**Search (REST)**

```http
POST /v1/search/image
Content-Type: application/json
{"image_url":"https://.../street-look.jpg","bbox":{"x":120,"y":240,"w":320,"h":380},"text":"brown leather tote","filters":{"price_lte":200,"category":"bags"},"top_k":60}
```

**Index Build**

```http
POST /v1/index/build {"product_ids":["sku_123","sku_456"]}
```

**Export Session**

```http
POST /v1/exports/session {"search_id":"srch_abc"}
```

**JSON Bundle** keys: `search`, `query`, `results[]`, `products[]`, `embeddings[]` (ids only), `diagnostics`.

---

## 7) DevOps & Deployment

* **FE:** Vercel (Next.js).
* **APIs/Workers:** Render/Fly/GKE; GPU pool for embed/detect; autoscaling with queue depth.
* **DB:** Managed Postgres; **Milvus** on managed cluster (or Qdrant/Weaviate alternative) with backups.
* **Cache/Bus:** Redis + NATS; DLQ with retries/backoff/jitter.
* **Storage:** S3/R2 with lifecycle (originals, thumbnails).
* **CI/CD:** GitHub Actions (lint/typecheck/unit/integration, Docker, scan, sign, deploy); blue/green; migration approvals.
* **IaC:** Terraform modules for DB/Redis/NATS/Milvus/buckets/CDN/secrets/DNS.
* **Envs:** dev/staging/prod; per‑tenant region option; error budgets/alerts.

**Operational SLOs**

* Index build throughput **≥ 10 imgs/sec/GPU** (CLIP baseline).
* P95 search latency **< 700 ms** (warm index, k=60).
* Recall\@20 on labeled set **≥ 0.85** after tuning.
* 5xx **< 0.5%/1k**.

---

## 8) Testing

* **Unit:** pHash dedupe; bbox math; CLIP encode wrapper; MMR diversity; color distance.
* **Integration:** feed → preprocess → detect → embed → index → search (image/text/mixed) → re‑rank.
* **Regression:** recall\@K guardrails on canary set; latency budgets by category; NSFW filter rules.
* **E2E (Playwright):** import catalog → build index → user uploads lifestyle photo → crop → apply filters → click‑through to PDP.
* **Load:** concurrent search spikes; index rebuild during traffic; cache stampede protection.
* **Chaos:** GPU node kill; Milvus pod restart; connector 5xx; ensure retries/backoff and graceful degradation.
* **Security:** RLS coverage; signed URL expiry; audit completeness.

---

## 9) Success Criteria

**Product KPIs**

* Click‑through rate **≥ 20%** on visual search results pages.
* Add‑to‑cart uplift **≥ 8%** for users exposed to visual search vs control.
* Time‑to‑first result **≤ 1.2 s** p95 for common categories.
* Merchant satisfaction (quality thumbs‑up) **≥ 80%** on top queries.

**Engineering SLOs**

* Pipeline success **≥ 99%** excl. provider outages; index rebuild completes overnight for 95% of tenants; search error rate **< 0.3%**.

---

## 10) Visual/Logical Flows

**A) Import → Preprocess → Index**
Connect Shopify/CSV → normalize → download images → pHash + detect → CLIP embeddings → Milvus upsert → ready.

**B) User Query**
Upload image (or URL) → auto detect/crop → optional text & filters → ANN retrieve → re‑rank & diversify → results grid.

**C) Iterate**
User feedback (“more like this”) → adjust weights → save to board → share with team.

**D) Monitor**
Dashboards show recall\@K, CTR, latency; alerts on index health and connector failures; AB test new ranker variant.
