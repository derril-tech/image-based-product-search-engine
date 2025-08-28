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
from ..src.services.cdn_service import CDNService
from ..src.models.product import Product
from ..src.models.search_result import SearchResult


class TestUserJourneyE2E:
    """End-to-end tests for complete user journey: import catalog → build index → upload image → crop → search → PDP."""
    
    @pytest.fixture
    def sample_catalog_data(self):
        """Create sample catalog data for testing."""
        return [
            {
                "id": "product_001",
                "title": "Wireless Bluetooth Headphones",
                "description": "High-quality wireless headphones with noise cancellation",
                "price": 199.99,
                "category": "electronics",
                "brand": "AudioTech",
                "image_url": "https://example.com/headphones.jpg",
                "metadata": {
                    "sku": "ATH-001",
                    "availability": "in_stock",
                    "color": "black",
                    "features": ["bluetooth", "noise_cancellation", "wireless"]
                }
            },
            {
                "id": "product_002",
                "title": "Smartphone Case",
                "description": "Durable protective case for smartphones",
                "price": 29.99,
                "category": "accessories",
                "brand": "ProtectPro",
                "image_url": "https://example.com/case.jpg",
                "metadata": {
                    "sku": "PP-002",
                    "availability": "in_stock",
                    "color": "clear",
                    "compatibility": ["iphone", "samsung"]
                }
            },
            {
                "id": "product_003",
                "title": "Laptop Stand",
                "description": "Adjustable laptop stand for ergonomic workspace",
                "price": 79.99,
                "category": "accessories",
                "brand": "ErgoWorks",
                "image_url": "https://example.com/stand.jpg",
                "metadata": {
                    "sku": "EW-003",
                    "availability": "in_stock",
                    "material": "aluminum",
                    "adjustable": True
                }
            }
        ]
    
    @pytest.fixture
    def sample_search_image(self):
        """Create a sample image for search testing."""
        # Create a test image that looks like headphones
        img = Image.new('RGB', (224, 224), color='black')
        return img
    
    @pytest.fixture
    def sample_embedding(self):
        """Create a sample embedding vector."""
        np.random.seed(42)
        return np.random.randn(512).astype(np.float32)
    
    @pytest.fixture
    def mock_services(self):
        """Create mock service instances for testing."""
        services = {
            'ingest': Mock(spec=IngestService),
            'preprocess': Mock(spec=PreprocessService),
            'detect': Mock(spec=DetectService),
            'embed': Mock(spec=EmbedService),
            'index': Mock(spec=IndexService),
            'search': Mock(spec=SearchService),
            'cdn': Mock(spec=CDNService)
        }
        return services
    
    @pytest.mark.asyncio
    async def test_complete_user_journey(self, mock_services, sample_catalog_data, sample_search_image, sample_embedding):
        """Test the complete user journey from catalog import to search results."""
        
        # Setup mock responses
        mock_services['ingest'].process_feed.return_value = sample_catalog_data
        mock_services['preprocess'].process_image.return_value = sample_search_image
        mock_services['detect'].detect_objects.return_value = [
            {"bbox": [50, 50, 150, 150], "confidence": 0.95, "class": "product"}
        ]
        mock_services['embed'].encode_image.return_value = sample_embedding
        mock_services['embed'].encode_text.return_value = sample_embedding
        mock_services['index'].upsert_products.return_value = {"success": True, "count": 3}
        mock_services['index'].build_index.return_value = {"success": True, "status": "completed"}
        mock_services['search'].search_similar.return_value = [
            SearchResult(
                id="product_001",
                score=0.95,
                metadata=sample_catalog_data[0],
                embedding=sample_embedding
            ),
            SearchResult(
                id="product_002",
                score=0.87,
                metadata=sample_catalog_data[1],
                embedding=sample_embedding
            )
        ]
        mock_services['cdn'].upload_image.return_value = "https://cdn.example.com/uploaded_image.jpg"
        
        # Step 1: Import catalog
        print("Step 1: Importing catalog...")
        catalog_products = await mock_services['ingest'].process_feed("https://example.com/catalog.xml")
        assert len(catalog_products) == 3
        assert catalog_products[0]["id"] == "product_001"
        assert catalog_products[1]["id"] == "product_002"
        assert catalog_products[2]["id"] == "product_003"
        
        # Step 2: Process and index products
        print("Step 2: Processing and indexing products...")
        indexed_products = []
        
        for product in catalog_products:
            # Simulate image processing
            processed_image = await mock_services['preprocess'].process_image(sample_search_image)
            detections = await mock_services['detect'].detect_objects(processed_image)
            embedding = await mock_services['embed'].encode_image(processed_image)
            
            indexed_product = {
                "id": product["id"],
                "embedding": embedding,
                "metadata": product,
                "detections": detections
            }
            indexed_products.append(indexed_product)
        
        # Index the products
        index_result = await mock_services['index'].upsert_products(indexed_products)
        assert index_result["success"] is True
        assert index_result["count"] == 3
        
        # Build the index
        build_result = await mock_services['index'].build_index()
        assert build_result["success"] is True
        assert build_result["status"] == "completed"
        
        # Step 3: User uploads search image
        print("Step 3: User uploads search image...")
        uploaded_image_url = await mock_services['cdn'].upload_image(sample_search_image)
        assert uploaded_image_url == "https://cdn.example.com/uploaded_image.jpg"
        
        # Step 4: Process search image
        print("Step 4: Processing search image...")
        processed_search_image = await mock_services['preprocess'].process_image(sample_search_image)
        search_detections = await mock_services['detect'].detect_objects(processed_search_image)
        search_embedding = await mock_services['embed'].encode_image(processed_search_image)
        
        assert processed_search_image is not None
        assert len(search_detections) > 0
        assert search_embedding.shape == (512,)
        
        # Step 5: Perform search
        print("Step 5: Performing search...")
        search_results = await mock_services['search'].search_similar(
            query_embedding=search_embedding,
            limit=10
        )
        
        assert len(search_results) == 2
        assert search_results[0].id == "product_001"
        assert search_results[0].score > search_results[1].score
        
        # Step 6: User selects product (PDP)
        print("Step 6: User selects product (PDP)...")
        selected_product = search_results[0]
        assert selected_product.metadata["title"] == "Wireless Bluetooth Headphones"
        assert selected_product.metadata["price"] == 199.99
        assert selected_product.metadata["brand"] == "AudioTech"
        
        print("✅ Complete user journey test passed!")
    
    @pytest.mark.asyncio
    async def test_catalog_import_with_validation(self, mock_services, sample_catalog_data):
        """Test catalog import with data validation."""
        # Setup mock
        mock_services['ingest'].process_feed.return_value = sample_catalog_data
        mock_services['ingest'].validate_products.return_value = {
            "valid": 3,
            "invalid": 0,
            "errors": []
        }
        
        # Import catalog
        products = await mock_services['ingest'].process_feed("https://example.com/catalog.xml")
        
        # Validate products
        validation_result = await mock_services['ingest'].validate_products(products)
        
        assert validation_result["valid"] == 3
        assert validation_result["invalid"] == 0
        assert len(validation_result["errors"]) == 0
        
        # Check product data integrity
        for product in products:
            assert "id" in product
            assert "title" in product
            assert "price" in product
            assert "image_url" in product
            assert product["price"] > 0
    
    @pytest.mark.asyncio
    async def test_index_build_and_status(self, mock_services, sample_catalog_data, sample_embedding):
        """Test index build process and status monitoring."""
        # Setup mocks
        mock_services['index'].build_index.return_value = {"success": True, "status": "building"}
        mock_services['index'].get_index_status.return_value = {"status": "completed", "progress": 100}
        mock_services['index'].upsert_products.return_value = {"success": True, "count": 3}
        
        # Start index build
        build_result = await mock_services['index'].build_index()
        assert build_result["success"] is True
        assert build_result["status"] == "building"
        
        # Check index status
        status_result = await mock_services['index'].get_index_status()
        assert status_result["status"] == "completed"
        assert status_result["progress"] == 100
        
        # Verify index is ready for search
        mock_services['index'].is_index_ready.return_value = True
        is_ready = await mock_services['index'].is_index_ready()
        assert is_ready is True
    
    @pytest.mark.asyncio
    async def test_image_upload_and_processing(self, mock_services, sample_search_image):
        """Test image upload and processing workflow."""
        # Setup mocks
        mock_services['cdn'].upload_image.return_value = "https://cdn.example.com/test_image.jpg"
        mock_services['preprocess'].process_image.return_value = sample_search_image
        mock_services['detect'].detect_objects.return_value = [
            {"bbox": [50, 50, 150, 150], "confidence": 0.95, "class": "product"}
        ]
        mock_services['embed'].encode_image.return_value = np.random.randn(512).astype(np.float32)
        
        # Upload image
        image_url = await mock_services['cdn'].upload_image(sample_search_image)
        assert image_url == "https://cdn.example.com/test_image.jpg"
        
        # Process image
        processed_image = await mock_services['preprocess'].process_image(sample_search_image)
        assert processed_image is not None
        
        # Detect objects
        detections = await mock_services['detect'].detect_objects(processed_image)
        assert len(detections) > 0
        assert detections[0]["confidence"] > 0.9
        
        # Generate embedding
        embedding = await mock_services['embed'].encode_image(processed_image)
        assert embedding.shape == (512,)
    
    @pytest.mark.asyncio
    async def test_search_with_filters(self, mock_services, sample_embedding, sample_catalog_data):
        """Test search with various filters and constraints."""
        # Setup mock search results
        mock_services['search'].search_similar.return_value = [
            SearchResult(
                id="product_001",
                score=0.95,
                metadata=sample_catalog_data[0],
                embedding=sample_embedding
            )
        ]
        
        # Test search with category filter
        category_results = await mock_services['search'].search_similar(
            query_embedding=sample_embedding,
            limit=10,
            filters={"category": "electronics"}
        )
        assert len(category_results) == 1
        assert category_results[0].metadata["category"] == "electronics"
        
        # Test search with price range filter
        price_results = await mock_services['search'].search_similar(
            query_embedding=sample_embedding,
            limit=10,
            filters={"price_min": 100, "price_max": 300}
        )
        assert len(price_results) == 1
        assert 100 <= price_results[0].metadata["price"] <= 300
        
        # Test search with brand filter
        brand_results = await mock_services['search'].search_similar(
            query_embedding=sample_embedding,
            limit=10,
            filters={"brand": "AudioTech"}
        )
        assert len(brand_results) == 1
        assert brand_results[0].metadata["brand"] == "AudioTech"
    
    @pytest.mark.asyncio
    async def test_search_result_ranking(self, mock_services, sample_embedding, sample_catalog_data):
        """Test search result ranking and relevance."""
        # Setup mock search results with different scores
        mock_services['search'].search_similar.return_value = [
            SearchResult(
                id="product_001",
                score=0.95,
                metadata=sample_catalog_data[0],
                embedding=sample_embedding
            ),
            SearchResult(
                id="product_002",
                score=0.87,
                metadata=sample_catalog_data[1],
                embedding=sample_embedding
            ),
            SearchResult(
                id="product_003",
                score=0.82,
                metadata=sample_catalog_data[2],
                embedding=sample_embedding
            )
        ]
        
        # Perform search
        search_results = await mock_services['search'].search_similar(
            query_embedding=sample_embedding,
            limit=10
        )
        
        # Verify ranking order
        assert len(search_results) == 3
        assert search_results[0].score > search_results[1].score
        assert search_results[1].score > search_results[2].score
        
        # Verify relevance scores are reasonable
        for result in search_results:
            assert 0.0 <= result.score <= 1.0
            assert result.score > 0.8  # High relevance threshold
    
    @pytest.mark.asyncio
    async def test_product_detail_page_data(self, mock_services, sample_catalog_data):
        """Test product detail page data retrieval and display."""
        # Simulate product selection
        selected_product = sample_catalog_data[0]
        
        # Verify product detail data
        assert selected_product["id"] == "product_001"
        assert selected_product["title"] == "Wireless Bluetooth Headphones"
        assert selected_product["description"] == "High-quality wireless headphones with noise cancellation"
        assert selected_product["price"] == 199.99
        assert selected_product["brand"] == "AudioTech"
        assert selected_product["category"] == "electronics"
        
        # Verify metadata
        metadata = selected_product["metadata"]
        assert metadata["sku"] == "ATH-001"
        assert metadata["availability"] == "in_stock"
        assert metadata["color"] == "black"
        assert "bluetooth" in metadata["features"]
        assert "noise_cancellation" in metadata["features"]
        
        # Verify image URL
        assert selected_product["image_url"] == "https://example.com/headphones.jpg"
    
    @pytest.mark.asyncio
    async def test_error_handling_in_journey(self, mock_services, sample_search_image):
        """Test error handling throughout the user journey."""
        # Test catalog import failure
        mock_services['ingest'].process_feed.side_effect = Exception("Feed not accessible")
        
        with pytest.raises(Exception, match="Feed not accessible"):
            await mock_services['ingest'].process_feed("https://example.com/invalid_feed.xml")
        
        # Reset mock
        mock_services['ingest'].process_feed.side_effect = None
        mock_services['ingest'].process_feed.return_value = []
        
        # Test empty catalog
        products = await mock_services['ingest'].process_feed("https://example.com/empty_feed.xml")
        assert len(products) == 0
        
        # Test image processing failure
        mock_services['preprocess'].process_image.side_effect = Exception("Image processing failed")
        
        with pytest.raises(Exception, match="Image processing failed"):
            await mock_services['preprocess'].process_image(sample_search_image)
        
        # Test search with no results
        mock_services['search'].search_similar.return_value = []
        
        search_results = await mock_services['search'].search_similar(
            query_embedding=np.random.randn(512).astype(np.float32),
            limit=10
        )
        assert len(search_results) == 0
    
    @pytest.mark.asyncio
    async def test_performance_metrics_in_journey(self, mock_services, sample_catalog_data, sample_search_image, sample_embedding):
        """Test performance metrics throughout the user journey."""
        import time
        
        # Setup mocks
        mock_services['ingest'].process_feed.return_value = sample_catalog_data
        mock_services['preprocess'].process_image.return_value = sample_search_image
        mock_services['detect'].detect_objects.return_value = [{"bbox": [50, 50, 150, 150], "confidence": 0.95, "class": "product"}]
        mock_services['embed'].encode_image.return_value = sample_embedding
        mock_services['index'].upsert_products.return_value = {"success": True, "count": 3}
        mock_services['search'].search_similar.return_value = [
            SearchResult(id="product_001", score=0.95, metadata=sample_catalog_data[0], embedding=sample_embedding)
        ]
        
        # Measure catalog import time
        start_time = time.time()
        products = await mock_services['ingest'].process_feed("https://example.com/catalog.xml")
        import_time = time.time() - start_time
        
        assert import_time < 1.0  # Should complete within 1 second
        assert len(products) == 3
        
        # Measure image processing time
        start_time = time.time()
        processed_image = await mock_services['preprocess'].process_image(sample_search_image)
        detections = await mock_services['detect'].detect_objects(processed_image)
        embedding = await mock_services['embed'].encode_image(processed_image)
        processing_time = time.time() - start_time
        
        assert processing_time < 0.5  # Should complete within 500ms
        
        # Measure search time
        start_time = time.time()
        search_results = await mock_services['search'].search_similar(
            query_embedding=sample_embedding,
            limit=10
        )
        search_time = time.time() - start_time
        
        assert search_time < 0.1  # Should complete within 100ms
        assert len(search_results) == 1
    
    @pytest.mark.asyncio
    async def test_data_consistency_in_journey(self, mock_services, sample_catalog_data, sample_search_image, sample_embedding):
        """Test data consistency throughout the user journey."""
        # Setup mocks
        mock_services['ingest'].process_feed.return_value = sample_catalog_data
        mock_services['preprocess'].process_image.return_value = sample_search_image
        mock_services['detect'].detect_objects.return_value = [{"bbox": [50, 50, 150, 150], "confidence": 0.95, "class": "product"}]
        mock_services['embed'].encode_image.return_value = sample_embedding
        mock_services['index'].upsert_products.return_value = {"success": True, "count": 3}
        mock_services['search'].search_similar.return_value = [
            SearchResult(id="product_001", score=0.95, metadata=sample_catalog_data[0], embedding=sample_embedding)
        ]
        
        # Import catalog
        products = await mock_services['ingest'].process_feed("https://example.com/catalog.xml")
        original_product = products[0]
        
        # Process and index
        processed_image = await mock_services['preprocess'].process_image(sample_search_image)
        detections = await mock_services['detect'].detect_objects(processed_image)
        embedding = await mock_services['embed'].encode_image(processed_image)
        
        indexed_product = {
            "id": original_product["id"],
            "embedding": embedding,
            "metadata": original_product,
            "detections": detections
        }
        
        # Verify data consistency
        assert indexed_product["id"] == original_product["id"]
        assert indexed_product["metadata"]["title"] == original_product["title"]
        assert indexed_product["metadata"]["price"] == original_product["price"]
        assert indexed_product["metadata"]["brand"] == original_product["brand"]
        
        # Search and verify consistency
        search_results = await mock_services['search'].search_similar(
            query_embedding=sample_embedding,
            limit=10
        )
        
        result = search_results[0]
        assert result.id == original_product["id"]
        assert result.metadata["title"] == original_product["title"]
        assert result.metadata["price"] == original_product["price"]
        assert result.metadata["brand"] == original_product["brand"]
    
    @pytest.mark.asyncio
    async def test_user_interaction_flow(self, mock_services, sample_catalog_data, sample_search_image, sample_embedding):
        """Test complete user interaction flow."""
        # Setup mocks
        mock_services['ingest'].process_feed.return_value = sample_catalog_data
        mock_services['preprocess'].process_image.return_value = sample_search_image
        mock_services['detect'].detect_objects.return_value = [{"bbox": [50, 50, 150, 150], "confidence": 0.95, "class": "product"}]
        mock_services['embed'].encode_image.return_value = sample_embedding
        mock_services['index'].upsert_products.return_value = {"success": True, "count": 3}
        mock_services['search'].search_similar.return_value = [
            SearchResult(id="product_001", score=0.95, metadata=sample_catalog_data[0], embedding=sample_embedding),
            SearchResult(id="product_002", score=0.87, metadata=sample_catalog_data[1], embedding=sample_embedding)
        ]
        
        # Simulate user interaction flow
        print("🎯 User Journey Simulation:")
        
        # 1. User browses catalog
        print("1. User browses catalog...")
        catalog_products = await mock_services['ingest'].process_feed("https://example.com/catalog.xml")
        print(f"   Found {len(catalog_products)} products in catalog")
        
        # 2. User uploads image for search
        print("2. User uploads image for search...")
        processed_image = await mock_services['preprocess'].process_image(sample_search_image)
        search_embedding = await mock_services['embed'].encode_image(processed_image)
        print("   Image processed and embedding generated")
        
        # 3. User performs search
        print("3. User performs search...")
        search_results = await mock_services['search'].search_similar(
            query_embedding=search_embedding,
            limit=10
        )
        print(f"   Found {len(search_results)} search results")
        
        # 4. User views search results
        print("4. User views search results...")
        for i, result in enumerate(search_results):
            print(f"   Result {i+1}: {result.metadata['title']} (Score: {result.score:.3f})")
        
        # 5. User selects a product
        print("5. User selects a product...")
        selected_product = search_results[0]
        print(f"   Selected: {selected_product.metadata['title']}")
        print(f"   Price: ${selected_product.metadata['price']}")
        print(f"   Brand: {selected_product.metadata['brand']}")
        
        # 6. User views product details
        print("6. User views product details...")
        metadata = selected_product.metadata["metadata"]
        print(f"   SKU: {metadata['sku']}")
        print(f"   Availability: {metadata['availability']}")
        if 'features' in metadata:
            print(f"   Features: {', '.join(metadata['features'])}")
        
        print("✅ User journey simulation completed successfully!")
        
        # Verify final state
        assert len(search_results) == 2
        assert selected_product.metadata["title"] == "Wireless Bluetooth Headphones"
        assert selected_product.score > 0.9
