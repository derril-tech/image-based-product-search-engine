# Created automatically by Cursor AI (2024-12-19)

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import numpy as np
from ..services.advanced_search import (
    AdvancedSearchService, RerankingConfig, MMRConfig, BusinessRule,
    RerankingModel, MMRStrategy, BusinessRuleType
)
from ..services.embedding_service import EmbeddingService
from ..dependencies import get_advanced_search_service, get_embedding_service

router = APIRouter(prefix="/advanced-search", tags=["Advanced Search"])


class BusinessRuleRequest(BaseModel):
    rule_type: BusinessRuleType
    field: str
    value: Any
    weight: float = Field(default=1.0, ge=0.0)
    operator: str = Field(default="eq")
    description: str = Field(default="")


class RerankingConfigRequest(BaseModel):
    model: RerankingModel = RerankingModel.CROSS_ENCODER
    model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    top_k: int = Field(default=100, ge=1, le=1000)
    batch_size: int = Field(default=32, ge=1, le=128)
    device: str = "cpu"


class MMRConfigRequest(BaseModel):
    strategy: MMRStrategy = MMRStrategy.BALANCED
    lambda_param: float = Field(default=0.5, ge=0.0, le=1.0)
    diversity_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    max_results: int = Field(default=20, ge=1, le=100)


class SearchRequest(BaseModel):
    query_embedding: List[float]
    collection_name: str
    top_k: int = Field(default=20, ge=1, le=100)
    reranking_config: Optional[RerankingConfigRequest] = None
    mmr_config: Optional[MMRConfigRequest] = None
    business_rules: Optional[List[BusinessRuleRequest]] = None


class SearchResultResponse(BaseModel):
    id: str
    score: float
    metadata: Dict[str, Any]


class SearchResponse(BaseModel):
    results: List[SearchResultResponse]
    total_count: int
    search_time_ms: float
    reranking_applied: bool
    mmr_applied: bool
    business_rules_applied: bool


