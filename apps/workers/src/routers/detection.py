"""FastAPI router for object detection endpoints."""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import List, Dict, Any, Optional
import json

from ..models.detection_models import (
    DetectionRequest, DetectionResponse, DetectionJobStatus, 
    DetectionConfig, ModelInfo, DetectionResult
)
from ..services.detection_service import DetectionService

router = APIRouter(prefix="/detection", tags=["Object Detection"])

# Initialize service
detection_service = DetectionService()

@router.post("/start", response_model=DetectionResponse)
async def start_detection(request: DetectionRequest):
    """Start a new object detection job."""
    try:
        job_id = await detection_service.start_detection(request)
        
        # Start processing in background
        import asyncio
        asyncio.create_task(detection_service.process_detection(job_id))
        
        return DetectionResponse(
            job_id=job_id,
            status="started",
            message="Detection job started successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect")
async def detect_objects(
    image_id: str,
    model: str = "yolov8n",
    confidence_threshold: float = 0.5,
    nms_threshold: float = 0.4,
    max_detections: int = 50,
    classes: Optional[str] = None  # JSON string of class IDs
):
    """Detect objects in a specific image."""
    try:
        # Parse classes if provided
        class_list = None
        if classes:
            class_list = json.loads(classes)
        
        config = DetectionConfig(
            model=model,
            confidence_threshold=confidence_threshold,
            nms_threshold=nms_threshold,
            max_detections=max_detections,
            classes=class_list
        )
        
        result = await detection_service.detect_objects(image_id, config)
        return result
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in classes parameter")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}", response_model=DetectionJobStatus)
async def get_detection_status(job_id: str):
    """Get the status of a detection job."""
    try:
        return await detection_service.get_detection_status(job_id)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cancel/{job_id}")
async def cancel_detection(job_id: str):
    """Cancel an ongoing detection job."""
    try:
        await detection_service.cancel_detection(job_id)
        return {"message": "Job cancelled successfully"}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models", response_model=List[ModelInfo])
async def list_models():
    """List available detection models."""
    try:
        return await detection_service.list_models()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch")
async def batch_detect(
    image_ids: List[str],
    model: str = "yolov8n",
    confidence_threshold: float = 0.5,
    nms_threshold: float = 0.4,
    max_detections: int = 50
):
    """Start batch detection for multiple images."""
    try:
        config = DetectionConfig(
            model=model,
            confidence_threshold=confidence_threshold,
            nms_threshold=nms_threshold,
            max_detections=max_detections
        )
        
        job_ids = await detection_service.batch_detect(image_ids, config)
        
        return {
            "message": f"Started batch detection for {len(image_ids)} images",
            "job_ids": job_ids,
            "total_images": len(image_ids)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/classes")
async def get_class_names():
    """Get list of COCO class names."""
    try:
        return await detection_service.get_class_names()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-and-detect")
async def upload_and_detect(
    file: UploadFile = File(...),
    model: str = Form("yolov8n"),
    confidence_threshold: float = Form(0.5),
    nms_threshold: float = Form(0.4),
    max_detections: int = Form(50)
):
    """Upload and detect objects in an image immediately."""
    try:
        # Validate file
        if not file.content_type.startswith('image/'):
            raise ValueError("File must be an image")
        
        # Generate image ID
        import uuid
        image_id = str(uuid.uuid4())
        
        # Save uploaded file (would save to storage in real implementation)
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Uploaded file: {file.filename}, size: {file.size}")
        
        # Create config
        config = DetectionConfig(
            model=model,
            confidence_threshold=confidence_threshold,
            nms_threshold=nms_threshold,
            max_detections=max_detections
        )
        
        # Detect objects
        result = await detection_service.detect_objects(image_id, config)
        
        return {
            "image_id": image_id,
            "filename": file.filename,
            "size": file.size,
            "content_type": file.content_type,
            "detection_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-regions")
async def detect_regions(
    image_id: str,
    regions: str,  # JSON string of regions [[x, y, width, height], ...]
    model: str = "yolov8n",
    confidence_threshold: float = 0.5
):
    """Detect objects in specific regions of an image."""
    try:
        # Parse regions
        regions_list = json.loads(regions)
        
        # In real implementation, would call detection service with regions
        # For now, return mock results
        results = []
        for i, region in enumerate(regions_list):
            results.append({
                "region_id": f"region_{i}",
                "bbox": region,
                "detections": []  # Would contain actual detections
            })
        
        return {
            "image_id": image_id,
            "regions": results,
            "model": model,
            "confidence_threshold": confidence_threshold
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in regions parameter")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/filter-by-class")
async def filter_detections_by_class(
    detections: List[Dict[str, Any]],
    class_names: List[str]
):
    """Filter detections by class names."""
    try:
        # Convert dict to Detection objects
        from ..models.detection_models import Detection, BoundingBox
        
        detection_objects = []
        for det in detections:
            bbox = BoundingBox(**det['bbox'])
            detection = Detection(
                class_id=det['class_id'],
                class_name=det['class_name'],
                confidence=det['confidence'],
                bbox=bbox,
                area=det['area'],
                center_x=det['center_x'],
                center_y=det['center_y']
            )
            detection_objects.append(detection)
        
        filtered = await detection_service.filter_detections_by_class(detection_objects, class_names)
        
        return {
            "original_count": len(detection_objects),
            "filtered_count": len(filtered),
            "filtered_detections": [det.dict() for det in filtered]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/filter-by-confidence")
async def filter_detections_by_confidence(
    detections: List[Dict[str, Any]],
    min_confidence: float
):
    """Filter detections by minimum confidence."""
    try:
        # Convert dict to Detection objects
        from ..models.detection_models import Detection, BoundingBox
        
        detection_objects = []
        for det in detections:
            bbox = BoundingBox(**det['bbox'])
            detection = Detection(
                class_id=det['class_id'],
                class_name=det['class_name'],
                confidence=det['confidence'],
                bbox=bbox,
                area=det['area'],
                center_x=det['center_x'],
                center_y=det['center_y']
            )
            detection_objects.append(detection)
        
        filtered = await detection_service.filter_detections_by_confidence(detection_objects, min_confidence)
        
        return {
            "original_count": len(detection_objects),
            "filtered_count": len(filtered),
            "min_confidence": min_confidence,
            "filtered_detections": [det.dict() for det in filtered]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs")
async def list_jobs():
    """List all active detection jobs."""
    try:
        jobs = list(detection_service.active_jobs.values())
        return {
            "total_jobs": len(jobs),
            "jobs": jobs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
