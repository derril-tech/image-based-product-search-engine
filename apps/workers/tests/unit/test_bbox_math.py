# Created automatically by Cursor AI (2024-12-19)

import pytest
import numpy as np
from ..src.services.detect_service import DetectService


class TestBoundingBoxMath:
    """Test suite for bounding box mathematics."""
    
    @pytest.fixture
    def detect_service(self):
        """Create a detect service instance for testing."""
        return DetectService()
    
    @pytest.fixture
    def sample_bbox(self):
        """Create a sample bounding box [x1, y1, x2, y2, confidence, class_id]."""
        return [10, 20, 50, 80, 0.95, 1]
    
    @pytest.fixture
    def overlapping_bbox(self):
        """Create a bounding box that overlaps with sample_bbox."""
        return [30, 40, 70, 100, 0.85, 1]
    
    @pytest.fixture
    def non_overlapping_bbox(self):
        """Create a bounding box that doesn't overlap with sample_bbox."""
        return [100, 100, 150, 150, 0.90, 1]
    
    def test_bbox_area_calculation(self, detect_service, sample_bbox):
        """Test bounding box area calculation."""
        area = detect_service.calculate_bbox_area(sample_bbox)
        expected_area = (50 - 10) * (80 - 20)  # width * height
        assert area == expected_area
        assert area > 0
    
    def test_bbox_intersection(self, detect_service, sample_bbox, overlapping_bbox):
        """Test bounding box intersection calculation."""
        intersection_area = detect_service.calculate_intersection_area(sample_bbox, overlapping_bbox)
        
        # Manual calculation
        x1 = max(10, 30)
        y1 = max(20, 40)
        x2 = min(50, 70)
        y2 = min(80, 100)
        expected_intersection = (x2 - x1) * (y2 - y1)
        
        assert intersection_area == expected_intersection
        assert intersection_area > 0
    
    def test_bbox_no_intersection(self, detect_service, sample_bbox, non_overlapping_bbox):
        """Test that non-overlapping bounding boxes have zero intersection."""
        intersection_area = detect_service.calculate_intersection_area(sample_bbox, non_overlapping_bbox)
        assert intersection_area == 0
    
    def test_bbox_union(self, detect_service, sample_bbox, overlapping_bbox):
        """Test bounding box union calculation."""
        union_area = detect_service.calculate_union_area(sample_bbox, overlapping_bbox)
        
        # Manual calculation
        area1 = detect_service.calculate_bbox_area(sample_bbox)
        area2 = detect_service.calculate_bbox_area(overlapping_bbox)
        intersection = detect_service.calculate_intersection_area(sample_bbox, overlapping_bbox)
        expected_union = area1 + area2 - intersection
        
        assert union_area == expected_union
        assert union_area > 0
    
    def test_iou_calculation(self, detect_service, sample_bbox, overlapping_bbox):
        """Test Intersection over Union (IoU) calculation."""
        iou = detect_service.calculate_iou(sample_bbox, overlapping_bbox)
        
        intersection = detect_service.calculate_intersection_area(sample_bbox, overlapping_bbox)
        union = detect_service.calculate_union_area(sample_bbox, overlapping_bbox)
        expected_iou = intersection / union
        
        assert abs(iou - expected_iou) < 1e-6
        assert 0 <= iou <= 1
    
    def test_iou_identical_boxes(self, detect_service, sample_bbox):
        """Test IoU calculation for identical bounding boxes."""
        iou = detect_service.calculate_iou(sample_bbox, sample_bbox)
        assert iou == 1.0
    
    def test_iou_no_overlap(self, detect_service, sample_bbox, non_overlapping_bbox):
        """Test IoU calculation for non-overlapping boxes."""
        iou = detect_service.calculate_iou(sample_bbox, non_overlapping_bbox)
        assert iou == 0.0
    
    def test_bbox_center_calculation(self, detect_service, sample_bbox):
        """Test bounding box center point calculation."""
        center_x, center_y = detect_service.calculate_bbox_center(sample_bbox)
        
        expected_center_x = (10 + 50) / 2
        expected_center_y = (20 + 80) / 2
        
        assert center_x == expected_center_x
        assert center_y == expected_center_y
    
    def test_bbox_width_height(self, detect_service, sample_bbox):
        """Test bounding box width and height calculation."""
        width = detect_service.calculate_bbox_width(sample_bbox)
        height = detect_service.calculate_bbox_height(sample_bbox)
        
        assert width == 40  # 50 - 10
        assert height == 60  # 80 - 20
        assert width > 0
        assert height > 0
    
    def test_bbox_aspect_ratio(self, detect_service, sample_bbox):
        """Test bounding box aspect ratio calculation."""
        aspect_ratio = detect_service.calculate_bbox_aspect_ratio(sample_bbox)
        
        width = detect_service.calculate_bbox_width(sample_bbox)
        height = detect_service.calculate_bbox_height(sample_bbox)
        expected_ratio = width / height
        
        assert abs(aspect_ratio - expected_ratio) < 1e-6
        assert aspect_ratio > 0
    
    def test_bbox_normalization(self, detect_service, sample_bbox):
        """Test bounding box normalization to [0, 1] range."""
        image_width, image_height = 200, 200
        normalized_bbox = detect_service.normalize_bbox(sample_bbox, image_width, image_height)
        
        expected_normalized = [
            10 / 200,  # x1
            20 / 200,  # y1
            50 / 200,  # x2
            80 / 200   # y2
        ]
        
        for i in range(4):
            assert abs(normalized_bbox[i] - expected_normalized[i]) < 1e-6
            assert 0 <= normalized_bbox[i] <= 1
    
    def test_bbox_denormalization(self, detect_service):
        """Test bounding box denormalization from [0, 1] range."""
        normalized_bbox = [0.1, 0.2, 0.5, 0.8]
        image_width, image_height = 200, 200
        
        denormalized_bbox = detect_service.denormalize_bbox(normalized_bbox, image_width, image_height)
        
        expected_denormalized = [20, 40, 100, 160]  # [0.1*200, 0.2*200, 0.5*200, 0.8*200]
        
        for i in range(4):
            assert denormalized_bbox[i] == expected_denormalized[i]
    
    def test_bbox_contains_point(self, detect_service, sample_bbox):
        """Test if a point is contained within a bounding box."""
        # Point inside the bbox
        point_inside = (30, 50)
        assert detect_service.bbox_contains_point(sample_bbox, point_inside)
        
        # Point outside the bbox
        point_outside = (100, 100)
        assert not detect_service.bbox_contains_point(sample_bbox, point_outside)
        
        # Point on the boundary
        point_boundary = (10, 20)
        assert detect_service.bbox_contains_point(sample_bbox, point_boundary)
    
    def test_bbox_distance(self, detect_service, sample_bbox, non_overlapping_bbox):
        """Test distance calculation between bounding boxes."""
        distance = detect_service.calculate_bbox_distance(sample_bbox, non_overlapping_bbox)
        
        # Manual calculation: distance between centers
        center1 = detect_service.calculate_bbox_center(sample_bbox)
        center2 = detect_service.calculate_bbox_center(non_overlapping_bbox)
        
        expected_distance = np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
        
        assert abs(distance - expected_distance) < 1e-6
        assert distance > 0
    
    def test_bbox_merge(self, detect_service, sample_bbox, overlapping_bbox):
        """Test merging of overlapping bounding boxes."""
        merged_bbox = detect_service.merge_bboxes(sample_bbox, overlapping_bbox)
        
        # Manual calculation
        x1 = min(10, 30)
        y1 = min(20, 40)
        x2 = max(50, 70)
        y2 = max(80, 100)
        
        assert merged_bbox[0] == x1
        assert merged_bbox[1] == y1
        assert merged_bbox[2] == x2
        assert merged_bbox[3] == y2
    
    def test_bbox_clip(self, detect_service):
        """Test bounding box clipping to image boundaries."""
        bbox = [10, 20, 150, 180]  # Partially outside image
        image_width, image_height = 100, 100
        
        clipped_bbox = detect_service.clip_bbox(bbox, image_width, image_height)
        
        assert clipped_bbox[0] == 10  # x1 stays the same
        assert clipped_bbox[1] == 20  # y1 stays the same
        assert clipped_bbox[2] == 100  # x2 clipped to image width
        assert clipped_bbox[3] == 100  # y2 clipped to image height
    
    def test_bbox_scale(self, detect_service, sample_bbox):
        """Test bounding box scaling."""
        scale_factor = 2.0
        scaled_bbox = detect_service.scale_bbox(sample_bbox, scale_factor)
        
        # Manual calculation
        center_x, center_y = detect_service.calculate_bbox_center(sample_bbox)
        width = detect_service.calculate_bbox_width(sample_bbox)
        height = detect_service.calculate_bbox_height(sample_bbox)
        
        new_width = width * scale_factor
        new_height = height * scale_factor
        
        expected_bbox = [
            center_x - new_width / 2,
            center_y - new_height / 2,
            center_x + new_width / 2,
            center_y + new_height / 2
        ]
        
        for i in range(4):
            assert abs(scaled_bbox[i] - expected_bbox[i]) < 1e-6
    
    def test_bbox_validation(self, detect_service):
        """Test bounding box validation."""
        # Valid bbox
        valid_bbox = [10, 20, 50, 80, 0.95, 1]
        assert detect_service.is_valid_bbox(valid_bbox)
        
        # Invalid bbox (x2 < x1)
        invalid_bbox1 = [50, 20, 10, 80, 0.95, 1]
        assert not detect_service.is_valid_bbox(invalid_bbox1)
        
        # Invalid bbox (y2 < y1)
        invalid_bbox2 = [10, 80, 50, 20, 0.95, 1]
        assert not detect_service.is_valid_bbox(invalid_bbox2)
        
        # Invalid bbox (negative coordinates)
        invalid_bbox3 = [-10, 20, 50, 80, 0.95, 1]
        assert not detect_service.is_valid_bbox(invalid_bbox3)
    
    def test_bbox_confidence_thresholding(self, detect_service):
        """Test bounding box confidence thresholding."""
        bboxes = [
            [10, 20, 50, 80, 0.95, 1],
            [30, 40, 70, 100, 0.85, 1],
            [100, 100, 150, 150, 0.75, 1],
            [200, 200, 250, 250, 0.65, 1]
        ]
        
        threshold = 0.8
        filtered_bboxes = detect_service.filter_bboxes_by_confidence(bboxes, threshold)
        
        # Only bboxes with confidence >= 0.8 should remain
        assert len(filtered_bboxes) == 2
        for bbox in filtered_bboxes:
            assert bbox[4] >= threshold
    
    def test_bbox_nms(self, detect_service):
        """Test Non-Maximum Suppression (NMS)."""
        bboxes = [
            [10, 20, 50, 80, 0.95, 1],
            [15, 25, 55, 85, 0.90, 1],  # Overlaps with first
            [100, 100, 150, 150, 0.85, 1],
            [105, 105, 155, 155, 0.80, 1]  # Overlaps with third
        ]
        
        iou_threshold = 0.5
        nms_bboxes = detect_service.apply_nms(bboxes, iou_threshold)
        
        # Should keep the highest confidence bbox from each overlapping group
        assert len(nms_bboxes) == 2
        assert nms_bboxes[0][4] == 0.95  # Highest confidence from first group
        assert nms_bboxes[1][4] == 0.85  # Highest confidence from second group