@router.post("/search", response_model=SearchResponse)
async def advanced_search(
    request: SearchRequest,
    search_service: AdvancedSearchService = Depends(get_advanced_search_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
):
    """Perform advanced search with reranking, MMR, and business rules."""
    try:
        import time
        start_time = time.time()
        
        # Convert query embedding to numpy array
        query_embedding = np.array(request.query_embedding)
        
        # Convert configurations
        reranking_config = None
        if request.reranking_config:
            reranking_config = RerankingConfig(
                model=request.reranking_config.model,
                model_name=request.reranking_config.model_name,
                top_k=request.reranking_config.top_k,
                batch_size=request.reranking_config.batch_size,
                device=request.reranking_config.device
            )
        
        mmr_config = None
        if request.mmr_config:
            mmr_config = MMRConfig(
                strategy=request.mmr_config.strategy,
                lambda_param=request.mmr_config.lambda_param,
                diversity_threshold=request.mmr_config.diversity_threshold,
                max_results=request.mmr_config.max_results
            )
        
        business_rules = None
        if request.business_rules:
            business_rules = [
                BusinessRule(
                    rule_type=rule.rule_type,
                    field=rule.field,
                    value=rule.value,
                    weight=rule.weight,
                    operator=rule.operator,
                    description=rule.description
                )
                for rule in request.business_rules
            ]
        
        # Perform search based on configuration
        if mmr_config:
            results = await search_service.search_with_mmr(
                query_embedding=query_embedding,
                collection_name=request.collection_name,
                mmr_config=mmr_config,
                business_rules=business_rules
            )
        else:
            results = await search_service.search_with_reranking(
                query_embedding=query_embedding,
                collection_name=request.collection_name,
                top_k=request.top_k,
                reranking_config=reranking_config,
                business_rules=business_rules
            )
        
        # Convert to response format
        search_results = [
            SearchResultResponse(
                id=result.id,
                score=result.score,
                metadata=result.metadata
            )
            for result in results
        ]
        
        search_time = (time.time() - start_time) * 1000
        
        return SearchResponse(
            results=search_results,
            total_count=len(search_results),
            search_time_ms=search_time,
            reranking_applied=reranking_config is not None,
            mmr_applied=mmr_config is not None,
            business_rules_applied=business_rules is not None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/rerank", response_model=List[SearchResultResponse])
async def rerank_results(
    results: List[SearchResultResponse],
    query_embedding: List[float],
    config: RerankingConfigRequest,
    search_service: AdvancedSearchService = Depends(get_advanced_search_service)
):
    """Rerank existing search results."""
    try:
        # Convert to internal format
        search_results = [
            search_service.SearchResult(
                id=result.id,
                score=result.score,
                metadata=result.metadata
            )
            for result in results
        ]
        
        query_embedding_np = np.array(query_embedding)
        reranking_config = RerankingConfig(
            model=config.model,
            model_name=config.model_name,
            top_k=config.top_k,
            batch_size=config.batch_size,
            device=config.device
        )
        
        # Apply reranking
        reranked_results = await search_service._rerank_results(
            search_results, query_embedding_np, reranking_config
        )
        
        # Convert back to response format
        return [
            SearchResultResponse(
                id=result.id,
                score=result.score,
                metadata=result.metadata
            )
            for result in reranked_results
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reranking failed: {str(e)}")


@router.post("/mmr", response_model=List[SearchResultResponse])
async def apply_mmr(
    results: List[SearchResultResponse],
    query_embedding: List[float],
    config: MMRConfigRequest,
    search_service: AdvancedSearchService = Depends(get_advanced_search_service)
):
    """Apply Maximal Marginal Relevance to existing results."""
    try:
        # Convert to internal format
        search_results = [
            search_service.SearchResult(
                id=result.id,
                score=result.score,
                metadata=result.metadata
            )
            for result in results
        ]
        
        query_embedding_np = np.array(query_embedding)
        mmr_config = MMRConfig(
            strategy=config.strategy,
            lambda_param=config.lambda_param,
            diversity_threshold=config.diversity_threshold,
            max_results=config.max_results
        )
        
        # Apply MMR
        mmr_results = search_service._apply_mmr(
            search_results, query_embedding_np, mmr_config
        )
        
        # Convert back to response format
        return [
            SearchResultResponse(
                id=result.id,
                score=result.score,
                metadata=result.metadata
            )
            for result in mmr_results
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MMR application failed: {str(e)}")


@router.post("/business-rules", response_model=List[SearchResultResponse])
async def apply_business_rules(
    results: List[SearchResultResponse],
    business_rules: List[BusinessRuleRequest],
    search_service: AdvancedSearchService = Depends(get_advanced_search_service)
):
    """Apply business rules to existing search results."""
    try:
        # Convert to internal format
        search_results = [
            search_service.SearchResult(
                id=result.id,
                score=result.score,
                metadata=result.metadata
            )
            for result in results
        ]
        
        # Convert business rules
        rules = [
            BusinessRule(
                rule_type=rule.rule_type,
                field=rule.field,
                value=rule.value,
                weight=rule.weight,
                operator=rule.operator,
                description=rule.description
            )
            for rule in business_rules
        ]
        
        # Apply business rules
        filtered_results = await search_service.apply_business_rules(
            search_results, rules
        )
        
        # Convert back to response format
        return [
            SearchResultResponse(
                id=result.id,
                score=result.score,
                metadata=result.metadata
            )
            for result in filtered_results
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Business rules application failed: {str(e)}")


@router.get("/models/reranking")
async def get_reranking_models():
    """Get available reranking models."""
    return {
        "models": [
            {
                "name": "cross-encoder/ms-marco-MiniLM-L-6-v2",
                "type": "cross-encoder",
                "description": "Microsoft MARCO cross-encoder for reranking"
            },
            {
                "name": "cross-encoder/ms-marco-MiniLM-L-12-v2",
                "type": "cross-encoder",
                "description": "Larger Microsoft MARCO cross-encoder"
            },
            {
                "name": "sentence-transformers/all-MiniLM-L6-v2",
                "type": "bi-encoder",
                "description": "Sentence transformer for bi-encoder reranking"
            }
        ]
    }


@router.get("/strategies/mmr")
async def get_mmr_strategies():
    """Get available MMR strategies."""
    return {
        "strategies": [
            {
                "name": "diversity",
                "description": "Maximize diversity among results"
            },
            {
                "name": "relevance",
                "description": "Maximize relevance to query"
            },
            {
                "name": "balanced",
                "description": "Balance diversity and relevance"
            }
        ]
    }


@router.get("/rules/business")
async def get_business_rule_types():
    """Get available business rule types."""
    return {
        "rule_types": [
            {
                "name": "boost",
                "description": "Increase score for matching items"
            },
            {
                "name": "penalty",
                "description": "Decrease score for matching items"
            },
            {
                "name": "filter",
                "description": "Filter out non-matching items"
            },
            {
                "name": "requirement",
                "description": "Require items to match this rule"
            }
        ],
        "operators": [
            "eq", "gt", "lt", "gte", "lte", "in", "not_in", "contains"
        ]
    }
