# Thumbnailing Pipeline Service
# Created automatically by Cursor AI (2024-12-19)

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time
from concurrent.futures import ThreadPoolExecutor
import io
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
import os

from .cdn_service import CDNService

logger = logging.getLogger(__name__)

class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ThumbnailJob:
    job_id: str
    image_data: bytes
    filename: str
    content_type: str
    requested_sizes: List[str]
    status: ProcessingStatus
    created_at: float
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    result_urls: Optional[Dict[str, str]] = None

class ThumbnailingPipeline:
    """Pipeline for processing images and generating thumbnails"""
    
    def __init__(self, cdn_service: CDNService, config: Dict):
        self.cdn_service = cdn_service
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=config.get('max_workers', 4))
        self.active_jobs: Dict[str, ThumbnailJob] = {}
        
        # Processing options
        self.enable_enhancement = config.get('enable_enhancement', True)
        self.enable_watermark = config.get('enable_watermark', False)
        self.watermark_path = config.get('watermark_path')
        self.enhancement_settings = config.get('enhancement_settings', {
            'sharpness': 1.2,
            'contrast': 1.1,
            'brightness': 1.05,
            'saturation': 1.1
        })

    async def process_image(self, image_data: bytes, filename: str, content_type: str = None, 
                          sizes: List[str] = None) -> str:
        """Process an image and return the job ID"""
        job_id = f"thumb_{int(time.time())}_{hash(filename) % 10000}"
        
        if sizes is None:
            sizes = ['xs', 'sm', 'md', 'lg']
        
        job = ThumbnailJob(
            job_id=job_id,
            image_data=image_data,
            filename=filename,
            content_type=content_type or 'image/jpeg',
            requested_sizes=sizes,
            status=ProcessingStatus.PENDING,
            created_at=time.time()
        )
        
        self.active_jobs[job_id] = job
        
        # Start processing in background
        asyncio.create_task(self._process_job(job))
        
        return job_id

    async def _process_job(self, job: ThumbnailJob):
        """Process a thumbnail job"""
        try:
            job.status = ProcessingStatus.PROCESSING
            
            # Optimize original image
            optimized_data = self.cdn_service.optimize_image(job.image_data, job.content_type)
            
            # Upload original
            original_url = self.cdn_service.upload_image(
                optimized_data, 
                job.filename, 
                job.content_type
            )
            
            # Generate requested thumbnails
            thumbnail_urls = {}
            for size in job.requested_sizes:
                if size in self.cdn_service.thumbnail_sizes:
                    url = self.cdn_service.get_image_url(job.filename, size)
                    thumbnail_urls[size] = url
            
            # Store results
            job.result_urls = {
                'original': original_url,
                'thumbnails': thumbnail_urls
            }
            job.status = ProcessingStatus.COMPLETED
            job.completed_at = time.time()
            
            logger.info(f"Completed thumbnail job {job.job_id} for {job.filename}")
            
        except Exception as e:
            job.status = ProcessingStatus.FAILED
            job.error_message = str(e)
            job.completed_at = time.time()
            logger.error(f"Failed thumbnail job {job.job_id} for {job.filename}: {e}")

    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get the status of a thumbnail job"""
        job = self.active_jobs.get(job_id)
        if not job:
            return None
        
        return {
            'job_id': job.job_id,
            'status': job.status.value,
            'created_at': job.created_at,
            'completed_at': job.completed_at,
            'error_message': job.error_message,
            'result_urls': job.result_urls,
            'progress': self._calculate_progress(job)
        }

    def _calculate_progress(self, job: ThumbnailJob) -> float:
        """Calculate progress percentage for a job"""
        if job.status == ProcessingStatus.COMPLETED:
            return 100.0
        elif job.status == ProcessingStatus.FAILED:
            return 0.0
        elif job.status == ProcessingStatus.PROCESSING:
            # Estimate progress based on time elapsed
            elapsed = time.time() - job.created_at
            # Assume average processing time is 5 seconds
            progress = min(90.0, (elapsed / 5.0) * 90.0)
            return progress
        else:
            return 0.0

    def cleanup_completed_jobs(self, max_age_hours: int = 24):
        """Clean up completed jobs older than specified age"""
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        jobs_to_remove = []
        for job_id, job in self.active_jobs.items():
            if (job.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED] and 
                job.completed_at and job.completed_at < cutoff_time):
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.active_jobs[job_id]
        
        if jobs_to_remove:
            logger.info(f"Cleaned up {len(jobs_to_remove)} completed jobs")

    async def batch_process(self, images: List[Tuple[bytes, str, str]]) -> List[str]:
        """Process multiple images in batch"""
        job_ids = []
        
        for image_data, filename, content_type in images:
            job_id = await self.process_image(image_data, filename, content_type)
            job_ids.append(job_id)
        
        return job_ids

    def get_active_jobs_count(self) -> int:
        """Get count of active jobs"""
        return len([j for j in self.active_jobs.values() 
                   if j.status in [ProcessingStatus.PENDING, ProcessingStatus.PROCESSING]])

    def get_completed_jobs_count(self) -> int:
        """Get count of completed jobs"""
        return len([j for j in self.active_jobs.values() 
                   if j.status == ProcessingStatus.COMPLETED])

    def get_failed_jobs_count(self) -> int:
        """Get count of failed jobs"""
        return len([j for j in self.active_jobs.values() 
                   if j.status == ProcessingStatus.FAILED])

class ImageEnhancer:
    """Enhance images for better quality"""
    
    def __init__(self, settings: Dict):
        self.settings = settings

    def enhance_image(self, image: Image.Image) -> Image.Image:
        """Apply enhancements to an image"""
        try:
            # Sharpness
            if self.settings.get('sharpness', 1.0) != 1.0:
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(self.settings['sharpness'])
            
            # Contrast
            if self.settings.get('contrast', 1.0) != 1.0:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(self.settings['contrast'])
            
            # Brightness
            if self.settings.get('brightness', 1.0) != 1.0:
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(self.settings['brightness'])
            
            # Saturation
            if self.settings.get('saturation', 1.0) != 1.0:
                enhancer = ImageEnhance.Color(image)
                image = enhancer.enhance(self.settings['saturation'])
            
            return image
            
        except Exception as e:
            logger.error(f"Failed to enhance image: {e}")
            return image

class WatermarkProcessor:
    """Add watermarks to images"""
    
    def __init__(self, watermark_path: str):
        self.watermark_path = watermark_path
        self.watermark = None
        self._load_watermark()

    def _load_watermark(self):
        """Load watermark image"""
        try:
            if self.watermark_path and os.path.exists(self.watermark_path):
                self.watermark = Image.open(self.watermark_path).convert('RGBA')
                logger.info(f"Loaded watermark from {self.watermark_path}")
        except Exception as e:
            logger.error(f"Failed to load watermark: {e}")

    def add_watermark(self, image: Image.Image, position: str = 'bottom-right', 
                     opacity: float = 0.7) -> Image.Image:
        """Add watermark to image"""
        if not self.watermark:
            return image
        
        try:
            # Convert image to RGBA if necessary
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Resize watermark to appropriate size (e.g., 10% of image width)
            watermark_width = int(image.width * 0.1)
            watermark_height = int(self.watermark.height * (watermark_width / self.watermark.width))
            resized_watermark = self.watermark.resize((watermark_width, watermark_height), Image.Resampling.LANCZOS)
            
            # Apply opacity
            if opacity < 1.0:
                alpha = resized_watermark.split()[3]
                alpha = alpha.point(lambda x: int(x * opacity))
                resized_watermark.putalpha(alpha)
            
            # Calculate position
            if position == 'bottom-right':
                x = image.width - watermark_width - 10
                y = image.height - watermark_height - 10
            elif position == 'bottom-left':
                x = 10
                y = image.height - watermark_height - 10
            elif position == 'top-right':
                x = image.width - watermark_width - 10
                y = 10
            elif position == 'top-left':
                x = 10
                y = 10
            elif position == 'center':
                x = (image.width - watermark_width) // 2
                y = (image.height - watermark_height) // 2
            else:
                x = 10
                y = 10
            
            # Paste watermark
            image.paste(resized_watermark, (x, y), resized_watermark)
            
            return image
            
        except Exception as e:
            logger.error(f"Failed to add watermark: {e}")
            return image

class ResponsiveImageGenerator:
    """Generate responsive images with srcset"""
    
    def __init__(self, cdn_service: CDNService):
        self.cdn_service = cdn_service

    def generate_srcset(self, filename: str, sizes: List[str] = None) -> str:
        """Generate srcset attribute for responsive images"""
        if sizes is None:
            sizes = ['xs', 'sm', 'md', 'lg', 'xl']
        
        srcset_parts = []
        for size in sizes:
            if size in self.cdn_service.thumbnail_sizes:
                url = self.cdn_service.get_image_url(filename, size)
                width = self.cdn_service.thumbnail_sizes[size][0]
                srcset_parts.append(f"{url} {width}w")
        
        return ", ".join(srcset_parts)

    def generate_picture_element(self, filename: str, alt_text: str, 
                               sizes: str = "(max-width: 768px) 100vw, 50vw") -> str:
        """Generate HTML picture element for responsive images"""
        srcset = self.generate_srcset(filename)
        original_url = self.cdn_service.get_image_url(filename, 'original')
        
        return f"""
        <picture>
            <source srcset="{srcset}" sizes="{sizes}">
            <img src="{original_url}" alt="{alt_text}" loading="lazy">
        </picture>
        """

    def generate_webp_srcset(self, filename: str, sizes: List[str] = None) -> str:
        """Generate WebP srcset for modern browsers"""
        if sizes is None:
            sizes = ['xs', 'sm', 'md', 'lg', 'xl']
        
        srcset_parts = []
        for size in sizes:
            if size in self.cdn_service.thumbnail_sizes:
                # Convert to WebP URL (assuming WebP versions exist)
                url = self.cdn_service.get_image_url(filename, size).replace('.jpg', '.webp')
                width = self.cdn_service.thumbnail_sizes[size][0]
                srcset_parts.append(f"{url} {width}w")
        
        return ", ".join(srcset_parts)
