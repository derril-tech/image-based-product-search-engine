# Created automatically by Cursor AI (2024-12-19)

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import torch
from transformers import AutoTokenizer, AutoModel
from pymilvus import Collection, connections
from .milvus_service import MilvusService
from .embedding_service import EmbeddingService
from ..config import get_settings

logger = logging.getLogger(__name__)


class RerankingModel(str, Enum):
    CROSS_ENCODER = "cross-encoder"
    BI_ENCODER = "bi-encoder"
    CUSTOM = "custom"


class MMRStrategy(str, Enum):
    DIVERSITY = "diversity"
    RELEVANCE = "relevance"
    BALANCED = "balanced"


class BusinessRuleType(str, Enum):
    BOOST = "boost"
    FILTER = "filter"
    PENALTY = "penalty"
    REQUIREMENT = "requirement"


@dataclass
class BusinessRule:
    rule_type: BusinessRuleType
    field: str
    value: Any
    weight: float = 1.0
    operator: str = "eq"  # eq, gt, lt, gte, lte, in, not_in, contains
    description: str = ""


@dataclass
class SearchResult:
    id: str
    score: float
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None


@dataclass
class RerankingConfig:
    model: RerankingModel = RerankingModel.CROSS_ENCODER
    model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    top_k: int = 100
    batch_size: int = 32
    device: str = "cpu"


@dataclass
class MMRConfig:
    strategy: MMRStrategy = MMRStrategy.BALANCED
    lambda_param: float = 0.5
    diversity_threshold: float = 0.3
    max_results: int = 20


