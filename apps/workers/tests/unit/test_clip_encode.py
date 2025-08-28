# Created automatically by Cursor AI (2024-12-19)

import pytest
import numpy as np
from PIL import Image
import torch
from unittest.mock import Mock, patch
from ..src.services.embedding_service import EmbeddingService


class TestCLIPEncodeWrapper:
    """Test suite for CLIP encoding wrapper functionality."""
    
    @pytest.fixture
    def embedding_service(self):
        """Create an embedding service instance for testing."""
        return EmbeddingService()
    
    @pytest.fixture
    def sample_image(self):
        """Create a sample test image."""
        # Create a simple 224x224 test image (CLIP input size)
        img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        return Image.fromarray(img_array)
    
    @pytest.fixture
    def sample_texts(self):
        """Create sample text inputs for testing."""
        return [
            "a red car",
            "a blue bicycle",
            "a person walking",
            "a cat sitting on a chair"
        ]
    
    @pytest.fixture
    def mock_clip_model(self):
        """Create a mock CLIP model for testing."""
        mock_model = Mock()
        
        # Mock the model's forward pass
        def mock_forward(**kwargs):
            # Return mock embeddings
            if 'input_ids' in kwargs:  # Text input
                batch_size = kwargs['input_ids'].shape[0]
                return Mock(logits_per_image=torch.randn(batch_size, 512))
            else:  # Image input
                batch_size = kwargs['pixel_values'].shape[0]
                return Mock(logits_per_text=torch.randn(batch_size, 512))
        
        mock_model.forward = mock_forward
        mock_model.eval.return_value = mock_model
        
        return mock_model
    
    def test_clip_model_initialization(self, embedding_service):
        """Test CLIP model initialization."""
        # Test that the model is properly initialized
        assert embedding_service.clip_model is not None
        assert embedding_service.clip_processor is not None
        
        # Test model is in evaluation mode
        assert embedding_service.clip_model.training == False
    
    def test_image_encoding(self, embedding_service, sample_image):
        """Test image encoding functionality."""
        # Encode the image
        embedding = embedding_service.encode_image(sample_image)
        
        # Check output format
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (512,)  # CLIP embedding dimension
        assert embedding.dtype == np.float32
        
        # Check embedding values are reasonable
        assert np.all(np.isfinite(embedding))
        assert np.linalg.norm(embedding) > 0
    
    def test_text_encoding(self, embedding_service, sample_texts):
        """Test text encoding functionality."""
        # Encode single text
        single_embedding = embedding_service.encode_text(sample_texts[0])
        
        # Check output format
        assert isinstance(single_embedding, np.ndarray)
        assert single_embedding.shape == (512,)
        assert single_embedding.dtype == np.float32
        
        # Encode multiple texts
        batch_embeddings = embedding_service.encode_texts(sample_texts)
        
        # Check batch output format
        assert isinstance(batch_embeddings, np.ndarray)
        assert batch_embeddings.shape == (len(sample_texts), 512)
        assert batch_embeddings.dtype == np.float32
        
        # Check all embeddings are valid
        for embedding in batch_embeddings:
            assert np.all(np.isfinite(embedding))
            assert np.linalg.norm(embedding) > 0
    
    def test_encoding_consistency(self, embedding_service, sample_image, sample_texts):
        """Test that encoding produces consistent results."""
        # Encode the same image multiple times
        embedding1 = embedding_service.encode_image(sample_image)
        embedding2 = embedding_service.encode_image(sample_image)
        
        # Should be identical (within numerical precision)
        assert np.allclose(embedding1, embedding2, rtol=1e-5)
        
        # Encode the same text multiple times
        text_embedding1 = embedding_service.encode_text(sample_texts[0])
        text_embedding2 = embedding_service.encode_text(sample_texts[0])
        
        # Should be identical
        assert np.allclose(text_embedding1, text_embedding2, rtol=1e-5)
    
    def test_encoding_normalization(self, embedding_service, sample_image, sample_texts):
        """Test that embeddings are properly normalized."""
        # Check image embedding normalization
        image_embedding = embedding_service.encode_image(sample_image)
        norm = np.linalg.norm(image_embedding)
        
        # CLIP embeddings are typically normalized
        assert abs(norm - 1.0) < 0.1  # Allow some tolerance
        
        # Check text embedding normalization
        text_embedding = embedding_service.encode_text(sample_texts[0])
        norm = np.linalg.norm(text_embedding)
        
        assert abs(norm - 1.0) < 0.1
    
    def test_similarity_calculation(self, embedding_service, sample_image, sample_texts):
        """Test similarity calculation between image and text embeddings."""
        # Encode image and text
        image_embedding = embedding_service.encode_image(sample_image)
        text_embedding = embedding_service.encode_text(sample_texts[0])
        
        # Calculate similarity
        similarity = embedding_service.calculate_similarity(image_embedding, text_embedding)
        
        # Check similarity is in reasonable range
        assert isinstance(similarity, float)
        assert -1.0 <= similarity <= 1.0  # Cosine similarity range
        assert np.isfinite(similarity)
    
    def test_batch_similarity_calculation(self, embedding_service, sample_image, sample_texts):
        """Test batch similarity calculation."""
        # Encode image and multiple texts
        image_embedding = embedding_service.encode_image(sample_image)
        text_embeddings = embedding_service.encode_texts(sample_texts)
        
        # Calculate similarities
        similarities = embedding_service.calculate_batch_similarity(image_embedding, text_embeddings)
        
        # Check output format
        assert isinstance(similarities, np.ndarray)
        assert similarities.shape == (len(sample_texts),)
        assert similarities.dtype == np.float32
        
        # Check all similarities are in valid range
        for similarity in similarities:
            assert -1.0 <= similarity <= 1.0
            assert np.isfinite(similarity)
    
    def test_encoding_with_different_image_sizes(self, embedding_service):
        """Test encoding with different image sizes."""
        sizes = [(64, 64), (128, 128), (224, 224), (256, 256), (512, 512)]
        
        for size in sizes:
            # Create image of different size
            img_array = np.random.randint(0, 255, (*size, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            
            # Should be able to encode regardless of size
            embedding = embedding_service.encode_image(img)
            
            assert embedding.shape == (512,)
            assert np.all(np.isfinite(embedding))
    
    def test_encoding_with_different_text_lengths(self, embedding_service):
        """Test encoding with different text lengths."""
        texts = [
            "short",
            "medium length text",
            "this is a much longer text that should still be encoded properly",
            "a" * 1000  # Very long text
        ]
        
        for text in texts:
            embedding = embedding_service.encode_text(text)
            
            assert embedding.shape == (512,)
            assert np.all(np.isfinite(embedding))
    
    def test_encoding_edge_cases(self, embedding_service):
        """Test encoding with edge cases."""
        # Test with empty text
        empty_embedding = embedding_service.encode_text("")
        assert empty_embedding.shape == (512,)
        assert np.all(np.isfinite(empty_embedding))
        
        # Test with very small image
        small_img = Image.fromarray(np.random.randint(0, 255, (1, 1, 3), dtype=np.uint8))
        small_embedding = embedding_service.encode_image(small_img)
        assert small_embedding.shape == (512,)
        assert np.all(np.isfinite(small_embedding))
        
        # Test with single color image
        single_color = Image.new('RGB', (224, 224), color=(255, 0, 0))
        color_embedding = embedding_service.encode_image(single_color)
        assert color_embedding.shape == (512,)
        assert np.all(np.isfinite(color_embedding))
    
    def test_encoding_performance(self, embedding_service, sample_image, sample_texts):
        """Test encoding performance."""
        import time
        
        # Test image encoding performance
        start_time = time.time()
        for _ in range(10):
            embedding_service.encode_image(sample_image)
        image_time = (time.time() - start_time) / 10
        
        # Should be reasonably fast (less than 100ms per image)
        assert image_time < 0.1
        
        # Test text encoding performance
        start_time = time.time()
        for _ in range(10):
            embedding_service.encode_text(sample_texts[0])
        text_time = (time.time() - start_time) / 10
        
        # Should be reasonably fast (less than 50ms per text)
        assert text_time < 0.05
    
    def test_encoding_memory_usage(self, embedding_service, sample_image, sample_texts):
        """Test that encoding doesn't cause memory leaks."""
        import gc
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform multiple encoding operations
        for _ in range(100):
            image_embedding = embedding_service.encode_image(sample_image)
            text_embedding = embedding_service.encode_text(sample_texts[0])
            del image_embedding, text_embedding
        
        # Force garbage collection
        gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100
    
    def test_encoding_with_gpu(self, embedding_service, sample_image, sample_texts):
        """Test encoding with GPU if available."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")
        
        # Move model to GPU
        embedding_service.clip_model = embedding_service.clip_model.cuda()
        
        # Test encoding on GPU
        image_embedding = embedding_service.encode_image(sample_image)
        text_embedding = embedding_service.encode_text(sample_texts[0])
        
        # Check outputs are still numpy arrays
        assert isinstance(image_embedding, np.ndarray)
        assert isinstance(text_embedding, np.ndarray)
        assert image_embedding.shape == (512,)
        assert text_embedding.shape == (512,)
        
        # Move model back to CPU
        embedding_service.clip_model = embedding_service.clip_model.cpu()
    
    def test_encoding_error_handling(self, embedding_service):
        """Test error handling in encoding."""
        # Test with invalid image
        with pytest.raises(Exception):
            embedding_service.encode_image(None)
        
        # Test with invalid text
        with pytest.raises(Exception):
            embedding_service.encode_text(None)
        
        # Test with corrupted image data
        corrupted_img = Image.fromarray(np.zeros((224, 224, 3), dtype=np.uint8))
        # This should not raise an exception
        embedding = embedding_service.encode_image(corrupted_img)
        assert embedding.shape == (512,)
    
    def test_encoding_with_special_characters(self, embedding_service):
        """Test encoding with special characters in text."""
        special_texts = [
            "text with spaces",
            "text-with-hyphens",
            "text_with_underscores",
            "text with numbers 123",
            "text with symbols !@#$%^&*()",
            "text with unicode: café, naïve, résumé",
            "text with emojis: 🚗 🚲 👤 🐱"
        ]
        
        for text in special_texts:
            embedding = embedding_service.encode_text(text)
            assert embedding.shape == (512,)
            assert np.all(np.isfinite(embedding))
    
    def test_encoding_batch_consistency(self, embedding_service, sample_texts):
        """Test that batch encoding produces same results as individual encoding."""
        # Encode texts individually
        individual_embeddings = []
        for text in sample_texts:
            embedding = embedding_service.encode_text(text)
            individual_embeddings.append(embedding)
        
        # Encode texts in batch
        batch_embeddings = embedding_service.encode_texts(sample_texts)
        
        # Compare results
        for i, (individual, batch) in enumerate(zip(individual_embeddings, batch_embeddings)):
            assert np.allclose(individual, batch, rtol=1e-5), f"Mismatch at index {i}"
    
    def test_encoding_with_different_precision(self, embedding_service, sample_image, sample_texts):
        """Test encoding with different precision settings."""
        # Test with float16 precision
        with patch.object(embedding_service.clip_model, 'half') as mock_half:
            mock_half.return_value = embedding_service.clip_model
            
            image_embedding = embedding_service.encode_image(sample_image, precision='float16')
            text_embedding = embedding_service.encode_text(sample_texts[0], precision='float16')
            
            assert image_embedding.shape == (512,)
            assert text_embedding.shape == (512,)
            assert image_embedding.dtype == np.float32  # Output should still be float32
            assert text_embedding.dtype == np.float32
