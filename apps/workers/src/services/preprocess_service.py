"""Media preprocessing service for image search workers."""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from fastapi import UploadFile

from ..models.preprocess_models import (
    PreprocessRequest, PreprocessJobStatus, PreprocessStatus, PreprocessOperation,
    OperationInfo, PreprocessResult
)
from ..processors.image_processor import ImageProcessor
from ..processors.phash_processor import PHashProcessor
from ..processors.bg_removal_processor import BackgroundRemovalProcessor

logger = logging.getLogger(__name__)

class PreprocessService:
    """Service for managing media preprocessing jobs."""
    
    def __init__(self):
        self.active_jobs: Dict[str, PreprocessJobStatus] = {}
        self.image_processor = ImageProcessor()
        self.phash_processor = PHashProcessor()
        self.bg_removal_processor = BackgroundRemovalProcessor()
    
    async def start_preprocessing(self, request: PreprocessRequest) -> str:
        """Start a new preprocessing job."""
        job_id = str(uuid.uuid4())
        
        # Create job status
        job_status = PreprocessJobStatus(
            job_id=job_id,
            status=PreprocessStatus.PENDING,
            progress=0.0,
            message="Job created",
            started_at=datetime.utcnow()
        )
        
        self.active_jobs[job_id] = job_status
        
        logger.info(f"Started preprocessing job {job_id} for image {request.image_id}")
        
        return job_id
    
    async def process_preprocessing(self, job_id: str):
        """Process a preprocessing job."""
        if job_id not in self.active_jobs:
            logger.error(f"Job {job_id} not found")
            return
        
        job_status = self.active_jobs[job_id]
        job_status.status = PreprocessStatus.PROCESSING
        job_status.message = "Processing started"
        
        try:
            # Get job configuration (would come from database in real implementation)
            # For now, use default operations
            operations = [PreprocessOperation.RESIZE, PreprocessOperation.PHASH]
            config = {}
            
            # Process the image
            await self._process_image(job_id, operations, config)
            
            # Mark as completed
            job_status.status = PreprocessStatus.COMPLETED
            job_status.progress = 100.0
            job_status.message = "Processing completed successfully"
            job_status.completed_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            job_status.status = PreprocessStatus.FAILED
            job_status.message = f"Processing failed: {str(e)}"
            job_status.error = str(e)
            job_status.completed_at = datetime.utcnow()
    
    async def _process_image(self, job_id: str, operations: List[PreprocessOperation], config: Dict[str, Any]):
        """Process image with specified operations."""
        job_status = self.active_jobs[job_id]
        
        # Update progress
        job_status.progress = 10.0
        job_status.message = "Loading image"
        
        # Load image (would get from database/storage in real implementation)
        # For now, simulate loading
        await asyncio.sleep(0.1)
        
        # Update progress
        job_status.progress = 20.0
        job_status.message = "Processing operations"
        
        results = {}
        
        for i, operation in enumerate(operations):
            # Calculate progress for this operation
            operation_progress = 20 + (i / len(operations)) * 60
            job_status.progress = operation_progress
            job_status.message = f"Processing {operation.value}"
            
            try:
                if operation == PreprocessOperation.RESIZE:
                    results["resize"] = await self.image_processor.resize(config.get("resize", {}))
                
                elif operation == PreprocessOperation.CROP:
                    results["crop"] = await self.image_processor.crop(config.get("crop", {}))
                
                elif operation == PreprocessOperation.PHASH:
                    results["phash"] = await self.phash_processor.compute_hash(config.get("phash", {}))
                
                elif operation == PreprocessOperation.BG_REMOVAL:
                    results["bg_removal"] = await self.bg_removal_processor.remove_background(config.get("bg_removal", {}))
                
                elif operation == PreprocessOperation.NORMALIZE:
                    results["normalize"] = await self.image_processor.normalize(config.get("normalize", {}))
                
                elif operation == PreprocessOperation.ENHANCE:
                    results["enhance"] = await self.image_processor.enhance(config.get("enhance", {}))
                
                # Simulate processing time
                await asyncio.sleep(0.2)
                
            except Exception as e:
                logger.error(f"Error in operation {operation}: {str(e)}")
                results[operation.value] = {"error": str(e)}
        
        # Update progress
        job_status.progress = 80.0
        job_status.message = "Saving results"
        
        # Save results (would save to database/storage in real implementation)
        await asyncio.sleep(0.1)
        
        job_status.results = results
    
    async def upload_and_preprocess(self, file: UploadFile, operations: List[str], config: Dict[str, Any]):
        """Upload and preprocess an image immediately."""
        try:
            # Validate file
            if not file.content_type.startswith('image/'):
                raise ValueError("File must be an image")
            
            # Generate image ID
            image_id = str(uuid.uuid4())
            
            # Save uploaded file (would save to storage in real implementation)
            logger.info(f"Uploaded file: {file.filename}, size: {file.size}")
            
            # Process operations
            results = {}
            
            for operation in operations:
                if operation == "resize":
                    results["resize"] = await self.image_processor.resize(config.get("resize", {}))
                elif operation == "crop":
                    results["crop"] = await self.image_processor.crop(config.get("crop", {}))
                elif operation == "phash":
                    results["phash"] = await self.phash_processor.compute_hash(config.get("phash", {}))
                elif operation == "bg_removal":
                    results["bg_removal"] = await self.bg_removal_processor.remove_background(config.get("bg_removal", {}))
            
            return {
                "image_id": image_id,
                "filename": file.filename,
                "size": file.size,
                "content_type": file.content_type,
                "operations": operations,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Upload and preprocess failed: {str(e)}")
            raise
    
    async def get_preprocessing_status(self, job_id: str) -> PreprocessJobStatus:
        """Get the status of a preprocessing job."""
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        return self.active_jobs[job_id]
    
    async def cancel_preprocessing(self, job_id: str):
        """Cancel an ongoing preprocessing job."""
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job_status = self.active_jobs[job_id]
        
        if job_status.status in [PreprocessStatus.COMPLETED, PreprocessStatus.FAILED, PreprocessStatus.CANCELLED]:
            raise ValueError(f"Cannot cancel job in status: {job_status.status}")
        
        job_status.status = PreprocessStatus.CANCELLED
        job_status.message = "Job cancelled by user"
        job_status.completed_at = datetime.utcnow()
        
        logger.info(f"Cancelled preprocessing job {job_id}")
    
    async def list_operations(self) -> List[OperationInfo]:
        """List available preprocessing operations."""
        operations = [
            OperationInfo(
                name="resize",
                description="Resize image to specified dimensions",
                config_schema={
                    "type": "object",
                    "properties": {
                        "width": {"type": "integer"},
                        "height": {"type": "integer"},
                        "max_width": {"type": "integer"},
                        "max_height": {"type": "integer"},
                        "maintain_aspect_ratio": {"type": "boolean"},
                        "quality": {"type": "integer", "minimum": 1, "maximum": 100}
                    }
                },
                supported_formats=["jpeg", "png", "webp"],
                estimated_time=0.5
            ),
            OperationInfo(
                name="crop",
                description="Crop image to specified region",
                config_schema={
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer"},
                        "y": {"type": "integer"},
                        "width": {"type": "integer"},
                        "height": {"type": "integer"},
                        "center_crop": {"type": "boolean"},
                        "aspect_ratio": {"type": "number"}
                    }
                },
                supported_formats=["jpeg", "png", "webp"],
                estimated_time=0.3
            ),
            OperationInfo(
                name="phash",
                description="Compute perceptual hash of image",
                config_schema={
                    "type": "object",
                    "properties": {
                        "hash_size": {"type": "integer", "minimum": 4, "maximum": 32},
                        "highfreq_factor": {"type": "integer", "minimum": 1, "maximum": 10}
                    }
                },
                supported_formats=["jpeg", "png", "webp"],
                estimated_time=0.2
            ),
            OperationInfo(
                name="bg_removal",
                description="Remove background from image",
                config_schema={
                    "type": "object",
                    "properties": {
                        "method": {"type": "string", "enum": ["u2net", "rembg"]},
                        "threshold": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "post_process": {"type": "boolean"}
                    }
                },
                supported_formats=["jpeg", "png"],
                estimated_time=2.0
            )
        ]
        
        return operations
    
    async def batch_preprocess(self, image_ids: List[str], operations: List[str], config: Dict[str, Any]) -> List[str]:
        """Start batch preprocessing for multiple images."""
        job_ids = []
        
        for image_id in image_ids:
            # Create preprocessing request
            request = PreprocessRequest(
                image_id=image_id,
                organization_id="",  # Would come from context
                operations=[PreprocessOperation(op) for op in operations],
                config=config
            )
            
            # Start job
            job_id = await self.start_preprocessing(request)
            job_ids.append(job_id)
            
            # Start processing in background
            asyncio.create_task(self.process_preprocessing(job_id))
        
        return job_ids
