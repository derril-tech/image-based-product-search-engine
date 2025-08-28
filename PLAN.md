# Project Plan — Image-Based Product Search Engine

## Current Goal
Stand up a production-ready scaffold that covers:  
1. Next.js 14 frontend with upload/crop/search flows,  
2. NestJS API Gateway with OpenAPI contracts,  
3. Python workers for preprocessing, embedding, detection, and search,  
4. Milvus vector index + Postgres catalog,  
5. CI/CD, observability, and secrets hygiene.  

Enough for a demoable “import catalog → build index → upload image → crop → search results with filters.”

## Build Strategy
- Use CLIP embeddings (image & text) as baseline; YOLOv8 optional for region detection.  
- Milvus (or Qdrant) for high-perf ANN; Postgres for catalog + metadata; Redis for cache.  
- GPU pool for embedding/detection workers; autoscale with NATS queue depth.  
- Blueprint.js + Tailwind for polished UI.  

## Next Tasks
1. Scaffold monorepo: apps/frontend (Next.js), apps/gateway (NestJS), apps/workers (Python).  
2. Define Postgres schema + Milvus collections.  
3. Implement catalog import (Shopify/CSV).  
4. Build embedding pipeline (media preprocess → detect → embed → upsert Milvus).  
5. Frontend search UI with upload + crop + filters + streaming results.  

## Success Criteria (Launch)
- Index build throughput ≥ 10 imgs/sec/GPU.  
- P95 search latency < 700 ms for top-K=60.  
- Recall@20 ≥ 0.85 on labeled test set.  
- CTR uplift ≥ 20% in A/B tests vs baseline search.  
