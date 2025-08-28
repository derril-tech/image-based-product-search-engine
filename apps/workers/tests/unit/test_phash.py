# Created automatically by Cursor AI (2024-12-19)

import pytest
import numpy as np
from PIL import Image
import io
from ..src.services.preprocess_service import PreprocessService


class TestPerceptualHash:
    """Test suite for perceptual hash functionality."""
    
    @pytest.fixture
    def preprocess_service(self):
        """Create a preprocess service instance for testing."""
        return PreprocessService()
    
    @pytest.fixture
    def sample_image(self):
        """Create a sample test image."""
        # Create a simple 64x64 test image
        img_array = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        return img
    
    @pytest.fixture
    def similar_image(self, sample_image):
        """Create a slightly modified version of the sample image."""
        # Apply slight brightness adjustment
        img_array = np.array(sample_image)
        img_array = np.clip(img_array * 1.1, 0, 255).astype(np.uint8)
        return Image.fromarray(img_array)
    
    @pytest.fixture
    def different_image(self):
        """Create a completely different test image."""
        # Create a different random image
        img_array = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        return Image.fromarray(img_array)
    
    def test_phash_generation(self, preprocess_service, sample_image):
        """Test that pHash generation produces consistent results."""
        # Generate pHash for the same image multiple times
        hash1 = preprocess_service.generate_phash(sample_image)
        hash2 = preprocess_service.generate_phash(sample_image)
        
        # Should be identical
        assert hash1 == hash2
        assert len(hash1) == 64  # 8x8 = 64 bits
        assert isinstance(hash1, str)
    
    def test_phash_similarity(self, preprocess_service, sample_image, similar_image):
        """Test that similar images have similar pHash values."""
        hash1 = preprocess_service.generate_phash(sample_image)
        hash2 = preprocess_service.generate_phash(similar_image)
        
        # Calculate Hamming distance
        distance = preprocess_service.calculate_hamming_distance(hash1, hash2)
        
        # Similar images should have small Hamming distance
        assert distance <= 10  # Threshold for similar images
        assert distance >= 0
    
    def test_phash_difference(self, preprocess_service, sample_image, different_image):
        """Test that different images have different pHash values."""
        hash1 = preprocess_service.generate_phash(sample_image)
        hash2 = preprocess_service.generate_phash(different_image)
        
        # Calculate Hamming distance
        distance = preprocess_service.calculate_hamming_distance(hash1, hash2)
        
        # Different images should have larger Hamming distance
        assert distance > 10  # Should be more different than similar images
        assert distance <= 64  # Maximum possible distance
    
    def test_hamming_distance_calculation(self, preprocess_service):
        """Test Hamming distance calculation."""
        # Test with known values
        hash1 = "11110000"
        hash2 = "11110001"
        distance = preprocess_service.calculate_hamming_distance(hash1, hash2)
        assert distance == 1
        
        # Test with identical hashes
        distance = preprocess_service.calculate_hamming_distance(hash1, hash1)
        assert distance == 0
        
        # Test with completely different hashes
        hash3 = "00001111"
        distance = preprocess_service.calculate_hamming_distance(hash1, hash3)
        assert distance == 8
    
    def test_phash_with_different_sizes(self, preprocess_service):
        """Test pHash generation with different image sizes."""
        # Create images of different sizes
        sizes = [(32, 32), (64, 64), (128, 128), (256, 256)]
        hashes = []
        
        for size in sizes:
            img_array = np.random.randint(0, 255, (*size, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            hash_val = preprocess_service.generate_phash(img)
            hashes.append(hash_val)
        
        # All hashes should be the same length (64 bits)
        for hash_val in hashes:
            assert len(hash_val) == 64
    
    def test_phash_with_different_formats(self, preprocess_service):
        """Test pHash generation with different image formats."""
        # Create test image
        img_array = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        original_img = Image.fromarray(img_array)
        
        # Convert to different formats
        formats = ['RGB', 'RGBA', 'L', 'LA']
        hashes = []
        
        for format_name in formats:
            if format_name in ['L', 'LA']:
                # Convert to grayscale
                img = original_img.convert(format_name)
            else:
                img = original_img.convert(format_name)
            
            hash_val = preprocess_service.generate_phash(img)
            hashes.append(hash_val)
        
        # All hashes should be the same length
        for hash_val in hashes:
            assert len(hash_val) == 64
    
    def test_phash_edge_cases(self, preprocess_service):
        """Test pHash generation with edge cases."""
        # Test with very small image
        small_img = Image.fromarray(np.random.randint(0, 255, (8, 8, 3), dtype=np.uint8))
        hash_val = preprocess_service.generate_phash(small_img)
        assert len(hash_val) == 64
        
        # Test with very large image
        large_img = Image.fromarray(np.random.randint(0, 255, (1024, 1024, 3), dtype=np.uint8))
        hash_val = preprocess_service.generate_phash(large_img)
        assert len(hash_val) == 64
        
        # Test with single color image
        single_color = Image.new('RGB', (64, 64), color=(255, 0, 0))
        hash_val = preprocess_service.generate_phash(single_color)
        assert len(hash_val) == 64
    
    def test_phash_similarity_threshold(self, preprocess_service):
        """Test pHash similarity threshold detection."""
        # Create base image
        base_img = Image.fromarray(np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8))
        base_hash = preprocess_service.generate_phash(base_img)
        
        # Test with different thresholds
        thresholds = [5, 10, 15, 20]
        
        for threshold in thresholds:
            # Create slightly modified image
            img_array = np.array(base_img)
            noise = np.random.normal(0, 10, img_array.shape)
            modified_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
            modified_img = Image.fromarray(modified_array)
            modified_hash = preprocess_service.generate_phash(modified_img)
            
            distance = preprocess_service.calculate_hamming_distance(base_hash, modified_hash)
            is_similar = preprocess_service.is_phash_similar(base_hash, modified_hash, threshold)
            
            # Should be similar if distance is within threshold
            assert is_similar == (distance <= threshold)
    
    def test_phash_performance(self, preprocess_service):
        """Test pHash generation performance."""
        import time
        
        # Create test image
        img = Image.fromarray(np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8))
        
        # Measure generation time
        start_time = time.time()
        for _ in range(100):
            preprocess_service.generate_phash(img)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 100
        
        # Should be reasonably fast (less than 10ms per hash)
        assert avg_time < 0.01
    
    def test_phash_consistency_across_runs(self, preprocess_service):
        """Test that pHash is consistent across different runs."""
        # Create test image
        img = Image.fromarray(np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8))
        
        # Generate hashes multiple times
        hashes = []
        for _ in range(10):
            hash_val = preprocess_service.generate_phash(img)
            hashes.append(hash_val)
        
        # All hashes should be identical
        assert len(set(hashes)) == 1
        assert hashes[0] == hashes[-1]
