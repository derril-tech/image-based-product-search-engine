# CDN Service for Image Delivery and Thumbnailing
# Created automatically by Cursor AI (2024-12-19)

import os
import hashlib
import mimetypes
from typing import Optional, Dict, List, Tuple
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from PIL import Image, ImageOps
import io
import logging
from urllib.parse import urlparse, urljoin
import time

logger = logging.getLogger(__name__)

class CDNService:
    """CDN service for image delivery with automatic thumbnailing"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=config.get('aws_access_key_id'),
            aws_secret_access_key=config.get('aws_secret_access_key'),
            region_name=config.get('aws_region', 'us-east-1')
        )
        self.bucket_name = config.get('s3_bucket_name')
        self.cdn_domain = config.get('cdn_domain')
        self.cloudfront_distribution_id = config.get('cloudfront_distribution_id')
        
        # Thumbnail configurations
        self.thumbnail_sizes = {
            'xs': (100, 100),
            'sm': (200, 200),
            'md': (400, 400),
            'lg': (800, 800),
            'xl': (1200, 1200),
            'original': None
        }
        
        # Quality settings
        self.jpeg_quality = config.get('jpeg_quality', 85)
        self.png_optimize = config.get('png_optimize', True)
        
        # Cache settings
        self.cache_headers = {
            'Cache-Control': 'public, max-age=31536000',  # 1 year
            'Expires': 'Thu, 31 Dec 2025 23:59:59 GMT'
        }

    def upload_image(self, image_data: bytes, filename: str, content_type: str = None) -> str:
        """Upload an image to S3 and return the CDN URL"""
        try:
            # Generate unique filename
            file_hash = hashlib.md5(image_data).hexdigest()
            file_ext = Path(filename).suffix or self._get_extension_from_mime(content_type)
            unique_filename = f"{file_hash}{file_ext}"
            
            # Upload original image
            s3_key = f"images/original/{unique_filename}"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=image_data,
                ContentType=content_type or 'image/jpeg',
                **self.cache_headers
            )
            
            # Generate thumbnails
            self._generate_thumbnails(image_data, unique_filename, content_type)
            
            # Return CDN URL
            return self._get_cdn_url(s3_key)
            
        except Exception as e:
            logger.error(f"Failed to upload image {filename}: {e}")
            raise

    def _generate_thumbnails(self, image_data: bytes, filename: str, content_type: str):
        """Generate thumbnails for different sizes"""
        try:
            # Open image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Generate thumbnails for each size
            for size_name, dimensions in self.thumbnail_sizes.items():
                if size_name == 'original':
                    continue
                    
                thumbnail = self._create_thumbnail(image, dimensions)
                thumbnail_data = self._encode_image(thumbnail, content_type)
                
                # Upload thumbnail
                s3_key = f"images/thumbnails/{size_name}/{filename}"
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=thumbnail_data,
                    ContentType=content_type or 'image/jpeg',
                    **self.cache_headers
                )
                
        except Exception as e:
            logger.error(f"Failed to generate thumbnails for {filename}: {e}")
            raise

    def _create_thumbnail(self, image: Image.Image, dimensions: Tuple[int, int]) -> Image.Image:
        """Create a thumbnail with proper aspect ratio"""
        width, height = dimensions
        
        # Calculate aspect ratio
        img_ratio = image.width / image.height
        target_ratio = width / height
        
        if img_ratio > target_ratio:
            # Image is wider than target
            new_width = int(height * img_ratio)
            new_height = height
            crop_left = (new_width - width) // 2
            crop_right = crop_left + width
            crop_top = 0
            crop_bottom = height
        else:
            # Image is taller than target
            new_width = width
            new_height = int(width / img_ratio)
            crop_left = 0
            crop_right = width
            crop_top = (new_height - height) // 2
            crop_bottom = crop_top + height
        
        # Resize image
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Crop to target dimensions
        thumbnail = resized.crop((crop_left, crop_top, crop_right, crop_bottom))
        
        return thumbnail

    def _encode_image(self, image: Image.Image, content_type: str) -> bytes:
        """Encode image to bytes with appropriate format and quality"""
        buffer = io.BytesIO()
        
        if content_type == 'image/png':
            image.save(buffer, format='PNG', optimize=self.png_optimize)
        elif content_type == 'image/webp':
            image.save(buffer, format='WebP', quality=self.jpeg_quality)
        else:
            # Default to JPEG
            image.save(buffer, format='JPEG', quality=self.jpeg_quality, optimize=True)
        
        buffer.seek(0)
        return buffer.getvalue()

    def get_image_url(self, filename: str, size: str = 'original') -> str:
        """Get CDN URL for an image with specified size"""
        if size == 'original':
            s3_key = f"images/original/{filename}"
        else:
            if size not in self.thumbnail_sizes:
                size = 'md'  # Default to medium size
            s3_key = f"images/thumbnails/{size}/{filename}"
        
        return self._get_cdn_url(s3_key)

    def get_responsive_urls(self, filename: str) -> Dict[str, str]:
        """Get responsive image URLs for all sizes"""
        urls = {}
        for size_name in self.thumbnail_sizes.keys():
            urls[size_name] = self.get_image_url(filename, size_name)
        return urls

    def delete_image(self, filename: str):
        """Delete an image and all its thumbnails from S3"""
        try:
            # Delete original
            original_key = f"images/original/{filename}"
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=original_key)
            
            # Delete thumbnails
            for size_name in self.thumbnail_sizes.keys():
                if size_name != 'original':
                    thumbnail_key = f"images/thumbnails/{size_name}/{filename}"
                    self.s3_client.delete_object(Bucket=self.bucket_name, Key=thumbnail_key)
                    
        except Exception as e:
            logger.error(f"Failed to delete image {filename}: {e}")
            raise

    def invalidate_cache(self, paths: List[str]):
        """Invalidate CloudFront cache for specified paths"""
        if not self.cloudfront_distribution_id:
            logger.warning("CloudFront distribution ID not configured, skipping cache invalidation")
            return
        
        try:
            cloudfront = boto3.client('cloudfront')
            
            # Create invalidation
            response = cloudfront.create_invalidation(
                DistributionId=self.cloudfront_distribution_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(paths),
                        'Items': paths
                    },
                    'CallerReference': f"invalidation-{int(time.time())}"
                }
            )
            
            logger.info(f"Created CloudFront invalidation: {response['Invalidation']['Id']}")
            
        except Exception as e:
            logger.error(f"Failed to invalidate CloudFront cache: {e}")
            raise

    def _get_cdn_url(self, s3_key: str) -> str:
        """Generate CDN URL from S3 key"""
        if self.cdn_domain:
            return f"https://{self.cdn_domain}/{s3_key}"
        else:
            # Fallback to S3 URL
            return f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"

    def _get_extension_from_mime(self, content_type: str) -> str:
        """Get file extension from MIME type"""
        if not content_type:
            return '.jpg'
        
        ext = mimetypes.guess_extension(content_type)
        return ext or '.jpg'

    def get_image_info(self, filename: str) -> Dict:
        """Get information about an image"""
        try:
            original_key = f"images/original/{filename}"
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=original_key)
            
            return {
                'filename': filename,
                'size': response['ContentLength'],
                'content_type': response['ContentType'],
                'last_modified': response['LastModified'],
                'etag': response['ETag'].strip('"'),
                'urls': self.get_responsive_urls(filename)
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None
            raise

    def optimize_image(self, image_data: bytes, content_type: str = None) -> bytes:
        """Optimize image for web delivery"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Strip metadata
            data = list(image.getdata())
            optimized_image = Image.new(image.mode, image.size)
            optimized_image.putdata(data)
            
            # Encode with optimization
            return self._encode_image(optimized_image, content_type)
            
        except Exception as e:
            logger.error(f"Failed to optimize image: {e}")
            return image_data

    def create_signed_url(self, filename: str, size: str = 'original', expires_in: int = 3600) -> str:
        """Create a signed URL for private images"""
        try:
            if size == 'original':
                s3_key = f"images/original/{filename}"
            else:
                s3_key = f"images/thumbnails/{size}/{filename}"
            
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expires_in
            )
            
            return url
            
        except Exception as e:
            logger.error(f"Failed to create signed URL for {filename}: {e}")
            raise
