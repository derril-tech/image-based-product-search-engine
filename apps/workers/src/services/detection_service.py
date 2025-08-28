"""Object detection service for image search workers."""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid
import numpy as np

from ..models.detection_models import (
    DetectionRequest, DetectionJobStatus, DetectionStatus, DetectionModel,
    DetectionResult, Detection, BoundingBox, DetectionConfig, ModelInfo
)
from ..processors.yolo_processor import YOLOProcessor

logger = logging.getLogger(__name__)

class DetectionService:
    """Service for managing object detection jobs."""
    
    def __init__(self):
        self.active_jobs: Dict[str, DetectionJobStatus] = {}
        self.yolo_processor = YOLOProcessor()
        
        # COCO class names (YOLO default)
        self.coco_classes = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
            'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat',
            'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
            'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
            'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
            'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
            'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake',
            'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
            'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]
    
    async def start_detection(self, request: DetectionRequest) -> str:
        """Start a new object detection job."""
        job_id = str(uuid.uuid4())
        
        # Create job status
        job_status = DetectionJobStatus(
            job_id=job_id,
            status=DetectionStatus.PENDING,
            progress=0.0,
            message="Job created",
            started_at=datetime.utcnow()
        )
        
        self.active_jobs[job_id] = job_status
        
        logger.info(f"Started detection job {job_id} for image {request.image_id}")
        
        return job_id
    
    async def process_detection(self, job_id: str):
        """Process an object detection job."""
        if job_id not in self.active_jobs:
            logger.error(f"Job {job_id} not found")
            return
        
        job_status = self.active_jobs[job_id]
        job_status.status = DetectionStatus.PROCESSING
        job_status.message = "Detection started"
        
        try:
            # Get job configuration (would come from database in real implementation)
            # For now, use default configuration
            config = DetectionConfig(
                model=DetectionModel.YOLO_V8N,
                confidence_threshold=0.5,
                nms_threshold=0.4,
                max_detections=50
            )
            
            # Process the image
            await self._detect_objects(job_id, config)
            
            # Mark as completed
            job_status.status = DetectionStatus.COMPLETED
            job_status.progress = 100.0
            job_status.message = "Detection completed successfully"
            job_status.completed_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error processing detection job {job_id}: {str(e)}")
            job_status.status = DetectionStatus.FAILED
            job_status.message = f"Detection failed: {str(e)}"
            job_status.error = str(e)
            job_status.completed_at = datetime.utcnow()
    
    async def _detect_objects(self, job_id: str, config: DetectionConfig):
        """Detect objects in image with specified configuration."""
        job_status = self.active_jobs[job_id]
        
        # Update progress
        job_status.progress = 10.0
        job_status.message = "Loading image"
        
        # Load image (would get from database/storage in real implementation)
        # For now, simulate loading
        await asyncio.sleep(0.1)
        
        # Update progress
        job_status.progress = 20.0
        job_status.message = "Running detection model"
        
        # Run YOLO detection
        detections = await self.yolo_processor.detect(
            config.model,
            config.confidence_threshold,
            config.nms_threshold,
            config.max_detections
        )
        
        # Update progress
        job_status.progress = 80.0
        job_status.message = "Processing results"
        
        # Process and format results
        detection_results = []
        for detection in detections:
            bbox = BoundingBox(
                x=detection['bbox'][0],
                y=detection['bbox'][1],
                width=detection['bbox'][2] - detection['bbox'][0],
                height=detection['bbox'][3] - detection['bbox'][1]
            )
            
            detection_obj = Detection(
                class_id=detection['class_id'],
                class_name=self.coco_classes[detection['class_id']],
                confidence=detection['confidence'],
                bbox=bbox,
                area=bbox.width * bbox.height,
                center_x=bbox.x + bbox.width / 2,
                center_y=bbox.y + bbox.height / 2
            )
            detection_results.append(detection_obj)
        
        # Create detection result
        result = DetectionResult(
            image_id="mock_image_id",  # Would be actual image ID
            detections=detection_results,
            total_detections=len(detection_results),
            processing_time=2.5,  # Mock processing time
            model_used=config.model.value,
            image_width=1920,
            image_height=1080,
            confidence_threshold=config.confidence_threshold,
            nms_threshold=config.nms_threshold
        )
        
        job_status.results = result.dict()
    
    async def detect_objects(self, image_id: str, config: DetectionConfig) -> DetectionResult:
        """Detect objects in a specific image."""
        try:
            logger.info(f"Detecting objects in image {image_id} with model {config.model}")
            
            # Run detection
            detections = await self.yolo_processor.detect(
                config.model,
                config.confidence_threshold,
                config.nms_threshold,
                config.max_detections
            )
            
            # Process results
            detection_results = []
            for detection in detections:
                bbox = BoundingBox(
                    x=detection['bbox'][0],
                    y=detection['bbox'][1],
                    width=detection['bbox'][2] - detection['bbox'][0],
                    height=detection['bbox'][3] - detection['bbox'][1]
                )
                
                detection_obj = Detection(
                    class_id=detection['class_id'],
                    class_name=self.coco_classes[detection['class_id']],
                    confidence=detection['confidence'],
                    bbox=bbox,
                    area=bbox.width * bbox.height,
                    center_x=bbox.x + bbox.width / 2,
                    center_y=bbox.y + bbox.height / 2
                )
                detection_results.append(detection_obj)
            
            return DetectionResult(
                image_id=image_id,
                detections=detection_results,
                total_detections=len(detection_results),
                processing_time=2.5,
                model_used=config.model.value,
                image_width=1920,
                image_height=1080,
                confidence_threshold=config.confidence_threshold,
                nms_threshold=config.nms_threshold
            )
            
        except Exception as e:
            logger.error(f"Object detection failed: {str(e)}")
            raise
    
    async def get_detection_status(self, job_id: str) -> DetectionJobStatus:
        """Get the status of a detection job."""
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        return self.active_jobs[job_id]
    
    async def cancel_detection(self, job_id: str):
        """Cancel an ongoing detection job."""
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job_status = self.active_jobs[job_id]
        
        if job_status.status in [DetectionStatus.COMPLETED, DetectionStatus.FAILED, DetectionStatus.CANCELLED]:
            raise ValueError(f"Cannot cancel job in status: {job_status.status}")
        
        job_status.status = DetectionStatus.CANCELLED
        job_status.message = "Job cancelled by user"
        job_status.completed_at = datetime.utcnow()
        
        logger.info(f"Cancelled detection job {job_id}")
    
    async def list_models(self) -> List[ModelInfo]:
        """List available detection models."""
        models = [
            ModelInfo(
                name="YOLOv8n",
                version="8.0",
                description="YOLOv8 nano - fastest model",
                input_size=(640, 640),
                num_classes=80,
                model_size="6.7M",
                inference_time=0.8,
                mAP=0.37,
                supported_devices=["cpu", "cuda"]
            ),
            ModelInfo(
                name="YOLOv8s",
                version="8.0",
                description="YOLOv8 small - balanced model",
                input_size=(640, 640),
                num_classes=80,
                model_size="21.2M",
                inference_time=1.2,
                mAP=0.44,
                supported_devices=["cpu", "cuda"]
            ),
            ModelInfo(
                name="YOLOv8m",
                version="8.0",
                description="YOLOv8 medium - accurate model",
                input_size=(640, 640),
                num_classes=80,
                model_size="52.2M",
                inference_time=2.1,
                mAP=0.50,
                supported_devices=["cpu", "cuda"]
            ),
            ModelInfo(
                name="YOLOv8l",
                version="8.0",
                description="YOLOv8 large - very accurate model",
                input_size=(640, 640),
                num_classes=80,
                model_size="87.7M",
                inference_time=3.2,
                mAP=0.52,
                supported_devices=["cpu", "cuda"]
            ),
            ModelInfo(
                name="YOLOv8x",
                version="8.0",
                description="YOLOv8 xlarge - most accurate model",
                input_size=(640, 640),
                num_classes=80,
                model_size="136.1M",
                inference_time=4.8,
                mAP=0.53,
                supported_devices=["cpu", "cuda"]
            )
        ]
        
        return models
    
    async def batch_detect(self, image_ids: List[str], config: DetectionConfig) -> List[str]:
        """Start batch detection for multiple images."""
        job_ids = []
        
        for image_id in image_ids:
            # Create detection request
            request = DetectionRequest(
                image_id=image_id,
                organization_id="",  # Would come from context
                model=config.model,
                confidence_threshold=config.confidence_threshold,
                nms_threshold=config.nms_threshold,
                max_detections=config.max_detections,
                classes=config.classes,
                config=config.dict()
            )
            
            # Start job
            job_id = await self.start_detection(request)
            job_ids.append(job_id)
            
            # Start processing in background
            asyncio.create_task(self.process_detection(job_id))
        
        return job_ids
    
    async def get_class_names(self) -> List[str]:
        """Get list of COCO class names."""
        return self.coco_classes
    
    async def filter_detections_by_class(self, detections: List[Detection], 
                                       class_names: List[str]) -> List[Detection]:
        """Filter detections by class names."""
        filtered = []
        for detection in detections:
            if detection.class_name in class_names:
                filtered.append(detection)
        return filtered
    
    async def filter_detections_by_confidence(self, detections: List[Detection], 
                                            min_confidence: float) -> List[Detection]:
        """Filter detections by minimum confidence."""
        filtered = []
        for detection in detections:
            if detection.confidence >= min_confidence:
                filtered.append(detection)
        return filtered
