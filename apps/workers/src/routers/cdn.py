# CDN Router for Image Delivery and Thumbnailing
# Created automatically by Cursor AI (2024-12-19)

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict
import logging
from pydantic import BaseModel
import io

from ..services.cdn_service import CDNService
from ..services.thumbnailing_pipeline import ThumbnailingPipeline, ProcessingStatus
from ..dependencies import get_cdn_service, get_thumbnailing_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cdn", tags=["CDN"])

class ImageUploadResponse(BaseModel):
    url: str
    filename: str
    size: int
    content_type: str
    thumbnail_urls: Dict[str, str]

class ThumbnailJobResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    created_at: float
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    result_urls: Optional[Dict[str, str]] = None

class BatchUploadRequest(BaseModel):
    sizes: Optional[List[str]] = None
    enable_enhancement: Optional[bool] = True
    enable_watermark: Optional[bool] = False

class ImageInfoResponse(BaseModel):
    filename: str
    size: int
    content_type: str
    last_modified: str
    etag: str
    urls: Dict[str, str]

@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    cdn_service: CDNService = Depends(get_cdn_service)
):
    """Upload an image and generate thumbnails"""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file data
        image_data = await file.read()
        
        # Upload to CDN
        url = cdn_service.upload_image(image_data, file.filename, file.content_type)
        
        # Get thumbnail URLs
        filename = url.split('/')[-1]  # Extract filename from URL
        thumbnail_urls = cdn_service.get_responsive_urls(filename)
        
        return ImageUploadResponse(
            url=url,
            filename=filename,
            size=len(image_data),
            content_type=file.content_type,
            thumbnail_urls=thumbnail_urls
        )
        
    except Exception as e:
        logger.error(f"Failed to upload image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload/async", response_model=ThumbnailJobResponse)
async def upload_image_async(
    file: UploadFile = File(...),
    request: BatchUploadRequest = None,
    pipeline: ThumbnailingPipeline = Depends(get_thumbnailing_pipeline)
):
    """Upload an image asynchronously with custom processing"""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file data
        image_data = await file.read()
        
        # Process image
        job_id = await pipeline.process_image(
            image_data=image_data,
            filename=file.filename,
            content_type=file.content_type,
            sizes=request.sizes if request else None
        )
        
        # Get initial status
        status = pipeline.get_job_status(job_id)
        
        return ThumbnailJobResponse(**status)
        
    except Exception as e:
        logger.error(f"Failed to start async upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/job/{job_id}", response_model=ThumbnailJobResponse)
async def get_job_status(
    job_id: str,
    pipeline: ThumbnailingPipeline = Depends(get_thumbnailing_pipeline)
):
    """Get the status of a thumbnail job"""
    status = pipeline.get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return ThumbnailJobResponse(**status)

@router.get("/image/{filename}", response_model=ImageInfoResponse)
async def get_image_info(
    filename: str,
    cdn_service: CDNService = Depends(get_cdn_service)
):
    """Get information about an image"""
    info = cdn_service.get_image_info(filename)
    if not info:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return ImageInfoResponse(
        filename=info['filename'],
        size=info['size'],
        content_type=info['content_type'],
        last_modified=info['last_modified'].isoformat(),
        etag=info['etag'],
        urls=info['urls']
    )

@router.get("/image/{filename}/url")
async def get_image_url(
    filename: str,
    size: str = "original",
    cdn_service: CDNService = Depends(get_cdn_service)
):
    """Get CDN URL for an image with specified size"""
    try:
        url = cdn_service.get_image_url(filename, size)
        return {"url": url, "filename": filename, "size": size}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Image not found")

@router.get("/image/{filename}/responsive")
async def get_responsive_urls(
    filename: str,
    cdn_service: CDNService = Depends(get_cdn_service)
):
    """Get all responsive image URLs for a filename"""
    try:
        urls = cdn_service.get_responsive_urls(filename)
        return {"filename": filename, "urls": urls}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Image not found")

@router.delete("/image/{filename}")
async def delete_image(
    filename: str,
    cdn_service: CDNService = Depends(get_cdn_service)
):
    """Delete an image and all its thumbnails"""
    try:
        cdn_service.delete_image(filename)
        return {"message": "Image deleted successfully", "filename": filename}
    except Exception as e:
        logger.error(f"Failed to delete image {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch/upload")
async def batch_upload(
    files: List[UploadFile] = File(...),
    request: BatchUploadRequest = None,
    pipeline: ThumbnailingPipeline = Depends(get_thumbnailing_pipeline)
):
    """Upload multiple images in batch"""
    try:
        job_ids = []
        
        for file in files:
            # Validate file type
            if not file.content_type or not file.content_type.startswith('image/'):
                continue
            
            # Read file data
            image_data = await file.read()
            
            # Process image
            job_id = await pipeline.process_image(
                image_data=image_data,
                filename=file.filename,
                content_type=file.content_type,
                sizes=request.sizes if request else None
            )
            
            job_ids.append(job_id)
        
        return {
            "message": f"Started processing {len(job_ids)} images",
            "job_ids": job_ids
        }
        
    except Exception as e:
        logger.error(f"Failed to start batch upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/invalidate")
async def invalidate_cache(
    paths: List[str],
    cdn_service: CDNService = Depends(get_cdn_service)
):
    """Invalidate CloudFront cache for specified paths"""
    try:
        cdn_service.invalidate_cache(paths)
        return {
            "message": f"Cache invalidation requested for {len(paths)} paths",
            "paths": paths
        }
    except Exception as e:
        logger.error(f"Failed to invalidate cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_pipeline_stats(
    pipeline: ThumbnailingPipeline = Depends(get_thumbnailing_pipeline)
):
    """Get thumbnailing pipeline statistics"""
    return {
        "active_jobs": pipeline.get_active_jobs_count(),
        "completed_jobs": pipeline.get_completed_jobs_count(),
        "failed_jobs": pipeline.get_failed_jobs_count(),
        "total_jobs": len(pipeline.active_jobs)
    }

@router.post("/cleanup")
async def cleanup_jobs(
    max_age_hours: int = 24,
    pipeline: ThumbnailingPipeline = Depends(get_thumbnailing_pipeline)
):
    """Clean up completed jobs older than specified age"""
    try:
        pipeline.cleanup_completed_jobs(max_age_hours)
        return {
            "message": f"Cleaned up jobs older than {max_age_hours} hours"
        }
    except Exception as e:
        logger.error(f"Failed to cleanup jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signed-url/{filename}")
async def create_signed_url(
    filename: str,
    size: str = "original",
    expires_in: int = 3600,
    cdn_service: CDNService = Depends(get_cdn_service)
):
    """Create a signed URL for private image access"""
    try:
        url = cdn_service.create_signed_url(filename, size, expires_in)
        return {
            "url": url,
            "filename": filename,
            "size": size,
            "expires_in": expires_in
        }
    except Exception as e:
        logger.error(f"Failed to create signed URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize")
async def optimize_image(
    file: UploadFile = File(...),
    cdn_service: CDNService = Depends(get_cdn_service)
):
    """Optimize an image for web delivery"""
    try:
        # Read file data
        image_data = await file.read()
        
        # Optimize image
        optimized_data = cdn_service.optimize_image(image_data, file.content_type)
        
        # Return optimized image as streaming response
        return StreamingResponse(
            io.BytesIO(optimized_data),
            media_type=file.content_type,
            headers={
                "Content-Disposition": f"attachment; filename=optimized_{file.filename}",
                "Content-Length": str(len(optimized_data))
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to optimize image: {e}")
        raise HTTPException(status_code=500, detail=str(e))