class AdvancedSearchService:
    def __init__(self):
        self.settings = get_settings()
        self.milvus_service = MilvusService()
        self.embedding_service = EmbeddingService()
        self.reranking_model = None
        self.tokenizer = None
        self._init_reranking_model()
    
    def _init_reranking_model(self):
        """Initialize reranking model based on configuration."""
        try:
            if self.settings.ENABLE_RERANKING:
                if self.settings.RERANKING_MODEL == RerankingModel.CROSS_ENCODER:
                    self.tokenizer = AutoTokenizer.from_pretrained(self.settings.RERANKING_MODEL_NAME)
                    self.reranking_model = AutoModel.from_pretrained(self.settings.RERANKING_MODEL_NAME)
                    if torch.cuda.is_available():
                        self.reranking_model = self.reranking_model.cuda()
                    self.reranking_model.eval()
                    logger.info(f"Initialized reranking model: {self.settings.RERANKING_MODEL_NAME}")
        except Exception as e:
            logger.error(f"Failed to initialize reranking model: {e}")
    
    async def search_with_reranking(
        self,
        query_embedding: np.ndarray,
        collection_name: str,
        top_k: int = 100,
        reranking_config: Optional[RerankingConfig] = None,
        business_rules: Optional[List[BusinessRule]] = None
    ) -> List[SearchResult]:
        """Perform search with reranking."""
        # Initial vector search
        initial_results = await self._vector_search(
            query_embedding, collection_name, top_k, business_rules
        )
        
        if not initial_results:
            return []
        
        # Apply reranking if configured
        if reranking_config and self.reranking_model:
            reranked_results = await self._rerank_results(
                initial_results, query_embedding, reranking_config
            )
            return reranked_results
        
        return initial_results
    
    async def search_with_mmr(
        self,
        query_embedding: np.ndarray,
        collection_name: str,
        mmr_config: MMRConfig,
        business_rules: Optional[List[BusinessRule]] = None
    ) -> List[SearchResult]:
        """Perform search with Maximal Marginal Relevance for diversity."""
        # Get initial results
        initial_results = await self._vector_search(
            query_embedding, collection_name, mmr_config.max_results * 2, business_rules
        )
        
        if not initial_results:
            return []
        
        # Apply MMR algorithm
        mmr_results = self._apply_mmr(
            initial_results, query_embedding, mmr_config
        )
        
        return mmr_results[:mmr_config.max_results]
    
    async def _vector_search(
        self,
        query_embedding: np.ndarray,
        collection_name: str,
        top_k: int,
        business_rules: Optional[List[BusinessRule]] = None
    ) -> List[SearchResult]:
        """Perform initial vector search with business rules."""
        try:
            # Build search parameters
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            # Apply business rules to build filter expression
            filter_expr = self._build_filter_expression(business_rules)
            
            # Perform search
            results = await self.milvus_service.search(
                collection_name=collection_name,
                query_vectors=[query_embedding.tolist()],
                top_k=top_k,
                search_params=search_params,
                filter_expr=filter_expr
            )
            
            # Convert to SearchResult objects
            search_results = []
            for result in results:
                search_results.append(SearchResult(
                    id=str(result.id),
                    score=result.score,
                    metadata=result.entity.get('metadata', {}),
                    embedding=np.array(result.entity.get('embedding', []))
                ))
            
            return search_results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    async def _rerank_results(
        self,
        results: List[SearchResult],
        query_embedding: np.ndarray,
        config: RerankingConfig
    ) -> List[SearchResult]:
        """Rerank results using cross-encoder or bi-encoder."""
        try:
            if config.model == RerankingModel.CROSS_ENCODER:
                return await self._cross_encoder_rerank(results, config)
            elif config.model == RerankingModel.BI_ENCODER:
                return await self._bi_encoder_rerank(results, query_embedding, config)
            else:
                return results
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            return results
    
    async def _cross_encoder_rerank(
        self,
        results: List[SearchResult],
        config: RerankingConfig
    ) -> List[SearchResult]:
        """Rerank using cross-encoder model."""
        if not self.reranking_model or not self.tokenizer:
            return results
        
        try:
            # Prepare pairs for cross-encoder
            pairs = []
            for result in results[:config.top_k]:
                # Create text representation from metadata
                text = self._metadata_to_text(result.metadata)
                pairs.append(text)
            
            # Batch process
            reranked_scores = []
            for i in range(0, len(pairs), config.batch_size):
                batch_pairs = pairs[i:i + config.batch_size]
                
                # Tokenize
                inputs = self.tokenizer(
                    batch_pairs,
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors="pt"
                )
                
                if torch.cuda.is_available():
                    inputs = {k: v.cuda() for k, v in inputs.items()}
                
                # Get scores
                with torch.no_grad():
                    outputs = self.reranking_model(**inputs)
                    scores = torch.softmax(outputs.logits, dim=1)[:, 1].cpu().numpy()
                    reranked_scores.extend(scores)
            
            # Update scores and sort
            for i, result in enumerate(results[:config.top_k]):
                result.score = reranked_scores[i]
            
            # Sort by new scores
            results[:config.top_k] = sorted(
                results[:config.top_k], key=lambda x: x.score, reverse=True
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Cross-encoder reranking failed: {e}")
            return results
    
    async def _bi_encoder_rerank(
        self,
        results: List[SearchResult],
        query_embedding: np.ndarray,
        config: RerankingConfig
    ) -> List[SearchResult]:
        """Rerank using bi-encoder model."""
        try:
            # Get embeddings for result texts
            result_texts = [self._metadata_to_text(r.metadata) for r in results[:config.top_k]]
            result_embeddings = await self.embedding_service.encode_texts(result_texts)
            
            # Calculate similarities
            similarities = cosine_similarity([query_embedding], result_embeddings)[0]
            
            # Update scores
            for i, result in enumerate(results[:config.top_k]):
                result.score = similarities[i]
            
            # Sort by new scores
            results[:config.top_k] = sorted(
                results[:config.top_k], key=lambda x: x.score, reverse=True
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Bi-encoder reranking failed: {e}")
            return results
    
    def _apply_mmr(
        self,
        results: List[SearchResult],
        query_embedding: np.ndarray,
        config: MMRConfig
    ) -> List[SearchResult]:
        """Apply Maximal Marginal Relevance algorithm."""
        if not results:
            return []
        
        # Initialize selected results
        selected = [results[0]]
        remaining = results[1:]
        
        while len(selected) < config.max_results and remaining:
            # Calculate MMR scores
            mmr_scores = []
            for result in remaining:
                # Relevance to query
                relevance = result.score
                
                # Diversity from selected results
                diversity = 0.0
                if selected:
                    similarities = []
                    for selected_result in selected:
                        if selected_result.embedding is not None and result.embedding is not None:
                            sim = cosine_similarity(
                                [selected_result.embedding], [result.embedding]
                            )[0][0]
                            similarities.append(sim)
                    
                    if similarities:
                        diversity = 1.0 - max(similarities)
                
                # MMR score based on strategy
                if config.strategy == MMRStrategy.DIVERSITY:
                    mmr_score = diversity
                elif config.strategy == MMRStrategy.RELEVANCE:
                    mmr_score = relevance
                else:  # BALANCED
                    mmr_score = config.lambda_param * relevance + (1 - config.lambda_param) * diversity
                
                mmr_scores.append((mmr_score, result))
            
            # Select result with highest MMR score
            if mmr_scores:
                best_score, best_result = max(mmr_scores, key=lambda x: x[0])
                
                # Check diversity threshold
                if config.strategy == MMRStrategy.DIVERSITY or best_score >= config.diversity_threshold:
                    selected.append(best_result)
                    remaining.remove(best_result)
                else:
                    break
            else:
                break
        
        return selected
    
    def _build_filter_expression(self, business_rules: Optional[List[BusinessRule]]) -> str:
        """Build Milvus filter expression from business rules."""
        if not business_rules:
            return ""
        
        filter_parts = []
        for rule in business_rules:
            if rule.rule_type == BusinessRuleType.FILTER:
                filter_expr = self._build_single_filter(rule)
                if filter_expr:
                    filter_parts.append(filter_expr)
        
        if filter_parts:
            return " and ".join(filter_parts)
        return ""
    
    def _build_single_filter(self, rule: BusinessRule) -> str:
        """Build single filter expression for a business rule."""
        field = rule.field
        value = rule.value
        operator = rule.operator
        
        if operator == "eq":
            return f'{field} == "{value}"'
        elif operator == "gt":
            return f'{field} > {value}'
        elif operator == "lt":
            return f'{field} < {value}'
        elif operator == "gte":
            return f'{field} >= {value}'
        elif operator == "lte":
            return f'{field} <= {value}'
        elif operator == "in":
            if isinstance(value, list):
                values_str = '", "'.join(str(v) for v in value)
                return f'{field} in ["{values_str}"]'
        elif operator == "not_in":
            if isinstance(value, list):
                values_str = '", "'.join(str(v) for v in value)
                return f'{field} not in ["{values_str}"]'
        elif operator == "contains":
            return f'{field} like "%{value}%"'
        
        return ""
    
    def _metadata_to_text(self, metadata: Dict[str, Any]) -> str:
        """Convert metadata to text representation for reranking."""
        text_parts = []
        
        # Add title/name
        if 'title' in metadata:
            text_parts.append(str(metadata['title']))
        elif 'name' in metadata:
            text_parts.append(str(metadata['name']))
        
        # Add description
        if 'description' in metadata:
            text_parts.append(str(metadata['description']))
        
        # Add category/tags
        if 'category' in metadata:
            text_parts.append(str(metadata['category']))
        if 'tags' in metadata and isinstance(metadata['tags'], list):
            text_parts.extend(str(tag) for tag in metadata['tags'])
        
        # Add brand
        if 'brand' in metadata:
            text_parts.append(str(metadata['brand']))
        
        return " ".join(text_parts)
    
    async def apply_business_rules(
        self,
        results: List[SearchResult],
        business_rules: List[BusinessRule]
    ) -> List[SearchResult]:
        """Apply business rules to search results."""
        if not business_rules:
            return results
        
        filtered_results = []
        
        for result in results:
            score_modifier = 0.0
            include_result = True
            
            for rule in business_rules:
                if rule.rule_type == BusinessRuleType.BOOST:
                    if self._evaluate_rule(result.metadata, rule):
                        score_modifier += rule.weight
                
                elif rule.rule_type == BusinessRuleType.PENALTY:
                    if self._evaluate_rule(result.metadata, rule):
                        score_modifier -= rule.weight
                
                elif rule.rule_type == BusinessRuleType.FILTER:
                    if not self._evaluate_rule(result.metadata, rule):
                        include_result = False
                        break
                
                elif rule.rule_type == BusinessRuleType.REQUIREMENT:
                    if not self._evaluate_rule(result.metadata, rule):
                        include_result = False
                        break
            
            if include_result:
                result.score += score_modifier
                filtered_results.append(result)
        
        # Re-sort by modified scores
        filtered_results.sort(key=lambda x: x.score, reverse=True)
        return filtered_results
    
    def _evaluate_rule(self, metadata: Dict[str, Any], rule: BusinessRule) -> bool:
        """Evaluate if a business rule applies to a result."""
        if rule.field not in metadata:
            return False
        
        field_value = metadata[rule.field]
        rule_value = rule.value
        operator = rule.operator
        
        if operator == "eq":
            return field_value == rule_value
        elif operator == "gt":
            return field_value > rule_value
        elif operator == "lt":
            return field_value < rule_value
        elif operator == "gte":
            return field_value >= rule_value
        elif operator == "lte":
            return field_value <= rule_value
        elif operator == "in":
            return field_value in rule_value
        elif operator == "not_in":
            return field_value not in rule_value
        elif operator == "contains":
            return str(rule_value).lower() in str(field_value).lower()
        
        return False
