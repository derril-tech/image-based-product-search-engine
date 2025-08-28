"""Search service for advanced search functionality."""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid
import numpy as np
import time

from ..models.search_models import (
    SearchRequest, SearchResponse, SearchResult, SearchType, RerankModel,
    MMRStrategy, BusinessRule, RerankRequest, RerankResponse, MMRRequest,
    MMRResponse, SearchJobStatus, SearchConfig, SearchStats, SearchAnalytics,
    SearchSuggestion, SearchSuggestionsResponse, SearchFacet, SearchFacetsResponse,
    SearchFilter, SearchQuery
)
from ..services.index_service import IndexService
from ..services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class SearchService:
    """Service for advanced search functionality."""
    
    def __init__(self):
        self.index_service = IndexService()
        self.embedding_service = EmbeddingService()
        self.active_jobs: Dict[str, SearchJobStatus] = {}
        self.business_rules: Dict[str, BusinessRule] = {}
        self.search_stats: List[SearchAnalytics] = []
        
        # Default search configurations
        self.default_configs = {
            SearchType.IMAGE: SearchConfig(
                ann_top_k=100,
                rerank_enabled=True,
                rerank_model=RerankModel.CROSS_ENCODER,
                rerank_top_k=50,
                mmr_enabled=False
            ),
            SearchType.TEXT: SearchConfig(
                ann_top_k=100,
                rerank_enabled=True,
                rerank_model=RerankModel.BI_ENCODER,
                rerank_top_k=50,
                mmr_enabled=True,
                mmr_lambda=0.3
            ),
            SearchType.MULTIMODAL: SearchConfig(
                ann_top_k=150,
                rerank_enabled=True,
                rerank_model=RerankModel.CROSS_ENCODER,
                rerank_top_k=75,
                mmr_enabled=True,
                mmr_lambda=0.4
            ),
            SearchType.HYBRID: SearchConfig(
                ann_top_k=200,
                rerank_enabled=True,
                rerank_model=RerankModel.CROSS_ENCODER,
                rerank_top_k=100,
                mmr_enabled=True,
                mmr_lambda=0.5
            )
        }
    
    async def search(self, request: SearchRequest) -> SearchResponse:
        """Perform advanced search with reranking, MMR, and business rules."""
        start_time = time.time()
        
        try:
            logger.info(f"Starting search: type={request.search_type}, collection={request.collection_name}")
            
            # Step 1: ANN Search
            ann_start = time.time()
            candidates = await self._perform_ann_search(request)
            ann_time = (time.time() - ann_start) * 1000
            
            # Step 2: Apply business rules
            business_start = time.time()
            candidates = await self._apply_business_rules(candidates, request.business_rules)
            business_time = (time.time() - business_start) * 1000
            
            # Step 3: Reranking
            rerank_time = None
            if request.enable_rerank and candidates:
                rerank_start = time.time()
                candidates = await self._rerank_results(request, candidates)
                rerank_time = (time.time() - rerank_start) * 1000
            
            # Step 4: MMR (Maximal Marginal Relevance)
            mmr_time = None
            if request.enable_mmr and candidates:
                mmr_start = time.time()
                candidates = await self._apply_mmr(request, candidates)
                mmr_time = (time.time() - mmr_start) * 1000
            
            # Step 5: Final processing
            final_results = candidates[:request.top_k] if candidates else []
            
            # Calculate total time
            total_time = (time.time() - start_time) * 1000
            
            # Create response
            response = SearchResponse(
                results=final_results,
                total_results=len(final_results),
                search_time_ms=total_time,
                rerank_time_ms=rerank_time,
                mmr_time_ms=mmr_time,
                collection_name=request.collection_name,
                search_type=request.search_type,
                query_info={"query_type": type(request.query).__name__},
                ann_time_ms=ann_time,
                total_time_ms=total_time,
                applied_business_rules=[rule["name"] for rule in request.business_rules],
                applied_filters=list(request.filters.keys())
            )
            
            # Log analytics
            await self._log_search_analytics(request, response, ann_time, rerank_time, mmr_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise
    
    async def _perform_ann_search(self, request: SearchRequest) -> List[SearchResult]:
        """Perform approximate nearest neighbor search."""
        try:
            # Convert query to embedding if needed
            if isinstance(request.query, str):
                # Generate embedding for text query
                embedding_config = self.embedding_service.model_dimensions.get(
                    "clip-vit-b-32", 512
                )
                query_embedding = await self.embedding_service.generate_text_embedding(
                    request.query, embedding_config
                )
                query_vector = query_embedding.embeddings[0].vector
            else:
                query_vector = request.query
            
            # Perform vector search
            search_request = type('SearchRequest', (), {
                'collection_name': request.collection_name,
                'organization_id': request.organization_id,
                'query_vectors': [query_vector],
                'top_k': request.top_k,
                'search_params': request.search_params,
                'filter_expr': request.filter_expr
            })()
            
            search_response = await self.index_service.search_vectors(search_request)
            
            # Convert to SearchResult objects
            results = []
            for i, result in enumerate(search_response.results[0]):
                search_result = SearchResult(
                    id=result.id,
                    score=result.score,
                    distance=result.distance,
                    rank=i + 1,
                    metadata=result.metadata
                )
                results.append(search_result)
            
            return results
            
        except Exception as e:
            logger.error(f"ANN search failed: {str(e)}")
            raise
    
    async def _apply_business_rules(self, candidates: List[SearchResult], 
                                  business_rules: List[Dict[str, Any]]) -> List[SearchResult]:
        """Apply business rules to search results."""
        if not business_rules:
            return candidates
        
        try:
            for candidate in candidates:
                candidate.business_rule_boosts = {}
                candidate.business_rule_penalties = {}
                
                for rule in business_rules:
                    rule_id = rule.get("rule_id")
                    rule_type = rule.get("type")
                    
                    if rule_id in self.business_rules:
                        business_rule = self.business_rules[rule_id]
                        
                        # Check if rule applies to this candidate
                        if await self._evaluate_rule_conditions(candidate, business_rule.conditions):
                            if business_rule.rule_type.value == "boost" and business_rule.boost_factor:
                                candidate.business_rule_boosts[rule_id] = business_rule.boost_factor
                                candidate.score *= (1 + business_rule.boost_factor)
                            
                            elif business_rule.rule_type.value == "penalty" and business_rule.penalty_factor:
                                candidate.business_rule_penalties[rule_id] = business_rule.penalty_factor
                                candidate.score *= (1 - business_rule.penalty_factor)
            
            # Re-sort by updated scores
            candidates.sort(key=lambda x: x.score, reverse=True)
            
            return candidates
            
        except Exception as e:
            logger.error(f"Business rules application failed: {str(e)}")
            return candidates
    
    async def _evaluate_rule_conditions(self, candidate: SearchResult, 
                                      conditions: Dict[str, Any]) -> bool:
        """Evaluate if business rule conditions apply to a candidate."""
        try:
            for field, condition in conditions.items():
                if field in candidate.metadata:
                    value = candidate.metadata[field]
                    
                    if isinstance(condition, dict):
                        operator = condition.get("operator", "eq")
                        expected_value = condition.get("value")
                        
                        if operator == "eq" and value != expected_value:
                            return False
                        elif operator == "ne" and value == expected_value:
                            return False
                        elif operator == "gt" and value <= expected_value:
                            return False
                        elif operator == "lt" and value >= expected_value:
                            return False
                        elif operator == "gte" and value < expected_value:
                            return False
                        elif operator == "lte" and value > expected_value:
                            return False
                        elif operator == "in" and value not in expected_value:
                            return False
                        elif operator == "not_in" and value in expected_value:
                            return False
                    else:
                        # Simple equality check
                        if value != condition:
                            return False
            
            return True
            
        except Exception as e:
            logger.error(f"Rule condition evaluation failed: {str(e)}")
            return False
    
    async def _rerank_results(self, request: SearchRequest, 
                            candidates: List[SearchResult]) -> List[SearchResult]:
        """Rerank search results using cross-encoder or bi-encoder."""
        try:
            if not candidates:
                return candidates
            
            # Create rerank request
            rerank_request = RerankRequest(
                query=request.query,
                candidates=candidates[:request.rerank_top_k],
                model=request.rerank_model or RerankModel.CROSS_ENCODER,
                top_k=request.top_k,
                batch_size=16
            )
            
            # Perform reranking
            reranked_results = await self._perform_reranking(rerank_request)
            
            # Update original candidates with rerank scores
            for i, result in enumerate(reranked_results):
                if i < len(candidates):
                    candidates[i].rerank_score = result.score
                    candidates[i].rerank_rank = i + 1
                    candidates[i].score = result.score  # Use rerank score as final score
            
            # Re-sort by rerank scores
            candidates.sort(key=lambda x: x.rerank_score or x.score, reverse=True)
            
            return candidates
            
        except Exception as e:
            logger.error(f"Reranking failed: {str(e)}")
            return candidates
    
    async def _perform_reranking(self, request: RerankRequest) -> List[SearchResult]:
        """Perform actual reranking using specified model."""
        try:
            # Mock reranking implementation
            # In real implementation, would use actual reranking models
            
            reranked_results = []
            for i, candidate in enumerate(request.candidates):
                # Simulate reranking by adjusting scores
                if request.model == RerankModel.CROSS_ENCODER:
                    # Cross-encoder typically provides more accurate scores
                    rerank_score = candidate.score * (1 + np.random.normal(0, 0.1))
                else:
                    # Bi-encoder scores
                    rerank_score = candidate.score * (1 + np.random.normal(0, 0.05))
                
                reranked_result = SearchResult(
                    id=candidate.id,
                    score=rerank_score,
                    distance=candidate.distance,
                    rank=i + 1,
                    metadata=candidate.metadata,
                    rerank_score=rerank_score,
                    rerank_rank=i + 1
                )
                reranked_results.append(reranked_result)
            
            # Sort by rerank score
            reranked_results.sort(key=lambda x: x.rerank_score, reverse=True)
            
            return reranked_results
            
        except Exception as e:
            logger.error(f"Reranking model execution failed: {str(e)}")
            return request.candidates
    
    async def _apply_mmr(self, request: SearchRequest, 
                        candidates: List[SearchResult]) -> List[SearchResult]:
        """Apply Maximal Marginal Relevance for diversity."""
        try:
            if not candidates:
                return candidates
            
            # Create MMR request
            mmr_request = MMRRequest(
                query=request.query,
                candidates=candidates,
                strategy=request.mmr_strategy,
                lambda_param=request.mmr_lambda,
                top_k=request.top_k
            )
            
            # Perform MMR
            mmr_results = await self._perform_mmr(mmr_request)
            
            return mmr_results
            
        except Exception as e:
            logger.error(f"MMR application failed: {str(e)}")
            return candidates
    
    async def _perform_mmr(self, request: MMRRequest) -> List[SearchResult]:
        """Perform Maximal Marginal Relevance calculation."""
        try:
            if not request.candidates:
                return []
            
            # Start with the highest scoring candidate
            selected = [request.candidates[0]]
            remaining = request.candidates[1:]
            
            # Calculate diversity scores for remaining candidates
            while remaining and len(selected) < (request.top_k or len(request.candidates)):
                max_mmr_score = -1
                best_candidate = None
                best_index = -1
                
                for i, candidate in enumerate(remaining):
                    # Calculate relevance score (original score)
                    relevance_score = candidate.score
                    
                    # Calculate diversity score (average distance from selected)
                    diversity_score = 0
                    for selected_candidate in selected:
                        # Calculate distance between embeddings (simplified)
                        distance = self._calculate_diversity_distance(candidate, selected_candidate)
                        diversity_score += distance
                    
                    if selected:
                        diversity_score /= len(selected)
                    
                    # Calculate MMR score
                    mmr_score = (request.lambda_param * relevance_score + 
                               (1 - request.lambda_param) * diversity_score)
                    
                    if mmr_score > max_mmr_score:
                        max_mmr_score = mmr_score
                        best_candidate = candidate
                        best_index = i
                
                if best_candidate:
                    # Update candidate with MMR info
                    best_candidate.mmr_score = max_mmr_score
                    best_candidate.diversity_score = diversity_score
                    
                    selected.append(best_candidate)
                    remaining.pop(best_index)
                else:
                    break
            
            return selected
            
        except Exception as e:
            logger.error(f"MMR calculation failed: {str(e)}")
            return request.candidates
    
    def _calculate_diversity_distance(self, candidate1: SearchResult, 
                                    candidate2: SearchResult) -> float:
        """Calculate diversity distance between two candidates."""
        try:
            # Use metadata-based diversity if embeddings not available
            if candidate1.embedding and candidate2.embedding:
                # Calculate cosine distance between embeddings
                vec1 = np.array(candidate1.embedding)
                vec2 = np.array(candidate2.embedding)
                
                # Normalize vectors
                vec1 = vec1 / np.linalg.norm(vec1)
                vec2 = vec2 / np.linalg.norm(vec2)
                
                # Calculate cosine distance
                distance = 1 - np.dot(vec1, vec2)
                return distance
            else:
                # Fallback to metadata-based diversity
                diversity_score = 0
                common_fields = set(candidate1.metadata.keys()) & set(candidate2.metadata.keys())
                
                for field in common_fields:
                    if candidate1.metadata[field] != candidate2.metadata[field]:
                        diversity_score += 1
                
                return diversity_score / max(len(common_fields), 1)
                
        except Exception as e:
            logger.error(f"Diversity distance calculation failed: {str(e)}")
            return 0.5  # Default diversity score
    
    async def _log_search_analytics(self, request: SearchRequest, 
                                  response: SearchResponse, ann_time: float,
                                  rerank_time: Optional[float], mmr_time: Optional[float]):
        """Log search analytics for monitoring."""
        try:
            analytics = SearchAnalytics(
                query_id=str(uuid.uuid4()),
                search_type=request.search_type,
                collection_name=request.collection_name,
                organization_id=request.organization_id,
                query_text=request.query if isinstance(request.query, str) else None,
                query_embedding_dim=len(request.query) if isinstance(request.query, list) else None,
                ann_time_ms=ann_time,
                rerank_time_ms=rerank_time,
                mmr_time_ms=mmr_time,
                total_time_ms=response.total_time_ms,
                total_candidates=len(response.results),
                total_results=response.total_results,
                avg_relevance_score=np.mean([r.score for r in response.results]) if response.results else 0,
                avg_diversity_score=np.mean([r.diversity_score for r in response.results if r.diversity_score]) if response.results else None,
                timestamp=datetime.utcnow()
            )
            
            self.search_stats.append(analytics)
            
            # Keep only last 1000 analytics entries
            if len(self.search_stats) > 1000:
                self.search_stats = self.search_stats[-1000:]
                
        except Exception as e:
            logger.error(f"Analytics logging failed: {str(e)}")
    
    async def get_search_suggestions(self, query: str, collection_name: str,
                                   limit: int = 10) -> SearchSuggestionsResponse:
        """Get search suggestions for autocomplete."""
        try:
            # Mock suggestions implementation
            suggestions = []
            
            # Generate mock suggestions based on query
            mock_suggestions = [
                f"{query} product",
                f"{query} item",
                f"{query} category",
                f"similar to {query}",
                f"related {query}"
            ]
            
            for i, suggestion in enumerate(mock_suggestions[:limit]):
                suggestion_obj = SearchSuggestion(
                    suggestion=suggestion,
                    type="query",
                    score=1.0 - (i * 0.1),
                    metadata={"source": "mock", "frequency": 100 - i * 10}
                )
                suggestions.append(suggestion_obj)
            
            return SearchSuggestionsResponse(
                suggestions=suggestions,
                query=query,
                total_suggestions=len(suggestions),
                processing_time_ms=10.0
            )
            
        except Exception as e:
            logger.error(f"Search suggestions failed: {str(e)}")
            raise
    
    async def get_search_facets(self, collection_name: str, 
                               fields: List[str]) -> SearchFacetsResponse:
        """Get search facets for filtering."""
        try:
            # Mock facets implementation
            facets = []
            
            for field in fields:
                # Generate mock facet values
                facet_values = []
                for i in range(5):
                    facet_values.append({
                        "value": f"{field}_value_{i}",
                        "count": 100 - i * 20,
                        "score": 1.0 - i * 0.1
                    })
                
                facet = SearchFacet(
                    field=field,
                    values=facet_values,
                    total_count=sum(v["count"] for v in facet_values)
                )
                facets.append(facet)
            
            return SearchFacetsResponse(
                facets=facets,
                total_facets=len(facets),
                processing_time_ms=15.0
            )
            
        except Exception as e:
            logger.error(f"Search facets failed: {str(e)}")
            raise
    
    async def get_search_stats(self, start_time: datetime, 
                             end_time: datetime) -> SearchStats:
        """Get search statistics for the specified time range."""
        try:
            # Filter analytics by time range
            filtered_stats = [
                stat for stat in self.search_stats
                if start_time <= stat.timestamp <= end_time
            ]
            
            if not filtered_stats:
                return SearchStats(
                    total_searches=0,
                    avg_search_time_ms=0,
                    p50_search_time_ms=0,
                    p95_search_time_ms=0,
                    p99_search_time_ms=0,
                    avg_result_relevance=0,
                    start_time=start_time,
                    end_time=end_time
                )
            
            # Calculate statistics
            search_times = [stat.total_time_ms for stat in filtered_stats]
            relevance_scores = [stat.avg_relevance_score for stat in filtered_stats]
            
            # Group by search type and collection
            searches_by_type = {}
            searches_by_collection = {}
            
            for stat in filtered_stats:
                searches_by_type[stat.search_type.value] = searches_by_type.get(stat.search_type.value, 0) + 1
                searches_by_collection[stat.collection_name] = searches_by_collection.get(stat.collection_name, 0) + 1
            
            return SearchStats(
                total_searches=len(filtered_stats),
                avg_search_time_ms=np.mean(search_times),
                avg_rerank_time_ms=np.mean([s.rerank_time_ms for s in filtered_stats if s.rerank_time_ms]),
                avg_mmr_time_ms=np.mean([s.mmr_time_ms for s in filtered_stats if s.mmr_time_ms]),
                p50_search_time_ms=np.percentile(search_times, 50),
                p95_search_time_ms=np.percentile(search_times, 95),
                p99_search_time_ms=np.percentile(search_times, 99),
                avg_result_relevance=np.mean(relevance_scores),
                avg_result_diversity=np.mean([s.avg_diversity_score for s in filtered_stats if s.avg_diversity_score]),
                searches_by_type=searches_by_type,
                searches_by_collection=searches_by_collection,
                start_time=start_time,
                end_time=end_time
            )
            
        except Exception as e:
            logger.error(f"Search stats calculation failed: {str(e)}")
            raise
    
    async def add_business_rule(self, rule: BusinessRule):
        """Add a business rule."""
        try:
            self.business_rules[rule.rule_id] = rule
            logger.info(f"Added business rule: {rule.rule_id}")
            
        except Exception as e:
            logger.error(f"Failed to add business rule: {str(e)}")
            raise
    
    async def remove_business_rule(self, rule_id: str):
        """Remove a business rule."""
        try:
            if rule_id in self.business_rules:
                del self.business_rules[rule_id]
                logger.info(f"Removed business rule: {rule_id}")
            else:
                raise ValueError(f"Business rule {rule_id} not found")
                
        except Exception as e:
            logger.error(f"Failed to remove business rule: {str(e)}")
            raise
    
    async def list_business_rules(self) -> List[BusinessRule]:
        """List all business rules."""
        return list(self.business_rules.values())
    
    async def get_business_rule(self, rule_id: str) -> BusinessRule:
        """Get a specific business rule."""
        if rule_id not in self.business_rules:
            raise ValueError(f"Business rule {rule_id} not found")
        
        return self.business_rules[rule_id]
