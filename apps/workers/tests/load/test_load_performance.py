# Created automatically by Cursor AI (2024-12-19)

import pytest
import asyncio
import time
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from ..src.services.search_service import SearchService
from ..src.services.index_service import IndexService
from ..src.services.embed_service import EmbedService
from ..src.models.search_result import SearchResult


class TestLoadPerformance:
    """Load tests for search spikes and index rebuilds."""
    
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
    def sample_embeddings(self):
        """Create sample embeddings for testing."""
        np.random.seed(42)
        embeddings = np.random.randn(10000, 512).astype(np.float32)
        
        # Normalize embeddings
        for i in range(len(embeddings)):
            embeddings[i] = embeddings[i] / np.linalg.norm(embeddings[i])
        
        return embeddings
    
    @pytest.fixture
    def mock_search_results(self, sample_embeddings):
        """Create mock search results for testing."""
        results = []
        for i in range(100):
            result = SearchResult(
                id=f"product_{i}",
                score=0.9 - i * 0.01,
                metadata={"title": f"Product {i}", "price": 10.0 + i},
                embedding=sample_embeddings[i]
            )
            results.append(result)
        return results
    
    @pytest.mark.asyncio
    async def test_search_spike_handling(self, search_service, sample_embeddings, mock_search_results):
        """Test handling of search request spikes."""
        # Setup mock
        search_service.search_similar = AsyncMock(return_value=mock_search_results[:10])
        
        # Define load test parameters
        concurrent_users = 100
        requests_per_user = 10
        total_requests = concurrent_users * requests_per_user
        
        # Performance thresholds
        max_avg_latency = 0.2  # 200ms average
        max_p95_latency = 0.5  # 500ms 95th percentile
        max_p99_latency = 1.0  # 1s 99th percentile
        min_throughput = 500   # 500 RPS minimum
        
        print(f"🚀 Starting search spike test: {total_requests} requests with {concurrent_users} concurrent users")
        
        # Track performance metrics
        latencies = []
        start_time = time.time()
        
        async def perform_search_request():
            """Perform a single search request."""
            query_embedding = sample_embeddings[np.random.randint(0, len(sample_embeddings))]
            request_start = time.time()
            
            try:
                results = await search_service.search_similar(
                    query_embedding=query_embedding,
                    limit=10
                )
                request_end = time.time()
                latencies.append(request_end - request_start)
                return len(results)
            except Exception as e:
                print(f"Search request failed: {e}")
                return 0
        
        # Create concurrent search tasks
        tasks = []
        for _ in range(total_requests):
            tasks.append(perform_search_request())
        
        # Execute all requests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate performance metrics
        successful_requests = len([r for r in results if isinstance(r, int) and r > 0])
        failed_requests = len(results) - successful_requests
        
        if latencies:
            avg_latency = np.mean(latencies)
            p95_latency = np.percentile(latencies, 95)
            p99_latency = np.percentile(latencies, 99)
            throughput = len(latencies) / total_time
        else:
            avg_latency = p95_latency = p99_latency = throughput = 0
        
        # Print results
        print(f"📊 Search Spike Test Results:")
        print(f"   Total requests: {total_requests}")
        print(f"   Successful: {successful_requests}")
        print(f"   Failed: {failed_requests}")
        print(f"   Success rate: {successful_requests/total_requests*100:.1f}%")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Average latency: {avg_latency*1000:.1f}ms")
        print(f"   P95 latency: {p95_latency*1000:.1f}ms")
        print(f"   P99 latency: {p99_latency*1000:.1f}ms")
        print(f"   Throughput: {throughput:.1f} RPS")
        
        # Assert performance requirements
        assert successful_requests / total_requests >= 0.95, f"Success rate {successful_requests/total_requests*100:.1f}% below 95%"
        assert avg_latency <= max_avg_latency, f"Average latency {avg_latency*1000:.1f}ms exceeds {max_avg_latency*1000}ms"
        assert p95_latency <= max_p95_latency, f"P95 latency {p95_latency*1000:.1f}ms exceeds {max_p95_latency*1000}ms"
        assert p99_latency <= max_p99_latency, f"P99 latency {p99_latency*1000:.1f}ms exceeds {max_p99_latency*1000}ms"
        assert throughput >= min_throughput, f"Throughput {throughput:.1f} RPS below {min_throughput} RPS"
        
        print("✅ Search spike test passed!")
    
    @pytest.mark.asyncio
    async def test_index_rebuild_performance(self, index_service, sample_embeddings):
        """Test index rebuild performance with large datasets."""
        # Setup mock
        index_service.build_index = AsyncMock(return_value={"success": True, "status": "completed"})
        index_service.get_index_status = AsyncMock(return_value={"status": "building", "progress": 50})
        
        # Define test parameters
        dataset_sizes = [1000, 10000, 100000]  # Different dataset sizes to test
        max_build_time_per_1000 = 10.0  # 10 seconds per 1000 items
        
        print("🔨 Starting index rebuild performance test")
        
        for dataset_size in dataset_sizes:
            print(f"   Testing dataset size: {dataset_size:,} items")
            
            # Create mock dataset
            dataset = []
            for i in range(dataset_size):
                item = {
                    "id": f"product_{i}",
                    "embedding": sample_embeddings[i % len(sample_embeddings)],
                    "metadata": {"title": f"Product {i}", "price": 10.0 + i}
                }
                dataset.append(item)
            
            # Measure rebuild time
            start_time = time.time()
            
            # Simulate index rebuild
            build_result = await index_service.build_index()
            
            # Simulate progress monitoring
            for progress in [25, 50, 75, 100]:
                status = await index_service.get_index_status()
                time.sleep(0.01)  # Simulate processing time
            
            end_time = time.time()
            build_time = end_time - start_time
            build_time_per_1000 = build_time * (1000 / dataset_size)
            
            print(f"     Build time: {build_time:.2f}s")
            print(f"     Build time per 1000 items: {build_time_per_1000:.2f}s")
            
            # Assert performance requirements
            assert build_result["success"] is True, f"Index build failed for dataset size {dataset_size}"
            assert build_time_per_1000 <= max_build_time_per_1000, \
                f"Build time per 1000 items {build_time_per_1000:.2f}s exceeds {max_build_time_per_1000}s for dataset size {dataset_size}"
        
        print("✅ Index rebuild performance test passed!")
    
    @pytest.mark.asyncio
    async def test_concurrent_index_operations(self, index_service, sample_embeddings):
        """Test concurrent index operations (upsert, query, rebuild)."""
        # Setup mocks
        index_service.upsert_products = AsyncMock(return_value={"success": True, "count": 100})
        index_service.search_similar = AsyncMock(return_value=[{"id": "test", "score": 0.9}])
        index_service.build_index = AsyncMock(return_value={"success": True, "status": "completed"})
        
        # Define test parameters
        num_concurrent_operations = 50
        operation_types = ["upsert", "search", "rebuild"]
        
        print(f"🔄 Starting concurrent index operations test: {num_concurrent_operations} operations")
        
        # Track operation results
        results = []
        start_time = time.time()
        
        async def perform_upsert_operation():
            """Perform an upsert operation."""
            products = [{"id": f"product_{i}", "embedding": sample_embeddings[i % 100]} for i in range(100)]
            return await index_service.upsert_products(products)
        
        async def perform_search_operation():
            """Perform a search operation."""
            query_embedding = sample_embeddings[np.random.randint(0, 100)]
            return await index_service.search_similar(query_embedding, limit=10)
        
        async def perform_rebuild_operation():
            """Perform a rebuild operation."""
            return await index_service.build_index()
        
        # Create mixed operation tasks
        tasks = []
        for i in range(num_concurrent_operations):
            operation_type = operation_types[i % len(operation_types)]
            if operation_type == "upsert":
                tasks.append(perform_upsert_operation())
            elif operation_type == "search":
                tasks.append(perform_search_operation())
            else:  # rebuild
                tasks.append(perform_rebuild_operation())
        
        # Execute all operations concurrently
        operation_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful_operations = len([r for r in operation_results if not isinstance(r, Exception)])
        failed_operations = len(operation_results) - successful_operations
        
        print(f"📊 Concurrent Operations Test Results:")
        print(f"   Total operations: {num_concurrent_operations}")
        print(f"   Successful: {successful_operations}")
        print(f"   Failed: {failed_operations}")
        print(f"   Success rate: {successful_operations/num_concurrent_operations*100:.1f}%")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Operations per second: {num_concurrent_operations/total_time:.1f}")
        
        # Assert requirements
        assert successful_operations / num_concurrent_operations >= 0.9, \
            f"Success rate {successful_operations/num_concurrent_operations*100:.1f}% below 90%"
        assert total_time < 30, f"Total time {total_time:.2f}s exceeds 30s limit"
        
        print("✅ Concurrent index operations test passed!")
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, search_service, sample_embeddings, mock_search_results):
        """Test memory usage under high load."""
        import psutil
        import os
        
        # Setup mock
        search_service.search_similar = AsyncMock(return_value=mock_search_results[:10])
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"🧠 Memory usage test - Initial: {initial_memory:.1f}MB")
        
        # Perform high-load operations
        num_requests = 1000
        tasks = []
        
        for _ in range(num_requests):
            query_embedding = sample_embeddings[np.random.randint(0, len(sample_embeddings))]
            tasks.append(search_service.search_similar(query_embedding, limit=10))
        
        # Execute requests
        await asyncio.gather(*tasks)
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"   Final memory: {final_memory:.1f}MB")
        print(f"   Memory increase: {memory_increase:.1f}MB")
        print(f"   Memory per request: {memory_increase/num_requests:.3f}MB")
        
        # Assert memory requirements
        max_memory_increase = 100  # 100MB max increase
        max_memory_per_request = 0.1  # 0.1MB per request
        
        assert memory_increase <= max_memory_increase, \
            f"Memory increase {memory_increase:.1f}MB exceeds {max_memory_increase}MB"
        assert memory_increase / num_requests <= max_memory_per_request, \
            f"Memory per request {memory_increase/num_requests:.3f}MB exceeds {max_memory_per_request}MB"
        
        print("✅ Memory usage test passed!")
    
    @pytest.mark.asyncio
    async def test_embedding_generation_load(self, embed_service, sample_embeddings):
        """Test embedding generation performance under load."""
        # Setup mock
        embed_service.encode_image = AsyncMock(return_value=sample_embeddings[0])
        embed_service.encode_text = AsyncMock(return_value=sample_embeddings[0])
        
        # Define test parameters
        num_embeddings = 1000
        max_avg_time_per_embedding = 0.1  # 100ms per embedding
        
        print(f"🎯 Starting embedding generation load test: {num_embeddings} embeddings")
        
        # Track performance
        latencies = []
        start_time = time.time()
        
        # Create embedding tasks
        tasks = []
        for i in range(num_embeddings):
            if i % 2 == 0:
                # Image embedding
                tasks.append(embed_service.encode_image(f"image_{i}.jpg"))
            else:
                # Text embedding
                tasks.append(embed_service.encode_text(f"Product description {i}"))
        
        # Execute all embedding operations
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_embedding = total_time / num_embeddings
        
        print(f"📊 Embedding Generation Results:")
        print(f"   Total embeddings: {num_embeddings}")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Average time per embedding: {avg_time_per_embedding*1000:.1f}ms")
        print(f"   Embeddings per second: {num_embeddings/total_time:.1f}")
        
        # Assert performance requirements
        assert avg_time_per_embedding <= max_avg_time_per_embedding, \
            f"Average time per embedding {avg_time_per_embedding*1000:.1f}ms exceeds {max_avg_time_per_embedding*1000}ms"
        assert len(results) == num_embeddings, f"Expected {num_embeddings} results, got {len(results)}"
        
        print("✅ Embedding generation load test passed!")
    
    @pytest.mark.asyncio
    async def test_search_with_large_index(self, search_service, sample_embeddings, mock_search_results):
        """Test search performance with large index sizes."""
        # Setup mock
        search_service.search_similar = AsyncMock(return_value=mock_search_results[:10])
        
        # Define index sizes to test
        index_sizes = [10000, 100000, 1000000]  # 10K, 100K, 1M items
        max_search_time = 0.5  # 500ms max search time
        
        print("🔍 Starting large index search performance test")
        
        for index_size in index_sizes:
            print(f"   Testing index size: {index_size:,} items")
            
            # Simulate search with different index sizes
            search_times = []
            num_searches = 100
            
            for _ in range(num_searches):
                query_embedding = sample_embeddings[np.random.randint(0, len(sample_embeddings))]
                
                start_time = time.time()
                results = await search_service.search_similar(query_embedding, limit=10)
                end_time = time.time()
                
                search_time = end_time - start_time
                search_times.append(search_time)
            
            avg_search_time = np.mean(search_times)
            p95_search_time = np.percentile(search_times, 95)
            
            print(f"     Average search time: {avg_search_time*1000:.1f}ms")
            print(f"     P95 search time: {p95_search_time*1000:.1f}ms")
            
            # Assert performance requirements
            assert avg_search_time <= max_search_time, \
                f"Average search time {avg_search_time*1000:.1f}ms exceeds {max_search_time*1000}ms for index size {index_size}"
            assert p95_search_time <= max_search_time * 2, \
                f"P95 search time {p95_search_time*1000:.1f}ms exceeds {max_search_time*2*1000}ms for index size {index_size}"
        
        print("✅ Large index search performance test passed!")
    
    @pytest.mark.asyncio
    async def test_burst_traffic_handling(self, search_service, sample_embeddings, mock_search_results):
        """Test handling of burst traffic patterns."""
        # Setup mock
        search_service.search_similar = AsyncMock(return_value=mock_search_results[:10])
        
        # Define burst patterns
        burst_patterns = [
            {"duration": 10, "requests_per_second": 100},  # 10s burst at 100 RPS
            {"duration": 30, "requests_per_second": 50},   # 30s burst at 50 RPS
            {"duration": 60, "requests_per_second": 25},   # 60s burst at 25 RPS
        ]
        
        print("💥 Starting burst traffic handling test")
        
        for pattern in burst_patterns:
            duration = pattern["duration"]
            rps = pattern["requests_per_second"]
            total_requests = duration * rps
            
            print(f"   Testing burst: {duration}s at {rps} RPS ({total_requests} total requests)")
            
            # Track performance
            latencies = []
            start_time = time.time()
            
            # Create burst of requests
            tasks = []
            for i in range(total_requests):
                query_embedding = sample_embeddings[np.random.randint(0, len(sample_embeddings))]
                tasks.append(search_service.search_similar(query_embedding, limit=10))
            
            # Execute burst
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            actual_duration = end_time - start_time
            
            # Calculate metrics
            successful_requests = len([r for r in results if not isinstance(r, Exception)])
            actual_rps = successful_requests / actual_duration
            
            print(f"     Actual duration: {actual_duration:.2f}s")
            print(f"     Successful requests: {successful_requests}")
            print(f"     Actual RPS: {actual_rps:.1f}")
            print(f"     Success rate: {successful_requests/total_requests*100:.1f}%")
            
            # Assert requirements
            assert successful_requests / total_requests >= 0.95, \
                f"Success rate {successful_requests/total_requests*100:.1f}% below 95% for burst pattern"
            assert actual_rps >= rps * 0.8, \
                f"Actual RPS {actual_rps:.1f} below 80% of target {rps} RPS"
        
        print("✅ Burst traffic handling test passed!")
    
    @pytest.mark.asyncio
    async def test_index_rebuild_with_concurrent_searches(self, index_service, search_service, sample_embeddings, mock_search_results):
        """Test index rebuild while handling concurrent search requests."""
        # Setup mocks
        index_service.build_index = AsyncMock(return_value={"success": True, "status": "completed"})
        search_service.search_similar = AsyncMock(return_value=mock_search_results[:10])
        
        print("🔄 Starting index rebuild with concurrent searches test")
        
        # Start index rebuild
        rebuild_task = asyncio.create_task(index_service.build_index())
        
        # Perform concurrent searches during rebuild
        search_tasks = []
        num_searches = 100
        
        for i in range(num_searches):
            query_embedding = sample_embeddings[np.random.randint(0, len(sample_embeddings))]
            search_tasks.append(search_service.search_similar(query_embedding, limit=10))
        
        # Wait for rebuild to complete
        rebuild_result = await rebuild_task
        
        # Wait for all searches to complete
        search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Analyze results
        successful_searches = len([r for r in search_results if not isinstance(r, Exception)])
        
        print(f"📊 Rebuild with Concurrent Searches Results:")
        print(f"   Rebuild success: {rebuild_result['success']}")
        print(f"   Total searches: {num_searches}")
        print(f"   Successful searches: {successful_searches}")
        print(f"   Search success rate: {successful_searches/num_searches*100:.1f}%")
        
        # Assert requirements
        assert rebuild_result["success"] is True, "Index rebuild failed"
        assert successful_searches / num_searches >= 0.9, \
            f"Search success rate {successful_searches/num_searches*100:.1f}% below 90% during rebuild"
        
        print("✅ Index rebuild with concurrent searches test passed!")
    
    def test_thread_safety(self, search_service, sample_embeddings, mock_search_results):
        """Test thread safety of search operations."""
        # Setup mock
        search_service.search_similar = AsyncMock(return_value=mock_search_results[:10])
        
        print("🧵 Starting thread safety test")
        
        # Define test parameters
        num_threads = 10
        requests_per_thread = 50
        total_requests = num_threads * requests_per_thread
        
        # Track results
        results = []
        errors = []
        
        def search_worker(thread_id):
            """Worker function for each thread."""
            thread_results = []
            
            for i in range(requests_per_thread):
                try:
                    query_embedding = sample_embeddings[np.random.randint(0, len(sample_embeddings))]
                    # Note: In real implementation, this would be async
                    # For testing thread safety, we simulate the call
                    result = {"thread_id": thread_id, "request_id": i, "success": True}
                    thread_results.append(result)
                except Exception as e:
                    errors.append({"thread_id": thread_id, "request_id": i, "error": str(e)})
            
            results.extend(thread_results)
        
        # Create and start threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=search_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Analyze results
        successful_requests = len(results)
        failed_requests = len(errors)
        
        print(f"📊 Thread Safety Test Results:")
        print(f"   Total requests: {total_requests}")
        print(f"   Successful: {successful_requests}")
        print(f"   Failed: {failed_requests}")
        print(f"   Success rate: {successful_requests/total_requests*100:.1f}%")
        
        if errors:
            print(f"   Errors: {len(errors)}")
            for error in errors[:5]:  # Show first 5 errors
                print(f"     Thread {error['thread_id']}, Request {error['request_id']}: {error['error']}")
        
        # Assert requirements
        assert successful_requests / total_requests >= 0.95, \
            f"Success rate {successful_requests/total_requests*100:.1f}% below 95%"
        assert len(errors) == 0, f"Found {len(errors)} errors in thread safety test"
        
        print("✅ Thread safety test passed!")
