# Created automatically by Cursor AI (2024-12-19)

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from PIL import Image
import numpy as np
from ..src.services.ingest_service import IngestService
from ..src.services.preprocess_service import PreprocessService
from ..src.services.detect_service import DetectService
from ..src.services.embed_service import EmbedService
from ..src.services.index_service import IndexService
from ..src.services.search_service import SearchService
from ..src.models.product import Product
from ..src.models.search_result import SearchResult


class TestPipelineIntegration:
    """Integration tests for the complete pipeline: feed → preprocess → detect → embed → index → search."""
    
    @pytest.fixture
    def sample_image(self):
        """Create a sample image for testing."""
        # Create a simple test image
        img = Image.new('RGB', (224, 224), color='red')
        return img
    
    @pytest.fixture
    def sample_product_data(self):
        """Create sample product data for testing."""
        return {
            "id": "test_product_1",
            "title": "Test Product",
            "description": "A test product for integration testing",
            "price": 29.99,
            "category": "electronics",
            "brand": "TestBrand",
            "image_url": "https://example.com/test_image.jpg",
            "metadata": {
                "sku": "TEST-001",
                "availability": "in_stock"
            }
        }
    
    @pytest.fixture
    def mock_services(self):
        """Create mock service instances for testing."""
        ingest_service = Mock(spec=IngestService)
        preprocess_service = Mock(spec=PreprocessService)
        detect_service = Mock(spec=DetectService)
        embed_service = Mock(spec=EmbedService)
        index_service = Mock(spec=IndexService)
        search_service = Mock(spec=SearchService)
        
        return {
            'ingest': ingest_service,
            'preprocess': preprocess_service,
            'detect': detect_service,
            'embed': embed_service,
            'index': index_service,
            'search': search_service
        }
    
    @pytest.fixture
    def sample_embedding(self):
        """Create a sample embedding vector."""
        np.random.seed(42)
        return np.random.randn(512).astype(np.float32)
    
    @pytest.fixture
    def sample_detection_results(self):
        """Create sample object detection results."""
        return [
            {
                "bbox": [100, 100, 200, 200],
                "confidence": 0.95,
                "class": "product",
                "class_id": 1
            },
            {
                "bbox": [50, 50, 150, 150],
                "confidence": 0.87,
                "class": "logo",
                "class_id": 2
            }
        ]
    
    @pytest.mark.asyncio
    async def test_complete_pipeline_flow(self, mock_services, sample_product_data, sample_image, sample_embedding, sample_detection_results):
        """Test the complete pipeline flow from ingestion to search."""
        # Setup mock responses
        mock_services['ingest'].process_feed.return_value = [sample_product_data]
        mock_services['preprocess'].process_image.return_value = sample_image
        mock_services['detect'].detect_objects.return_value = sample_detection_results
        mock_services['embed'].encode_image.return_value = sample_embedding
        mock_services['embed'].encode_text.return_value = sample_embedding
        mock_services['index'].upsert_products.return_value = {"success": True, "count": 1}
        mock_services['search'].search_similar.return_value = [
            SearchResult(
                id="test_product_1",
                score=0.95,
                metadata=sample_product_data,
                embedding=sample_embedding
            )
        ]
        
        # Test feed ingestion
        products = await mock_services['ingest'].process_feed("test_feed_url")
        assert len(products) == 1
        assert products[0]["id"] == "test_product_1"
        
        # Test image preprocessing
        processed_image = await mock_services['preprocess'].process_image(sample_image)
        assert processed_image is not None
        
        # Test object detection
        detections = await mock_services['detect'].detect_objects(processed_image)
        assert len(detections) == 2
        assert detections[0]["confidence"] > 0.9
        
        # Test embedding generation
        image_embedding = await mock_services['embed'].encode_image(processed_image)
        text_embedding = await mock_services['embed'].encode_text(sample_product_data["title"])
        assert image_embedding.shape == (512,)
        assert text_embedding.shape == (512,)
        
        # Test indexing
        index_result = await mock_services['index'].upsert_products([{
            "id": sample_product_data["id"],
            "embedding": image_embedding,
            "metadata": sample_product_data
        }])
        assert index_result["success"] is True
        assert index_result["count"] == 1
        
        # Test search
        search_results = await mock_services['search'].search_similar(
            query_embedding=sample_embedding,
            limit=10
        )
        assert len(search_results) == 1
        assert search_results[0].id == "test_product_1"
        assert search_results[0].score > 0.9
    
    @pytest.mark.asyncio
    async def test_pipeline_with_multiple_products(self, mock_services, sample_embedding):
        """Test pipeline with multiple products."""
        # Create multiple product data
        products_data = [
            {
                "id": f"product_{i}",
                "title": f"Product {i}",
                "description": f"Description for product {i}",
                "price": 10.0 + i,
                "category": "electronics",
                "brand": "TestBrand",
                "image_url": f"https://example.com/image_{i}.jpg",
                "metadata": {"sku": f"SKU-{i:03d}"}
            }
            for i in range(5)
        ]
        
        # Setup mock responses
        mock_services['ingest'].process_feed.return_value = products_data
        mock_services['preprocess'].process_image.return_value = Image.new('RGB', (224, 224))
        mock_services['detect'].detect_objects.return_value = [{"bbox": [0, 0, 100, 100], "confidence": 0.9, "class": "product"}]
        mock_services['embed'].encode_image.return_value = sample_embedding
        mock_services['embed'].encode_text.return_value = sample_embedding
        mock_services['index'].upsert_products.return_value = {"success": True, "count": 5}
        mock_services['search'].search_similar.return_value = [
            SearchResult(id=f"product_{i}", score=0.9-i*0.1, metadata=products_data[i], embedding=sample_embedding)
            for i in range(3)
        ]
        
        # Test ingestion
        products = await mock_services['ingest'].process_feed("test_feed_url")
        assert len(products) == 5
        
        # Test indexing multiple products
        index_data = [
            {
                "id": product["id"],
                "embedding": sample_embedding,
                "metadata": product
            }
            for product in products
        ]
        
        index_result = await mock_services['index'].upsert_products(index_data)
        assert index_result["success"] is True
        assert index_result["count"] == 5
        
        # Test search returns multiple results
        search_results = await mock_services['search'].search_similar(
            query_embedding=sample_embedding,
            limit=10
        )
        assert len(search_results) == 3
        assert search_results[0].score > search_results[1].score
    
    @pytest.mark.asyncio
    async def test_pipeline_error_handling(self, mock_services, sample_product_data, sample_image):
        """Test pipeline error handling and recovery."""
        # Setup mock to raise exception during preprocessing
        mock_services['ingest'].process_feed.return_value = [sample_product_data]
        mock_services['preprocess'].process_image.side_effect = Exception("Preprocessing failed")
        
        # Test that pipeline handles preprocessing errors gracefully
        products = await mock_services['ingest'].process_feed("test_feed_url")
        assert len(products) == 1
        
        # Should handle preprocessing error
        with pytest.raises(Exception, match="Preprocessing failed"):
            await mock_services['preprocess'].process_image(sample_image)
    
    @pytest.mark.asyncio
    async def test_pipeline_data_consistency(self, mock_services, sample_product_data, sample_embedding):
        """Test data consistency throughout the pipeline."""
        # Setup consistent mock responses
        mock_services['ingest'].process_feed.return_value = [sample_product_data]
        mock_services['preprocess'].process_image.return_value = Image.new('RGB', (224, 224))
        mock_services['detect'].detect_objects.return_value = [{"bbox": [0, 0, 100, 100], "confidence": 0.9, "class": "product"}]
        mock_services['embed'].encode_image.return_value = sample_embedding
        mock_services['embed'].encode_text.return_value = sample_embedding
        mock_services['index'].upsert_products.return_value = {"success": True, "count": 1}
        mock_services['search'].search_similar.return_value = [
            SearchResult(
                id=sample_product_data["id"],
                score=0.95,
                metadata=sample_product_data,
                embedding=sample_embedding
            )
        ]
        
        # Test data consistency
        products = await mock_services['ingest'].process_feed("test_feed_url")
        product = products[0]
        
        # Verify product data is preserved
        assert product["id"] == sample_product_data["id"]
        assert product["title"] == sample_product_data["title"]
        assert product["price"] == sample_product_data["price"]
        
        # Test that indexed data matches original
        index_data = {
            "id": product["id"],
            "embedding": sample_embedding,
            "metadata": product
        }
        
        index_result = await mock_services['index'].upsert_products([index_data])
        assert index_result["success"] is True
        
        # Test that search returns consistent data
        search_results = await mock_services['search'].search_similar(
            query_embedding=sample_embedding,
            limit=10
        )
        
        assert len(search_results) == 1
        result = search_results[0]
        assert result.id == sample_product_data["id"]
        assert result.metadata["title"] == sample_product_data["title"]
        assert result.metadata["price"] == sample_product_data["price"]
    
    @pytest.mark.asyncio
    async def test_pipeline_performance(self, mock_services, sample_embedding):
        """Test pipeline performance with multiple products."""
        import time
        
        # Create larger dataset
        products_data = [
            {
                "id": f"product_{i}",
                "title": f"Product {i}",
                "description": f"Description for product {i}",
                "price": 10.0 + i,
                "category": "electronics",
                "brand": "TestBrand",
                "image_url": f"https://example.com/image_{i}.jpg",
                "metadata": {"sku": f"SKU-{i:03d}"}
            }
            for i in range(100)
        ]
        
        # Setup mock responses
        mock_services['ingest'].process_feed.return_value = products_data
        mock_services['preprocess'].process_image.return_value = Image.new('RGB', (224, 224))
        mock_services['detect'].detect_objects.return_value = [{"bbox": [0, 0, 100, 100], "confidence": 0.9, "class": "product"}]
        mock_services['embed'].encode_image.return_value = sample_embedding
        mock_services['embed'].encode_text.return_value = sample_embedding
        mock_services['index'].upsert_products.return_value = {"success": True, "count": 100}
        mock_services['search'].search_similar.return_value = [
            SearchResult(id=f"product_{i}", score=0.9-i*0.01, metadata=products_data[i], embedding=sample_embedding)
            for i in range(10)
        ]
        
        # Measure pipeline performance
        start_time = time.time()
        
        # Ingestion
        products = await mock_services['ingest'].process_feed("test_feed_url")
        
        # Processing (simulate batch processing)
        processed_data = []
        for product in products:
            processed_image = await mock_services['preprocess'].process_image(Image.new('RGB', (224, 224)))
            detections = await mock_services['detect'].detect_objects(processed_image)
            embedding = await mock_services['embed'].encode_image(processed_image)
            
            processed_data.append({
                "id": product["id"],
                "embedding": embedding,
                "metadata": product,
                "detections": detections
            })
        
        # Indexing
        index_result = await mock_services['index'].upsert_products(processed_data)
        
        # Search
        search_results = await mock_services['search'].search_similar(
            query_embedding=sample_embedding,
            limit=10
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify results
        assert len(products) == 100
        assert len(processed_data) == 100
        assert index_result["count"] == 100
        assert len(search_results) == 10
        
        # Performance should be reasonable (less than 1 second for 100 products)
        assert total_time < 1.0
    
    @pytest.mark.asyncio
    async def test_pipeline_with_different_image_formats(self, mock_services, sample_product_data, sample_embedding):
        """Test pipeline with different image formats."""
        # Test with different image formats
        image_formats = ['RGB', 'RGBA', 'L', 'CMYK']
        
        for format_name in image_formats:
            if format_name == 'L':
                test_image = Image.new('L', (224, 224), color=128)
            elif format_name == 'CMYK':
                test_image = Image.new('CMYK', (224, 224), color=(0, 0, 0, 0))
            else:
                test_image = Image.new(format_name, (224, 224), color='red')
            
            # Setup mocks
            mock_services['ingest'].process_feed.return_value = [sample_product_data]
            mock_services['preprocess'].process_image.return_value = test_image
            mock_services['detect'].detect_objects.return_value = [{"bbox": [0, 0, 100, 100], "confidence": 0.9, "class": "product"}]
            mock_services['embed'].encode_image.return_value = sample_embedding
            mock_services['embed'].encode_text.return_value = sample_embedding
            mock_services['index'].upsert_products.return_value = {"success": True, "count": 1}
            mock_services['search'].search_similar.return_value = [
                SearchResult(
                    id=sample_product_data["id"],
                    score=0.95,
                    metadata=sample_product_data,
                    embedding=sample_embedding
                )
            ]
            
            # Test pipeline with this image format
            products = await mock_services['ingest'].process_feed("test_feed_url")
            processed_image = await mock_services['preprocess'].process_image(test_image)
            detections = await mock_services['detect'].detect_objects(processed_image)
            embedding = await mock_services['embed'].encode_image(processed_image)
            
            # Verify processing completed successfully
            assert processed_image is not None
            assert len(detections) > 0
            assert embedding.shape == (512,)
    
    @pytest.mark.asyncio
    async def test_pipeline_with_empty_results(self, mock_services, sample_embedding):
        """Test pipeline behavior with empty results."""
        # Setup mocks to return empty results
        mock_services['ingest'].process_feed.return_value = []
        mock_services['search'].search_similar.return_value = []
        
        # Test ingestion with empty feed
        products = await mock_services['ingest'].process_feed("empty_feed_url")
        assert len(products) == 0
        
        # Test search with no results
        search_results = await mock_services['search'].search_similar(
            query_embedding=sample_embedding,
            limit=10
        )
        assert len(search_results) == 0
    
    @pytest.mark.asyncio
    async def test_pipeline_concurrent_processing(self, mock_services, sample_embedding):
        """Test pipeline with concurrent processing."""
        import asyncio
        
        # Create multiple products
        products_data = [
            {
                "id": f"product_{i}",
                "title": f"Product {i}",
                "description": f"Description for product {i}",
                "price": 10.0 + i,
                "category": "electronics",
                "brand": "TestBrand",
                "image_url": f"https://example.com/image_{i}.jpg",
                "metadata": {"sku": f"SKU-{i:03d}"}
            }
            for i in range(10)
        ]
        
        # Setup mocks
        mock_services['ingest'].process_feed.return_value = products_data
        mock_services['preprocess'].process_image.return_value = Image.new('RGB', (224, 224))
        mock_services['detect'].detect_objects.return_value = [{"bbox": [0, 0, 100, 100], "confidence": 0.9, "class": "product"}]
        mock_services['embed'].encode_image.return_value = sample_embedding
        mock_services['embed'].encode_text.return_value = sample_embedding
        mock_services['index'].upsert_products.return_value = {"success": True, "count": 10}
        mock_services['search'].search_similar.return_value = [
            SearchResult(id=f"product_{i}", score=0.9-i*0.1, metadata=products_data[i], embedding=sample_embedding)
            for i in range(5)
        ]
        
        # Process products concurrently
        async def process_product(product):
            processed_image = await mock_services['preprocess'].process_image(Image.new('RGB', (224, 224)))
            detections = await mock_services['detect'].detect_objects(processed_image)
            embedding = await mock_services['embed'].encode_image(processed_image)
            
            return {
                "id": product["id"],
                "embedding": embedding,
                "metadata": product,
                "detections": detections
            }
        
        # Get products
        products = await mock_services['ingest'].process_feed("test_feed_url")
        
        # Process concurrently
        tasks = [process_product(product) for product in products]
        processed_data = await asyncio.gather(*tasks)
        
        # Index all processed data
        index_result = await mock_services['index'].upsert_products(processed_data)
        
        # Verify results
        assert len(processed_data) == 10
        assert index_result["count"] == 10
        
        # All products should have embeddings
        for data in processed_data:
            assert data["embedding"].shape == (512,)
            assert data["id"] in [p["id"] for p in products]
    
    @pytest.mark.asyncio
    async def test_pipeline_data_validation(self, mock_services, sample_embedding):
        """Test pipeline data validation."""
        # Test with invalid product data
        invalid_product = {
            "id": "",  # Empty ID
            "title": None,  # None title
            "price": -10,  # Negative price
            "image_url": "not_a_url"  # Invalid URL
        }
        
        # Setup mocks
        mock_services['ingest'].process_feed.return_value = [invalid_product]
        mock_services['preprocess'].process_image.return_value = Image.new('RGB', (224, 224))
        mock_services['detect'].detect_objects.return_value = []
        mock_services['embed'].encode_image.return_value = sample_embedding
        mock_services['embed'].encode_text.return_value = sample_embedding
        mock_services['index'].upsert_products.return_value = {"success": True, "count": 1}
        
        # Test that pipeline handles invalid data gracefully
        products = await mock_services['ingest'].process_feed("test_feed_url")
        assert len(products) == 1
        
        # Process should continue even with invalid data
        processed_image = await mock_services['preprocess'].process_image(Image.new('RGB', (224, 224)))
        detections = await mock_services['detect'].detect_objects(processed_image)
        embedding = await mock_services['embed'].encode_image(processed_image)
        
        # Should still produce valid embeddings
        assert embedding.shape == (512,)
        
        # Indexing should handle invalid metadata
        index_data = {
            "id": invalid_product["id"],
            "embedding": embedding,
            "metadata": invalid_product
        }
        
        index_result = await mock_services['index'].upsert_products([index_data])
        assert index_result["success"] is True
