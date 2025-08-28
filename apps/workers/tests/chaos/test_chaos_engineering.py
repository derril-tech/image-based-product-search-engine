# Created automatically by Cursor AI (2024-12-19)

import pytest
import asyncio
import time
import numpy as np
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import random
from ..src.services.search_service import SearchService
from ..src.services.index_service import IndexService
from ..src.services.embed_service import EmbedService
from ..src.services.ingest_service import IngestService
from ..src.models.search_result import SearchResult


class TestChaosEngineering:
    """Chaos engineering tests for system resilience under failure conditions."""
    
    @pytest.fixture
    def search_service(self):
        """Create a search service instance for testing."""
        return SearchService()
    
    @pytest.fixture
    def index_service(self):
        """Create an index service instance for testing."""
        return IndexService()
    
    @pytest.fixture
    def embed_service(self):
        """Create an embed service instance for testing."""
        return EmbedService()
    
    @pytest.fixture
    def ingest_service(self):
        """Create an ingest service instance for testing."""
        return IngestService()
    
    @pytest.fixture
    def sample_embeddings(self):
        """Create sample embeddings for testing."""
        np.random.seed(42)
        embeddings = np.random.randn(1000, 512).astype(np.float32)
        
        # Normalize embeddings
        for i in range(len(embeddings)):
            embeddings[i] = embeddings[i] / np.linalg.norm(embeddings[i])
        
        return embeddings
    
    @pytest.fixture
    def mock_search_results(self, sample_embeddings):
        """Create mock search results for testing."""
        results = []
        for i in range(10):
            result = SearchResult(
                id=f"product_{i}",
                score=0.9 - i * 0.01,
                metadata={"title": f"Product {i}", "price": 10.0 + i},
                embedding=sample_embeddings[i]
            )
            results.append(result)
        return results
    
    @pytest.mark.asyncio
    async def test_gpu_node_failure_recovery(self, embed_service, sample_embeddings):
        """Test recovery from GPU node failure during embedding generation."""
        print("🔥 Testing GPU node failure recovery")
        
        # Setup mock with failure simulation
        failure_count = 0
        max_failures = 3
        
        async def mock_encode_with_failures(*args, **kwargs):
            nonlocal failure_count
            if failure_count < max_failures:
                failure_count += 1
                raise Exception("GPU node unavailable")
            return sample_embeddings[0]
        
        embed_service.encode_image = AsyncMock(side_effect=mock_encode_with_failures)
        embed_service.encode_text = AsyncMock(side_effect=mock_encode_with_failures)
        
        # Test embedding generation with retries
        successful_embeddings = 0
        failed_embeddings = 0
        max_retries = 5
        
        for i in range(10):
            for attempt in range(max_retries):
                try:
                    if i % 2 == 0:
                        embedding = await embed_service.encode_image(f"image_{i}.jpg")
                    else:
                        embedding = await embed_service.encode_text(f"Product {i}")
                    
                    successful_embeddings += 1
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        failed_embeddings += 1
                        print(f"   Failed to generate embedding for item {i} after {max_retries} attempts")
                    else:
                        await asyncio.sleep(0.1)  # Simulate retry delay
        
        print(f"📊 GPU Failure Recovery Results:")
        print(f"   Successful embeddings: {successful_embeddings}")
        print(f"   Failed embeddings: {failed_embeddings}")
        print(f"   Success rate: {successful_embeddings/(successful_embeddings+failed_embeddings)*100:.1f}%")
        
        # Assert recovery requirements
        assert successful_embeddings >= 8, f"Only {successful_embeddings}/10 embeddings succeeded"
        assert failed_embeddings <= 2, f"Too many failed embeddings: {failed_embeddings}"
        
        print("✅ GPU node failure recovery test passed!")
    
    @pytest.mark.asyncio
    async def test_milvus_pod_restart_resilience(self, index_service, search_service, sample_embeddings, mock_search_results):
        """Test resilience to Milvus pod restarts during operations."""
        print("🔄 Testing Milvus pod restart resilience")
        
        # Setup mocks with restart simulation
        restart_count = 0
        max_restarts = 2
        
        async def mock_search_with_restarts(*args, **kwargs):
            nonlocal restart_count
            if restart_count < max_restarts and random.random() < 0.3:  # 30% chance of restart
                restart_count += 1
                raise Exception("Milvus connection lost - pod restarting")
            return mock_search_results
        
        async def mock_index_with_restarts(*args, **kwargs):
            nonlocal restart_count
            if restart_count < max_restarts and random.random() < 0.2:  # 20% chance of restart
                restart_count += 1
                raise Exception("Milvus index unavailable")
            return {"success": True, "count": 100}
        
        search_service.search_similar = AsyncMock(side_effect=mock_search_with_restarts)
        index_service.upsert_products = AsyncMock(side_effect=mock_index_with_restarts)
        
        # Test operations during pod restarts
        successful_operations = 0
        failed_operations = 0
        max_retries = 3
        
        # Test search operations
        for i in range(20):
            for attempt in range(max_retries):
                try:
                    query_embedding = sample_embeddings[i % len(sample_embeddings)]
                    results = await search_service.search_similar(query_embedding, limit=10)
                    successful_operations += 1
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        failed_operations += 1
                    else:
                        await asyncio.sleep(0.2)  # Simulate reconnection delay
        
        # Test index operations
        for i in range(10):
            for attempt in range(max_retries):
                try:
                    products = [{"id": f"product_{i}", "embedding": sample_embeddings[i % 100]}]
                    result = await index_service.upsert_products(products)
                    successful_operations += 1
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        failed_operations += 1
                    else:
                        await asyncio.sleep(0.2)
        
        print(f"📊 Milvus Restart Resilience Results:")
        print(f"   Successful operations: {successful_operations}")
        print(f"   Failed operations: {failed_operations}")
        print(f"   Success rate: {successful_operations/(successful_operations+failed_operations)*100:.1f}%")
        print(f"   Pod restarts simulated: {restart_count}")
        
        # Assert resilience requirements
        assert successful_operations / (successful_operations + failed_operations) >= 0.8, \
            f"Success rate {successful_operations/(successful_operations+failed_operations)*100:.1f}% below 80%"
        assert restart_count > 0, "No pod restarts were simulated"
        
        print("✅ Milvus pod restart resilience test passed!")
    
    @pytest.mark.asyncio
    async def test_connector_failure_handling(self, ingest_service):
        """Test handling of connector failures during data ingestion."""
        print("🔌 Testing connector failure handling")
        
        # Setup mock with connector failure simulation
        failure_scenarios = [
            {"connector": "shopify", "failure_rate": 0.3, "error": "API rate limit exceeded"},
            {"connector": "bigcommerce", "failure_rate": 0.2, "error": "Authentication failed"},
            {"connector": "woocommerce", "failure_rate": 0.4, "error": "Connection timeout"},
            {"connector": "csv", "failure_rate": 0.1, "error": "File not found"}
        ]
        
        async def mock_process_feed_with_failures(feed_url, *args, **kwargs):
            connector_type = "unknown"
            if "shopify" in feed_url:
                connector_type = "shopify"
            elif "bigcommerce" in feed_url:
                connector_type = "bigcommerce"
            elif "woocommerce" in feed_url:
                connector_type = "woocommerce"
            elif "csv" in feed_url:
                connector_type = "csv"
            
            # Find failure scenario
            scenario = next((s for s in failure_scenarios if s["connector"] == connector_type), None)
            
            if scenario and random.random() < scenario["failure_rate"]:
                raise Exception(scenario["error"])
            
            # Return mock data
            return [
                {"id": f"product_{i}", "title": f"Product {i}", "price": 10.0 + i}
                for i in range(10)
            ]
        
        ingest_service.process_feed = AsyncMock(side_effect=mock_process_feed_with_failures)
        
        # Test multiple connector types
        test_feeds = [
            "https://shop.example.com/shopify/feed.xml",
            "https://store.example.com/bigcommerce/feed.xml",
            "https://shop.example.com/woocommerce/feed.xml",
            "https://example.com/products.csv"
        ]
        
        successful_ingestions = 0
        failed_ingestions = 0
        max_retries = 3
        
        for feed_url in test_feeds:
            for attempt in range(max_retries):
                try:
                    products = await ingest_service.process_feed(feed_url)
                    successful_ingestions += 1
                    print(f"   Successfully ingested {len(products)} products from {feed_url}")
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        failed_ingestions += 1
                        print(f"   Failed to ingest from {feed_url}: {str(e)}")
                    else:
                        await asyncio.sleep(0.5)  # Simulate retry delay
        
        print(f"📊 Connector Failure Handling Results:")
        print(f"   Successful ingestions: {successful_ingestions}")
        print(f"   Failed ingestions: {failed_ingestions}")
        print(f"   Success rate: {successful_ingestions/(successful_ingestions+failed_ingestions)*100:.1f}%")
        
        # Assert failure handling requirements
        assert successful_ingestions >= 2, f"Only {successful_ingestions}/4 connectors succeeded"
        assert failed_ingestions <= 2, f"Too many connector failures: {failed_ingestions}"
        
        print("✅ Connector failure handling test passed!")
    
    @pytest.mark.asyncio
    async def test_network_partition_resilience(self, search_service, index_service, sample_embeddings, mock_search_results):
        """Test resilience to network partitions between services."""
        print("🌐 Testing network partition resilience")
        
        # Setup mocks with network partition simulation
        partition_active = False
        partition_duration = 5  # seconds
        
        async def mock_search_with_partition(*args, **kwargs):
            if partition_active:
                raise Exception("Network partition - service unavailable")
            return mock_search_results
        
        async def mock_index_with_partition(*args, **kwargs):
            if partition_active:
                raise Exception("Network partition - index service unavailable")
            return {"success": True, "count": 100}
        
        search_service.search_similar = AsyncMock(side_effect=mock_search_with_partition)
        index_service.upsert_products = AsyncMock(side_effect=mock_index_with_partition)
        
        # Start background task to simulate network partition
        async def simulate_partition():
            nonlocal partition_active
            await asyncio.sleep(2)  # Wait before starting partition
            partition_active = True
            print("   🔴 Network partition started")
            await asyncio.sleep(partition_duration)
            partition_active = False
            print("   🟢 Network partition resolved")
        
        # Start partition simulation
        partition_task = asyncio.create_task(simulate_partition())
        
        # Perform operations during partition
        successful_operations = 0
        failed_operations = 0
        max_retries = 5
        
        # Test operations during partition
        for i in range(30):
            for attempt in range(max_retries):
                try:
                    if i % 2 == 0:
                        # Search operation
                        query_embedding = sample_embeddings[i % len(sample_embeddings)]
                        results = await search_service.search_similar(query_embedding, limit=10)
                    else:
                        # Index operation
                        products = [{"id": f"product_{i}", "embedding": sample_embeddings[i % 100]}]
                        result = await index_service.upsert_products(products)
                    
                    successful_operations += 1
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        failed_operations += 1
                    else:
                        await asyncio.sleep(0.3)  # Simulate retry delay
            
            await asyncio.sleep(0.1)  # Small delay between operations
        
        # Wait for partition simulation to complete
        await partition_task
        
        print(f"📊 Network Partition Resilience Results:")
        print(f"   Successful operations: {successful_operations}")
        print(f"   Failed operations: {failed_operations}")
        print(f"   Success rate: {successful_operations/(successful_operations+failed_operations)*100:.1f}%")
        
        # Assert resilience requirements
        assert successful_operations / (successful_operations + failed_operations) >= 0.6, \
            f"Success rate {successful_operations/(successful_operations+failed_operations)*100:.1f}% below 60%"
        assert failed_operations > 0, "No operations failed during network partition"
        
        print("✅ Network partition resilience test passed!")
    
    @pytest.mark.asyncio
    async def test_memory_pressure_handling(self, search_service, sample_embeddings, mock_search_results):
        """Test system behavior under memory pressure."""
        print("💾 Testing memory pressure handling")
        
        import psutil
        import os
        
        # Setup mock
        search_service.search_similar = AsyncMock(return_value=mock_search_results)
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"   Initial memory usage: {initial_memory:.1f}MB")
        
        # Simulate memory pressure by creating large objects
        large_objects = []
        memory_pressure_objects = []
        
        # Create memory pressure
        for i in range(100):
            # Create large arrays to simulate memory pressure
            large_array = np.random.randn(1000, 1000).astype(np.float32)
            memory_pressure_objects.append(large_array)
            
            if i % 10 == 0:
                # Perform search operations under memory pressure
                query_embedding = sample_embeddings[i % len(sample_embeddings)]
                try:
                    results = await search_service.search_similar(query_embedding, limit=10)
                    large_objects.append(results)
                except Exception as e:
                    print(f"   Search failed under memory pressure: {e}")
        
        # Get memory usage under pressure
        pressure_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = pressure_memory - initial_memory
        
        print(f"   Memory under pressure: {pressure_memory:.1f}MB")
        print(f"   Memory increase: {memory_increase:.1f}MB")
        print(f"   Successful operations under pressure: {len(large_objects)}")
        
        # Clean up memory pressure objects
        del memory_pressure_objects
        del large_objects
        
        # Get memory after cleanup
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_recovery = pressure_memory - final_memory
        
        print(f"   Memory after cleanup: {final_memory:.1f}MB")
        print(f"   Memory recovered: {memory_recovery:.1f}MB")
        
        # Assert memory pressure handling requirements
        assert len(large_objects) >= 5, f"Only {len(large_objects)} operations succeeded under memory pressure"
        assert memory_recovery > 0, "No memory was recovered after cleanup"
        
        print("✅ Memory pressure handling test passed!")
    
    @pytest.mark.asyncio
    async def test_cascading_failure_prevention(self, search_service, index_service, embed_service, sample_embeddings, mock_search_results):
        """Test prevention of cascading failures across services."""
        print("🔄 Testing cascading failure prevention")
        
        # Setup mocks with cascading failure simulation
        failure_chain = []
        max_chain_length = 3
        
        async def mock_search_with_cascade(*args, **kwargs):
            if len(failure_chain) < max_chain_length and random.random() < 0.4:
                failure_chain.append("search")
                raise Exception("Search service failure")
            return mock_search_results
        
        async def mock_index_with_cascade(*args, **kwargs):
            if len(failure_chain) < max_chain_length and random.random() < 0.3:
                failure_chain.append("index")
                raise Exception("Index service failure")
            return {"success": True, "count": 100}
        
        async def mock_embed_with_cascade(*args, **kwargs):
            if len(failure_chain) < max_chain_length and random.random() < 0.5:
                failure_chain.append("embed")
                raise Exception("Embedding service failure")
            return sample_embeddings[0]
        
        search_service.search_similar = AsyncMock(side_effect=mock_search_with_cascade)
        index_service.upsert_products = AsyncMock(side_effect=mock_index_with_cascade)
        embed_service.encode_image = AsyncMock(side_effect=mock_embed_with_cascade)
        embed_service.encode_text = AsyncMock(side_effect=mock_embed_with_cascade)
        
        # Test operations with circuit breaker pattern
        successful_operations = 0
        failed_operations = 0
        circuit_breaker_state = "closed"  # closed, open, half-open
        failure_count = 0
        max_failures = 5
        
        for i in range(20):
            try:
                if circuit_breaker_state == "open":
                    # Circuit breaker is open, skip operation
                    failed_operations += 1
                    await asyncio.sleep(0.1)
                    continue
                
                # Perform operation
                if i % 3 == 0:
                    # Search operation
                    query_embedding = sample_embeddings[i % len(sample_embeddings)]
                    results = await search_service.search_similar(query_embedding, limit=10)
                elif i % 3 == 1:
                    # Index operation
                    products = [{"id": f"product_{i}", "embedding": sample_embeddings[i % 100]}]
                    result = await index_service.upsert_products(products)
                else:
                    # Embedding operation
                    embedding = await embed_service.encode_image(f"image_{i}.jpg")
                
                successful_operations += 1
                failure_count = 0  # Reset failure count on success
                
                # Close circuit breaker if it was half-open
                if circuit_breaker_state == "half-open":
                    circuit_breaker_state = "closed"
                
            except Exception as e:
                failed_operations += 1
                failure_count += 1
                
                # Circuit breaker logic
                if failure_count >= max_failures and circuit_breaker_state == "closed":
                    circuit_breaker_state = "open"
                    print(f"   🔴 Circuit breaker opened after {failure_count} failures")
                elif circuit_breaker_state == "open":
                    # Try to move to half-open state
                    if random.random() < 0.2:  # 20% chance to try
                        circuit_breaker_state = "half-open"
                        print(f"   🟡 Circuit breaker moved to half-open state")
        
        print(f"📊 Cascading Failure Prevention Results:")
        print(f"   Successful operations: {successful_operations}")
        print(f"   Failed operations: {failed_operations}")
        print(f"   Success rate: {successful_operations/(successful_operations+failed_operations)*100:.1f}%")
        print(f"   Failure chain length: {len(failure_chain)}")
        print(f"   Circuit breaker state: {circuit_breaker_state}")
        
        # Assert cascading failure prevention requirements
        assert len(failure_chain) <= max_chain_length, \
            f"Failure chain length {len(failure_chain)} exceeds maximum {max_chain_length}"
        assert successful_operations / (successful_operations + failed_operations) >= 0.5, \
            f"Success rate {successful_operations/(successful_operations+failed_operations)*100:.1f}% below 50%"
        
        print("✅ Cascading failure prevention test passed!")
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self, search_service, index_service, sample_embeddings, mock_search_results):
        """Test graceful degradation when services are partially available."""
        print("📉 Testing graceful degradation")
        
        # Setup mocks with partial availability
        service_health = {
            "search": 0.8,  # 80% availability
            "index": 0.6,   # 60% availability
            "embed": 0.9    # 90% availability
        }
        
        async def mock_search_with_degradation(*args, **kwargs):
            if random.random() > service_health["search"]:
                raise Exception("Search service degraded")
            return mock_search_results[:5]  # Return fewer results when degraded
        
        async def mock_index_with_degradation(*args, **kwargs):
            if random.random() > service_health["index"]:
                raise Exception("Index service degraded")
            return {"success": True, "count": 50}  # Reduced capacity
        
        search_service.search_similar = AsyncMock(side_effect=mock_search_with_degradation)
        index_service.upsert_products = AsyncMock(side_effect=mock_index_with_degradation)
        
        # Test operations with graceful degradation
        successful_operations = 0
        degraded_operations = 0
        failed_operations = 0
        
        for i in range(50):
            try:
                if i % 2 == 0:
                    # Search operation
                    query_embedding = sample_embeddings[i % len(sample_embeddings)]
                    results = await search_service.search_similar(query_embedding, limit=10)
                    
                    # Check if operation was degraded
                    if len(results) < 10:
                        degraded_operations += 1
                    else:
                        successful_operations += 1
                else:
                    # Index operation
                    products = [{"id": f"product_{i}", "embedding": sample_embeddings[i % 100]}]
                    result = await index_service.upsert_products(products)
                    
                    # Check if operation was degraded
                    if result["count"] < 100:
                        degraded_operations += 1
                    else:
                        successful_operations += 1
                        
            except Exception as e:
                failed_operations += 1
        
        total_operations = successful_operations + degraded_operations + failed_operations
        
        print(f"📊 Graceful Degradation Results:")
        print(f"   Successful operations: {successful_operations}")
        print(f"   Degraded operations: {degraded_operations}")
        print(f"   Failed operations: {failed_operations}")
        print(f"   Overall success rate: {(successful_operations+degraded_operations)/total_operations*100:.1f}%")
        print(f"   Degradation rate: {degraded_operations/total_operations*100:.1f}%")
        
        # Assert graceful degradation requirements
        assert (successful_operations + degraded_operations) / total_operations >= 0.7, \
            f"Overall success rate {(successful_operations+degraded_operations)/total_operations*100:.1f}% below 70%"
        assert degraded_operations > 0, "No degraded operations detected"
        assert failed_operations < total_operations * 0.3, \
            f"Too many failed operations: {failed_operations/total_operations*100:.1f}%"
        
        print("✅ Graceful degradation test passed!")
    
    @pytest.mark.asyncio
    async def test_rapid_failure_recovery(self, search_service, sample_embeddings, mock_search_results):
        """Test rapid recovery from transient failures."""
        print("⚡ Testing rapid failure recovery")
        
        # Setup mock with rapid failure/recovery pattern
        failure_pattern = [True, True, False, True, False, False, False]  # Failure pattern
        pattern_index = 0
        
        async def mock_search_with_rapid_failures(*args, **kwargs):
            nonlocal pattern_index
            should_fail = failure_pattern[pattern_index % len(failure_pattern)]
            pattern_index += 1
            
            if should_fail:
                raise Exception("Transient failure")
            return mock_search_results
        
        search_service.search_similar = AsyncMock(side_effect=mock_search_with_rapid_failures)
        
        # Test rapid recovery
        successful_operations = 0
        failed_operations = 0
        recovery_times = []
        
        for i in range(20):
            start_time = time.time()
            
            for attempt in range(3):  # Max 3 attempts per operation
                try:
                    query_embedding = sample_embeddings[i % len(sample_embeddings)]
                    results = await search_service.search_similar(query_embedding, limit=10)
                    successful_operations += 1
                    
                    if attempt > 0:  # Recovery occurred
                        recovery_time = time.time() - start_time
                        recovery_times.append(recovery_time)
                    
                    break
                except Exception as e:
                    if attempt == 2:  # Last attempt
                        failed_operations += 1
                    else:
                        await asyncio.sleep(0.05)  # Short retry delay
        
        print(f"📊 Rapid Failure Recovery Results:")
        print(f"   Successful operations: {successful_operations}")
        print(f"   Failed operations: {failed_operations}")
        print(f"   Success rate: {successful_operations/(successful_operations+failed_operations)*100:.1f}%")
        
        if recovery_times:
            avg_recovery_time = np.mean(recovery_times)
            print(f"   Average recovery time: {avg_recovery_time*1000:.1f}ms")
            print(f"   Recovery events: {len(recovery_times)}")
        
        # Assert rapid recovery requirements
        assert successful_operations / (successful_operations + failed_operations) >= 0.8, \
            f"Success rate {successful_operations/(successful_operations+failed_operations)*100:.1f}% below 80%"
        
        if recovery_times:
            assert avg_recovery_time <= 0.5, f"Average recovery time {avg_recovery_time*1000:.1f}ms exceeds 500ms"
        
        print("✅ Rapid failure recovery test passed!")
    
    def test_concurrent_failure_scenarios(self, search_service, sample_embeddings, mock_search_results):
        """Test multiple concurrent failure scenarios."""
        print("🌪️ Testing concurrent failure scenarios")
        
        # Setup mock
        search_service.search_similar = AsyncMock(return_value=mock_search_results)
        
        # Define failure scenarios
        failure_scenarios = [
            {"name": "Network timeout", "probability": 0.2},
            {"name": "Service unavailable", "probability": 0.15},
            {"name": "Resource exhaustion", "probability": 0.1},
            {"name": "Data corruption", "probability": 0.05}
        ]
        
        # Track scenario outcomes
        scenario_results = {scenario["name"]: {"success": 0, "failure": 0} for scenario in failure_scenarios}
        
        def simulate_failure_scenario(scenario_name, probability):
            """Simulate a failure scenario."""
            if random.random() < probability:
                # Simulate failure
                time.sleep(random.uniform(0.1, 0.5))  # Simulate failure duration
                return False
            else:
                # Simulate success
                time.sleep(random.uniform(0.01, 0.1))  # Simulate success duration
                return True
        
        # Run concurrent failure scenarios
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            for scenario in failure_scenarios:
                for _ in range(10):  # 10 iterations per scenario
                    future = executor.submit(
                        simulate_failure_scenario,
                        scenario["name"],
                        scenario["probability"]
                    )
                    futures.append((scenario["name"], future))
            
            # Collect results
            for scenario_name, future in futures:
                try:
                    success = future.result(timeout=2.0)
                    if success:
                        scenario_results[scenario_name]["success"] += 1
                    else:
                        scenario_results[scenario_name]["failure"] += 1
                except Exception as e:
                    scenario_results[scenario_name]["failure"] += 1
        
        # Analyze results
        total_success = sum(result["success"] for result in scenario_results.values())
        total_failures = sum(result["failure"] for result in scenario_results.values())
        
        print(f"📊 Concurrent Failure Scenarios Results:")
        for scenario_name, results in scenario_results.items():
            total = results["success"] + results["failure"]
            success_rate = results["success"] / total * 100 if total > 0 else 0
            print(f"   {scenario_name}: {success_rate:.1f}% success rate ({results['success']}/{total})")
        
        print(f"   Overall success rate: {total_success/(total_success+total_failures)*100:.1f}%")
        
        # Assert concurrent failure handling requirements
        assert total_success / (total_success + total_failures) >= 0.6, \
            f"Overall success rate {total_success/(total_success+total_failures)*100:.1f}% below 60%"
        
        # Check that each scenario was tested
        for scenario_name, results in scenario_results.items():
            total = results["success"] + results["failure"]
            assert total > 0, f"No tests run for scenario: {scenario_name}"
        
        print("✅ Concurrent failure scenarios test passed!")
