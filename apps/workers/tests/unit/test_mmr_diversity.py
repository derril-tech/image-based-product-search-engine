# Created automatically by Cursor AI (2024-12-19)

import pytest
import numpy as np
from unittest.mock import Mock
from ..src.services.advanced_search import AdvancedSearchService, MMRStrategy, MMRConfig


class TestMMRDiversity:
    """Test suite for MMR (Maximal Marginal Relevance) diversity functionality."""
    
    @pytest.fixture
    def advanced_search_service(self):
        """Create an advanced search service instance for testing."""
        return AdvancedSearchService()
    
    @pytest.fixture
    def sample_embeddings(self):
        """Create sample embeddings for testing."""
        # Create 10 embeddings with known similarity patterns
        np.random.seed(42)  # For reproducible tests
        embeddings = np.random.randn(10, 512).astype(np.float32)
        
        # Normalize embeddings
        for i in range(len(embeddings)):
            embeddings[i] = embeddings[i] / np.linalg.norm(embeddings[i])
        
        return embeddings
    
    @pytest.fixture
    def query_embedding(self):
        """Create a query embedding for testing."""
        np.random.seed(123)  # For reproducible tests
        embedding = np.random.randn(512).astype(np.float32)
        return embedding / np.linalg.norm(embedding)
    
    @pytest.fixture
    def sample_results(self, sample_embeddings):
        """Create sample search results for testing."""
        from ..src.services.advanced_search import SearchResult
        
        results = []
        for i, embedding in enumerate(sample_embeddings):
            result = SearchResult(
                id=f"result_{i}",
                score=0.9 - i * 0.05,  # Decreasing scores
                metadata={"title": f"Item {i}", "category": f"cat_{i % 3}"},
                embedding=embedding
            )
            results.append(result)
        
        return results
    
    def test_mmr_diversity_strategy(self, advanced_search_service, sample_results, query_embedding):
        """Test MMR diversity strategy."""
        config = MMRConfig(
            strategy=MMRStrategy.DIVERSITY,
            lambda_param=0.5,
            diversity_threshold=0.3,
            max_results=5
        )
        
        mmr_results = advanced_search_service._apply_mmr(sample_results, query_embedding, config)
        
        # Should return exactly max_results
        assert len(mmr_results) == 5
        
        # Should prioritize diversity over relevance
        # Check that results are different from each other
        embeddings = [result.embedding for result in mmr_results]
        similarities = []
        
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                similarity = np.dot(embeddings[i], embeddings[j])
                similarities.append(similarity)
        
        # Average similarity should be lower than random selection
        avg_similarity = np.mean(similarities)
        assert avg_similarity < 0.5  # Should be diverse
    
    def test_mmr_relevance_strategy(self, advanced_search_service, sample_results, query_embedding):
        """Test MMR relevance strategy."""
        config = MMRConfig(
            strategy=MMRStrategy.RELEVANCE,
            lambda_param=0.5,
            diversity_threshold=0.3,
            max_results=5
        )
        
        mmr_results = advanced_search_service._apply_mmr(sample_results, query_embedding, config)
        
        # Should return exactly max_results
        assert len(mmr_results) == 5
        
        # Should prioritize relevance over diversity
        # Results should be ordered by score (descending)
        scores = [result.score for result in mmr_results]
        assert scores == sorted(scores, reverse=True)
    
    def test_mmr_balanced_strategy(self, advanced_search_service, sample_results, query_embedding):
        """Test MMR balanced strategy."""
        config = MMRConfig(
            strategy=MMRStrategy.BALANCED,
            lambda_param=0.5,
            diversity_threshold=0.3,
            max_results=5
        )
        
        mmr_results = advanced_search_service._apply_mmr(sample_results, query_embedding, config)
        
        # Should return exactly max_results
        assert len(mmr_results) == 5
        
        # Should balance diversity and relevance
        # Check that it's not purely by score order
        scores = [result.score for result in mmr_results]
        original_scores = [result.score for result in sample_results[:5]]
        
        # Should not be identical to pure score ordering
        assert scores != original_scores
    
    def test_mmr_lambda_parameter(self, advanced_search_service, sample_results, query_embedding):
        """Test MMR lambda parameter effect."""
        # Test with high lambda (more relevance)
        config_high = MMRConfig(
            strategy=MMRStrategy.BALANCED,
            lambda_param=0.9,
            diversity_threshold=0.3,
            max_results=5
        )
        
        results_high = advanced_search_service._apply_mmr(sample_results, query_embedding, config_high)
        
        # Test with low lambda (more diversity)
        config_low = MMRConfig(
            strategy=MMRStrategy.BALANCED,
            lambda_param=0.1,
            diversity_threshold=0.3,
            max_results=5
        )
        
        results_low = advanced_search_service._apply_mmr(sample_results, query_embedding, config_low)
        
        # High lambda should prioritize relevance more
        scores_high = [result.score for result in results_high]
        scores_low = [result.score for result in results_low]
        
        # High lambda should have higher average score
        avg_score_high = np.mean(scores_high)
        avg_score_low = np.mean(scores_low)
        
        assert avg_score_high >= avg_score_low
    
    def test_mmr_diversity_threshold(self, advanced_search_service, sample_results, query_embedding):
        """Test MMR diversity threshold."""
        # Test with high threshold
        config_high = MMRConfig(
            strategy=MMRStrategy.DIVERSITY,
            lambda_param=0.5,
            diversity_threshold=0.8,
            max_results=5
        )
        
        results_high = advanced_search_service._apply_mmr(sample_results, query_embedding, config_high)
        
        # Test with low threshold
        config_low = MMRConfig(
            strategy=MMRStrategy.DIVERSITY,
            lambda_param=0.5,
            diversity_threshold=0.1,
            max_results=5
        )
        
        results_low = advanced_search_service._apply_mmr(sample_results, query_embedding, config_low)
        
        # High threshold should result in fewer results (more strict diversity)
        assert len(results_high) <= len(results_low)
    
    def test_mmr_max_results_limit(self, advanced_search_service, sample_results, query_embedding):
        """Test MMR max results limit."""
        config = MMRConfig(
            strategy=MMRStrategy.BALANCED,
            lambda_param=0.5,
            diversity_threshold=0.3,
            max_results=3
        )
        
        mmr_results = advanced_search_service._apply_mmr(sample_results, query_embedding, config)
        
        # Should not exceed max_results
        assert len(mmr_results) <= 3
        
        # Should return exactly max_results if enough candidates
        assert len(mmr_results) == 3
    
    def test_mmr_empty_results(self, advanced_search_service, query_embedding):
        """Test MMR with empty results."""
        config = MMRConfig(
            strategy=MMRStrategy.BALANCED,
            lambda_param=0.5,
            diversity_threshold=0.3,
            max_results=5
        )
        
        mmr_results = advanced_search_service._apply_mmr([], query_embedding, config)
        
        # Should return empty list
        assert len(mmr_results) == 0
    
    def test_mmr_single_result(self, advanced_search_service, sample_results, query_embedding):
        """Test MMR with single result."""
        config = MMRConfig(
            strategy=MMRStrategy.BALANCED,
            lambda_param=0.5,
            diversity_threshold=0.3,
            max_results=5
        )
        
        single_result = [sample_results[0]]
        mmr_results = advanced_search_service._apply_mmr(single_result, query_embedding, config)
        
        # Should return the single result
        assert len(mmr_results) == 1
        assert mmr_results[0].id == single_result[0].id
    
    def test_mmr_diversity_calculation(self, advanced_search_service, sample_results, query_embedding):
        """Test MMR diversity calculation."""
        config = MMRConfig(
            strategy=MMRStrategy.DIVERSITY,
            lambda_param=0.5,
            diversity_threshold=0.3,
            max_results=3
        )
        
        mmr_results = advanced_search_service._apply_mmr(sample_results, query_embedding, config)
        
        # Calculate diversity among selected results
        embeddings = [result.embedding for result in mmr_results]
        similarities = []
        
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                similarity = np.dot(embeddings[i], embeddings[j])
                similarities.append(similarity)
        
        # Should have low average similarity (high diversity)
        if similarities:
            avg_similarity = np.mean(similarities)
            assert avg_similarity < 0.7  # Should be diverse
    
    def test_mmr_relevance_calculation(self, advanced_search_service, sample_results, query_embedding):
        """Test MMR relevance calculation."""
        config = MMRConfig(
            strategy=MMRStrategy.RELEVANCE,
            lambda_param=0.5,
            diversity_threshold=0.3,
            max_results=3
        )
        
        mmr_results = advanced_search_service._apply_mmr(sample_results, query_embedding, config)
        
        # Should prioritize high scores
        scores = [result.score for result in mmr_results]
        original_scores = [result.score for result in sample_results[:3]]
        
        # Should select high-scoring results
        assert np.mean(scores) >= np.mean(original_scores) * 0.8
    
    def test_mmr_balanced_calculation(self, advanced_search_service, sample_results, query_embedding):
        """Test MMR balanced calculation."""
        config = MMRConfig(
            strategy=MMRStrategy.BALANCED,
            lambda_param=0.5,
            diversity_threshold=0.3,
            max_results=3
        )
        
        mmr_results = advanced_search_service._apply_mmr(sample_results, query_embedding, config)
        
        # Should balance both diversity and relevance
        embeddings = [result.embedding for result in mmr_results]
        scores = [result.score for result in mmr_results]
        
        # Check diversity
        similarities = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                similarity = np.dot(embeddings[i], embeddings[j])
                similarities.append(similarity)
        
        if similarities:
            avg_similarity = np.mean(similarities)
            # Should be more diverse than pure relevance but less than pure diversity
            assert avg_similarity < 0.8
        
        # Check relevance (should have reasonable scores)
        assert np.mean(scores) > 0.5
    
    def test_mmr_edge_cases(self, advanced_search_service, sample_results, query_embedding):
        """Test MMR edge cases."""
        # Test with very high max_results
        config = MMRConfig(
            strategy=MMRStrategy.BALANCED,
            lambda_param=0.5,
            diversity_threshold=0.3,
            max_results=100
        )
        
        mmr_results = advanced_search_service._apply_mmr(sample_results, query_embedding, config)
        
        # Should return all available results
        assert len(mmr_results) == len(sample_results)
        
        # Test with zero max_results
        config_zero = MMRConfig(
            strategy=MMRStrategy.BALANCED,
            lambda_param=0.5,
            diversity_threshold=0.3,
            max_results=0
        )
        
        mmr_results_zero = advanced_search_service._apply_mmr(sample_results, query_embedding, config_zero)
        
        # Should return empty list
        assert len(mmr_results_zero) == 0
    
    def test_mmr_performance(self, advanced_search_service, sample_results, query_embedding):
        """Test MMR performance."""
        import time
        
        config = MMRConfig(
            strategy=MMRStrategy.BALANCED,
            lambda_param=0.5,
            diversity_threshold=0.3,
            max_results=5
        )
        
        # Measure execution time
        start_time = time.time()
        for _ in range(100):
            advanced_search_service._apply_mmr(sample_results, query_embedding, config)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 100
        
        # Should be reasonably fast (less than 10ms per call)
        assert avg_time < 0.01
    
    def test_mmr_consistency(self, advanced_search_service, sample_results, query_embedding):
        """Test MMR consistency across multiple runs."""
        config = MMRConfig(
            strategy=MMRStrategy.BALANCED,
            lambda_param=0.5,
            diversity_threshold=0.3,
            max_results=5
        )
        
        # Run MMR multiple times
        results_list = []
        for _ in range(10):
            mmr_results = advanced_search_service._apply_mmr(sample_results, query_embedding, config)
            results_list.append([result.id for result in mmr_results])
        
        # Should produce consistent results
        first_result = results_list[0]
        for result in results_list[1:]:
            assert result == first_result
    
    def test_mmr_with_identical_embeddings(self, advanced_search_service, sample_results, query_embedding):
        """Test MMR with identical embeddings."""
        # Create results with identical embeddings
        identical_results = []
        for i, result in enumerate(sample_results[:5]):
            identical_result = Mock()
            identical_result.id = f"identical_{i}"
            identical_result.score = result.score
            identical_result.metadata = result.metadata
            identical_result.embedding = sample_results[0].embedding  # All identical
            identical_results.append(identical_result)
        
        config = MMRConfig(
            strategy=MMRStrategy.DIVERSITY,
            lambda_param=0.5,
            diversity_threshold=0.3,
            max_results=3
        )
        
        mmr_results = advanced_search_service._apply_mmr(identical_results, query_embedding, config)
        
        # Should still return results (based on scores when diversity is zero)
        assert len(mmr_results) > 0
    
    def test_mmr_with_none_embeddings(self, advanced_search_service, sample_results, query_embedding):
        """Test MMR with None embeddings."""
        # Create results with None embeddings
        none_embedding_results = []
        for i, result in enumerate(sample_results[:5]):
            none_result = Mock()
            none_result.id = f"none_{i}"
            none_result.score = result.score
            none_result.metadata = result.metadata
            none_result.embedding = None
            none_embedding_results.append(none_result)
        
        config = MMRConfig(
            strategy=MMRStrategy.DIVERSITY,
            lambda_param=0.5,
            diversity_threshold=0.3,
            max_results=3
        )
        
        # Should handle None embeddings gracefully
        mmr_results = advanced_search_service._apply_mmr(none_embedding_results, query_embedding, config)
        
        # Should still return results (based on scores)
        assert len(mmr_results) > 0
    
    def test_mmr_strategy_comparison(self, advanced_search_service, sample_results, query_embedding):
        """Test comparison between different MMR strategies."""
        strategies = [MMRStrategy.DIVERSITY, MMRStrategy.RELEVANCE, MMRStrategy.BALANCED]
        results_by_strategy = {}
        
        for strategy in strategies:
            config = MMRConfig(
                strategy=strategy,
                lambda_param=0.5,
                diversity_threshold=0.3,
                max_results=5
            )
            
            mmr_results = advanced_search_service._apply_mmr(sample_results, query_embedding, config)
            results_by_strategy[strategy] = mmr_results
        
        # All strategies should return the same number of results
        result_counts = [len(results) for results in results_by_strategy.values()]
        assert len(set(result_counts)) == 1
        
        # Different strategies should produce different result orderings
        result_ids = {strategy: [r.id for r in results] for strategy, results in results_by_strategy.items()}
        
        # At least two strategies should produce different orderings
        unique_orderings = set(tuple(ids) for ids in result_ids.values())
        assert len(unique_orderings) >= 2
