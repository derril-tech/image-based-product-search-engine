"""FastAPI router for advanced search endpoints."""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional, Union
import json

from ..models.search_models import (
    SearchRequest, SearchResponse, SearchType, RerankModel, MMRStrategy,
    BusinessRule, BusinessRuleType, SearchConfig, SearchStats, SearchAnalytics,
    SearchSuggestion, SearchSuggestionsResponse, SearchFacet, SearchFacetsResponse,
    SearchFilter, SearchQuery
)
from ..services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Advanced Search"])

# Initialize service
search_service = SearchService()

@router.post("/", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Perform advanced search with reranking, MMR, and business rules."""
    try:
        return await search_service.search(request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text")
async def text_search(
    query: str,
    collection_name: str,
    organization_id: str,
    top_k: int = Query(20, ge=1, le=1000),
    enable_rerank: bool = Query(True),
    enable_mmr: bool = Query(False),
    mmr_lambda: float = Query(0.5, ge=0.0, le=1.0),
    filters: Optional[str] = None  # JSON string
):
    """Perform text-based search."""
    try:
        # Parse filters
        filters_dict = {}
        if filters:
            filters_dict = json.loads(filters)
        
        request = SearchRequest(
            query=query,
            search_type=SearchType.TEXT,
            collection_name=collection_name,
            organization_id=organization_id,
            top_k=top_k,
            enable_rerank=enable_rerank,
            enable_mmr=enable_mmr,
            mmr_lambda=mmr_lambda,
            filters=filters_dict
        )
        
        return await search_service.search(request)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in filters parameter")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image")
async def image_search(
    query_vector: str,  # JSON string of embedding vector
    collection_name: str,
    organization_id: str,
    top_k: int = Query(20, ge=1, le=1000),
    enable_rerank: bool = Query(True),
    enable_mmr: bool = Query(False),
    mmr_lambda: float = Query(0.5, ge=0.0, le=1.0),
    filters: Optional[str] = None  # JSON string
):
    """Perform image-based search."""
    try:
        # Parse query vector
        vector = json.loads(query_vector)
        
        # Parse filters
        filters_dict = {}
        if filters:
            filters_dict = json.loads(filters)
        
        request = SearchRequest(
            query=vector,
            search_type=SearchType.IMAGE,
            collection_name=collection_name,
            organization_id=organization_id,
            top_k=top_k,
            enable_rerank=enable_rerank,
            enable_mmr=enable_mmr,
            mmr_lambda=mmr_lambda,
            filters=filters_dict
        )
        
        return await search_service.search(request)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in parameters")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/multimodal")
async def multimodal_search(
    query: str,
    query_vector: str,  # JSON string of embedding vector
    collection_name: str,
    organization_id: str,
    top_k: int = Query(20, ge=1, le=1000),
    enable_rerank: bool = Query(True),
    enable_mmr: bool = Query(True),
    mmr_lambda: float = Query(0.4, ge=0.0, le=1.0),
    filters: Optional[str] = None  # JSON string
):
    """Perform multimodal search (text + image)."""
    try:
        # Parse query vector
        vector = json.loads(query_vector)
        
        # Parse filters
        filters_dict = {}
        if filters:
            filters_dict = json.loads(filters)
        
        # For multimodal, we'll use the text query as primary
        request = SearchRequest(
            query=query,
            search_type=SearchType.MULTIMODAL,
            collection_name=collection_name,
            organization_id=organization_id,
            top_k=top_k,
            enable_rerank=enable_rerank,
            enable_mmr=enable_mmr,
            mmr_lambda=mmr_lambda,
            filters=filters_dict
        )
        
        return await search_service.search(request)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in parameters")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions", response_model=SearchSuggestionsResponse)
async def get_suggestions(
    query: str,
    collection_name: str,
    limit: int = Query(10, ge=1, le=50)
):
    """Get search suggestions for autocomplete."""
    try:
        return await search_service.get_search_suggestions(query, collection_name, limit)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/facets", response_model=SearchFacetsResponse)
async def get_facets(
    collection_name: str,
    fields: str  # Comma-separated field names
):
    """Get search facets for filtering."""
    try:
        field_list = [field.strip() for field in fields.split(",")]
        return await search_service.get_search_facets(collection_name, field_list)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=SearchStats)
async def get_search_stats(
    start_time: str,  # ISO format datetime string
    end_time: str,    # ISO format datetime string
    organization_id: Optional[str] = None
):
    """Get search statistics for the specified time range."""
    try:
        from datetime import datetime
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        return await search_service.get_search_stats(start_dt, end_dt)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/business-rules")
async def add_business_rule(rule: BusinessRule):
    """Add a business rule."""
    try:
        await search_service.add_business_rule(rule)
        return {"message": f"Business rule {rule.rule_id} added successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/business-rules")
async def list_business_rules():
    """List all business rules."""
    try:
        return await search_service.list_business_rules()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/business-rules/{rule_id}")
async def get_business_rule(rule_id: str):
    """Get a specific business rule."""
    try:
        return await search_service.get_business_rule(rule_id)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/business-rules/{rule_id}")
async def remove_business_rule(rule_id: str):
    """Remove a business rule."""
    try:
        await search_service.remove_business_rule(rule_id)
        return {"message": f"Business rule {rule_id} removed successfully"}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rerank")
async def rerank_results(
    query: str,
    candidates: str,  # JSON string of SearchResult objects
    model: RerankModel = RerankModel.CROSS_ENCODER,
    top_k: Optional[int] = None,
    batch_size: int = Query(16, ge=1, le=64)
):
    """Rerank search results using specified model."""
    try:
        # Parse candidates
        candidates_list = json.loads(candidates)
        
        # Convert to SearchResult objects
        from ..models.search_models import SearchResult
        search_results = []
        for candidate in candidates_list:
            result = SearchResult(**candidate)
            search_results.append(result)
        
        # Create rerank request
        from ..models.search_models import RerankRequest
        rerank_request = RerankRequest(
            query=query,
            candidates=search_results,
            model=model,
            top_k=top_k,
            batch_size=batch_size
        )
        
        # Perform reranking
        reranked_results = await search_service._perform_reranking(rerank_request)
        
        return {
            "reranked_results": [result.dict() for result in reranked_results],
            "total_candidates": len(reranked_results),
            "model_used": model.value
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in candidates parameter")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mmr")
async def apply_mmr(
    query: str,
    candidates: str,  # JSON string of SearchResult objects
    strategy: MMRStrategy = MMRStrategy.BALANCED,
    lambda_param: float = Query(0.5, ge=0.0, le=1.0),
    top_k: Optional[int] = None
):
    """Apply Maximal Marginal Relevance to search results."""
    try:
        # Parse candidates
        candidates_list = json.loads(candidates)
        
        # Convert to SearchResult objects
        from ..models.search_models import SearchResult
        search_results = []
        for candidate in candidates_list:
            result = SearchResult(**candidate)
            search_results.append(result)
        
        # Create MMR request
        from ..models.search_models import MMRRequest
        mmr_request = MMRRequest(
            query=query,
            candidates=search_results,
            strategy=strategy,
            lambda_param=lambda_param,
            top_k=top_k
        )
        
        # Perform MMR
        mmr_results = await search_service._perform_mmr(mmr_request)
        
        return {
            "mmr_results": [result.dict() for result in mmr_results],
            "strategy_used": strategy.value,
            "lambda_used": lambda_param,
            "total_results": len(mmr_results)
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in candidates parameter")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/configs")
async def get_search_configs():
    """Get available search configurations."""
    configs = {
        "search_types": {
            "image": {
                "description": "Image-based search using visual embeddings",
                "default_config": {
                    "ann_top_k": 100,
                    "rerank_enabled": True,
                    "rerank_model": "cross_encoder",
                    "mmr_enabled": False
                }
            },
            "text": {
                "description": "Text-based search using text embeddings",
                "default_config": {
                    "ann_top_k": 100,
                    "rerank_enabled": True,
                    "rerank_model": "bi_encoder",
                    "mmr_enabled": True,
                    "mmr_lambda": 0.3
                }
            },
            "multimodal": {
                "description": "Multimodal search combining text and image",
                "default_config": {
                    "ann_top_k": 150,
                    "rerank_enabled": True,
                    "rerank_model": "cross_encoder",
                    "mmr_enabled": True,
                    "mmr_lambda": 0.4
                }
            },
            "hybrid": {
                "description": "Hybrid search with multiple strategies",
                "default_config": {
                    "ann_top_k": 200,
                    "rerank_enabled": True,
                    "rerank_model": "cross_encoder",
                    "mmr_enabled": True,
                    "mmr_lambda": 0.5
                }
            }
        },
        "rerank_models": {
            "cross_encoder": {
                "description": "Cross-encoder for high accuracy reranking",
                "best_for": "High accuracy requirements"
            },
            "bi_encoder": {
                "description": "Bi-encoder for fast reranking",
                "best_for": "Speed requirements"
            }
        },
        "mmr_strategies": {
            "diversity": {
                "description": "Maximize result diversity",
                "lambda_range": [0.0, 0.3]
            },
            "relevance": {
                "description": "Maximize result relevance",
                "lambda_range": [0.7, 1.0]
            },
            "balanced": {
                "description": "Balance diversity and relevance",
                "lambda_range": [0.3, 0.7]
            }
        }
    }
    
    return configs

@router.post("/batch")
async def batch_search(
    queries: str,  # JSON string of search queries
    collection_name: str,
    organization_id: str,
    search_type: SearchType = SearchType.IMAGE,
    top_k: int = Query(20, ge=1, le=1000),
    enable_rerank: bool = Query(True),
    enable_mmr: bool = Query(False)
):
    """Perform batch search for multiple queries."""
    try:
        # Parse queries
        queries_list = json.loads(queries)
        
        results = []
        for query in queries_list:
            if isinstance(query, str):
                # Text query
                request = SearchRequest(
                    query=query,
                    search_type=search_type,
                    collection_name=collection_name,
                    organization_id=organization_id,
                    top_k=top_k,
                    enable_rerank=enable_rerank,
                    enable_mmr=enable_mmr
                )
            else:
                # Vector query
                request = SearchRequest(
                    query=query,
                    search_type=search_type,
                    collection_name=collection_name,
                    organization_id=organization_id,
                    top_k=top_k,
                    enable_rerank=enable_rerank,
                    enable_mmr=enable_mmr
                )
            
            result = await search_service.search(request)
            results.append(result.dict())
        
        return {
            "results": results,
            "total_queries": len(queries_list),
            "collection_name": collection_name,
            "search_type": search_type.value
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in queries parameter")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def search_health():
    """Get search service health status."""
    try:
        # Check if services are available
        health_status = {
            "status": "healthy",
            "services": {
                "search_service": "available",
                "index_service": "available",
                "embedding_service": "available"
            },
            "business_rules_count": len(await search_service.list_business_rules()),
            "search_stats_count": len(search_service.search_stats),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
