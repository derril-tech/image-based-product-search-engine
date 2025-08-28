"""FastAPI router for media preprocessing endpoints."""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import List, Dict, Any, Optional
import json

from ..models.preprocess_models import (
    PreprocessRequest, PreprocessResponse, PreprocessJobStatus, 
    OperationInfo, PreprocessOperation
)
from ..services.preprocess_service import PreprocessService

router = APIRouter(prefix="/preprocess", tags=["Media Preprocessing"])

# Initialize service
preprocess_service = PreprocessService()

@router.post("/start", response_model=PreprocessResponse)
async def start_preprocessing(request: PreprocessRequest):
    """Start a new preprocessing job."""
    try:
        job_id = await preprocess_service.start_preprocessing(request)
        
        # Start processing in background
        import asyncio
        asyncio.create_task(preprocess_service.process_preprocessing(job_id))
        
        return PreprocessResponse(
            job_id=job_id,
            status="started",
            message="Preprocessing job started successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-and-preprocess")
async def upload_and_preprocess(
    file: UploadFile = File(...),
    operations: str = Form(...),  # JSON string of operations
    config: str = Form("{}")  # JSON string of config
):
    """Upload and preprocess an image immediately."""
    try:
        # Parse operations and config
        operations_list = json.loads(operations)
        config_dict = json.loads(config)
        
        result = await preprocess_service.upload_and_preprocess(
            file, operations_list, config_dict
        )
        
        return result
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in operations or config")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}", response_model=PreprocessJobStatus)
async def get_preprocessing_status(job_id: str):
    """Get the status of a preprocessing job."""
    try:
        return await preprocess_service.get_preprocessing_status(job_id)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cancel/{job_id}")
async def cancel_preprocessing(job_id: str):
    """Cancel an ongoing preprocessing job."""
    try:
        await preprocess_service.cancel_preprocessing(job_id)
        return {"message": "Job cancelled successfully"}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/operations", response_model=List[OperationInfo])
async def list_operations():
    """List available preprocessing operations."""
    try:
        return await preprocess_service.list_operations()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch")
async def batch_preprocess(
    image_ids: List[str],
    operations: List[str],
    config: Dict[str, Any] = {}
):
    """Start batch preprocessing for multiple images."""
    try:
        job_ids = await preprocess_service.batch_preprocess(
            image_ids, operations, config
        )
        
        return {
            "message": f"Started batch preprocessing for {len(image_ids)} images",
            "job_ids": job_ids,
            "total_images": len(image_ids)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resize")
async def resize_image(
    image_id: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None,
    maintain_aspect_ratio: bool = True,
    quality: int = 85
):
    """Resize a specific image."""
    try:
        config = {
            "width": width,
            "height": height,
            "max_width": max_width,
            "max_height": max_height,
            "maintain_aspect_ratio": maintain_aspect_ratio,
            "quality": quality
        }
        
        result = await preprocess_service.image_processor.resize(config)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crop")
async def crop_image(
    image_id: str,
    x: Optional[int] = None,
    y: Optional[int] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    center_crop: bool = False,
    aspect_ratio: Optional[float] = None
):
    """Crop a specific image."""
    try:
        config = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "center_crop": center_crop,
            "aspect_ratio": aspect_ratio
        }
        
        result = await preprocess_service.image_processor.crop(config)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/phash")
async def compute_phash(
    image_id: str,
    hash_size: int = 8,
    highfreq_factor: int = 4
):
    """Compute perceptual hash for a specific image."""
    try:
        config = {
            "hash_size": hash_size,
            "highfreq_factor": highfreq_factor
        }
        
        result = await preprocess_service.phash_processor.compute_hash(config)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bg-removal")
async def remove_background(
    image_id: str,
    method: str = "u2net",
    threshold: float = 0.5,
    post_process: bool = True
):
    """Remove background from a specific image."""
    try:
        config = {
            "method": method,
            "threshold": threshold,
            "post_process": post_process
        }
        
        result = await preprocess_service.bg_removal_processor.remove_background(config)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bg-removal/methods")
async def get_bg_removal_methods():
    """Get supported background removal methods."""
    try:
        return await preprocess_service.bg_removal_processor.get_supported_methods()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enhance")
async def enhance_image(
    image_id: str,
    brightness: float = 1.0,
    contrast: float = 1.0,
    saturation: float = 1.0,
    sharpness: float = 1.0
):
    """Enhance a specific image."""
    try:
        config = {
            "brightness": brightness,
            "contrast": contrast,
            "saturation": saturation,
            "sharpness": sharpness
        }
        
        result = await preprocess_service.image_processor.enhance(config)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/normalize")
async def normalize_image(
    image_id: str,
    mean: List[float] = [0.485, 0.456, 0.406],
    std: List[float] = [0.229, 0.224, 0.225],
    scale: float = 1.0 / 255.0
):
    """Normalize a specific image."""
    try:
        config = {
            "mean": mean,
            "std": std,
            "scale": scale
        }
        
        result = await preprocess_service.image_processor.normalize(config)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs")
async def list_jobs():
    """List all active preprocessing jobs."""
    try:
        jobs = list(preprocess_service.active_jobs.values())
        return {
            "total_jobs": len(jobs),
            "jobs": jobs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
