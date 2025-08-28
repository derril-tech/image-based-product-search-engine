"""Embedding service for image search workers."""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid
import numpy as np

from ..models.embedding_models import (
    EmbeddingRequest, EmbeddingJobStatus, EmbeddingStatus, EmbeddingModel,
    EmbeddingResult, Embedding, EmbeddingConfig, EmbeddingType, ModelInfo
)
from ..processors.clip_processor import CLIPProcessor
from ..processors.resnet_processor import ResNetProcessor

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for managing embedding generation jobs."""
    
    def __init__(self):
        self.active_jobs: Dict[str, EmbeddingJobStatus] = {}
        self.clip_processor = CLIPProcessor()
        self.resnet_processor = ResNetProcessor()
        
        # Model dimension mapping
        self.model_dimensions = {
            EmbeddingModel.CLIP_VIT_B_32: 512,
            EmbeddingModel.CLIP_VIT_L_14: 768,
            EmbeddingModel.CLIP_VIT_L_14_336: 768,
            EmbeddingModel.RESNET_50: 2048,
            EmbeddingModel.RESNET_101: 2048,
            EmbeddingModel.EFFICIENTNET_B0: 1280,
            EmbeddingModel.EFFICIENTNET_B4: 1792
        }
    
    async def start_embedding(self, request: EmbeddingRequest) -> str:
        """Start a new embedding generation job."""
        job_id = str(uuid.uuid4())
        
        # Create job status
        job_status = EmbeddingJobStatus(
            job_id=job_id,
            status=EmbeddingStatus.PENDING,
            progress=0.0,
            message="Job created",
            started_at=datetime.utcnow()
        )
        
        self.active_jobs[job_id] = job_status
        
        logger.info(f"Started embedding job {job_id} for content {request.content_id}")
        
        return job_id
    
    async def process_embedding(self, job_id: str):
        """Process an embedding generation job."""
        if job_id not in self.active_jobs:
            logger.error(f"Job {job_id} not found")
            return
        
        job_status = self.active_jobs[job_id]
        job_status.status = EmbeddingStatus.PROCESSING
        job_status.message = "Embedding generation started"
        
        try:
            # Get job configuration (would come from database in real implementation)
            # For now, use default configuration
            config = EmbeddingConfig(
                model=EmbeddingModel.CLIP_VIT_B_32,
                embedding_type=EmbeddingType.IMAGE,
                normalize=True
            )
            
            # Process the content
            await self._generate_embedding(job_id, config)
            
            # Mark as completed
            job_status.status = EmbeddingStatus.COMPLETED
            job_status.progress = 100.0
            job_status.message = "Embedding generation completed successfully"
            job_status.completed_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error processing embedding job {job_id}: {str(e)}")
            job_status.status = EmbeddingStatus.FAILED
            job_status.message = f"Embedding generation failed: {str(e)}"
            job_status.error = str(e)
            job_status.completed_at = datetime.utcnow()
    
    async def _generate_embedding(self, job_id: str, config: EmbeddingConfig):
        """Generate embedding with specified configuration."""
        job_status = self.active_jobs[job_id]
        
        # Update progress
        job_status.progress = 10.0
        job_status.message = "Loading content"
        
        # Load content (would get from database/storage in real implementation)
        # For now, simulate loading
        await asyncio.sleep(0.1)
        
        # Update progress
        job_status.progress = 30.0
        job_status.message = "Generating embedding"
        
        # Generate embedding based on model type
        if config.model in [EmbeddingModel.CLIP_VIT_B_32, EmbeddingModel.CLIP_VIT_L_14, EmbeddingModel.CLIP_VIT_L_14_336]:
            embedding_vector = await self.clip_processor.encode(config.model, config.embedding_type)
        else:
            embedding_vector = await self.resnet_processor.encode(config.model, config.embedding_type)
        
        # Update progress
        job_status.progress = 80.0
        job_status.message = "Processing results"
        
        # Create embedding result
        embedding = Embedding(
            content_id="mock_content_id",  # Would be actual content ID
            model=config.model.value,
            embedding_type=config.embedding_type,
            vector=embedding_vector,
            dimension=len(embedding_vector),
            normalized=config.normalize
        )
        
        result = EmbeddingResult(
            content_id="mock_content_id",
            embeddings=[embedding],
            processing_time=1.5,  # Mock processing time
            model_used=config.model.value,
            embedding_type=config.embedding_type,
            total_embeddings=1
        )
        
        job_status.results = result.dict()
    
    async def generate_embedding(self, content_id: str, config: EmbeddingConfig) -> EmbeddingResult:
        """Generate embedding for specific content."""
        try:
            logger.info(f"Generating embedding for content {content_id} with model {config.model}")
            
            # Generate embedding based on model type
            if config.model in [EmbeddingModel.CLIP_VIT_B_32, EmbeddingModel.CLIP_VIT_L_14, EmbeddingModel.CLIP_VIT_L_14_336]:
                embedding_vector = await self.clip_processor.encode(config.model, config.embedding_type)
            else:
                embedding_vector = await self.resnet_processor.encode(config.model, config.embedding_type)
            
            # Create embedding
            embedding = Embedding(
                content_id=content_id,
                model=config.model.value,
                embedding_type=config.embedding_type,
                vector=embedding_vector,
                dimension=len(embedding_vector),
                normalized=config.normalize
            )
            
            return EmbeddingResult(
                content_id=content_id,
                embeddings=[embedding],
                processing_time=1.5,
                model_used=config.model.value,
                embedding_type=config.embedding_type,
                total_embeddings=1
            )
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise
    
    async def generate_text_embedding(self, text: str, config: EmbeddingConfig) -> EmbeddingResult:
        """Generate embedding for text content."""
        try:
            logger.info(f"Generating text embedding with model {config.model}")
            
            # Generate text embedding
            if config.model in [EmbeddingModel.CLIP_VIT_B_32, EmbeddingModel.CLIP_VIT_L_14, EmbeddingModel.CLIP_VIT_L_14_336]:
                embedding_vector = await self.clip_processor.encode_text(text, config.model)
            else:
                # ResNet doesn't support text, use CLIP as fallback
                embedding_vector = await self.clip_processor.encode_text(text, EmbeddingModel.CLIP_VIT_B_32)
            
            # Create embedding
            embedding = Embedding(
                content_id=f"text_{uuid.uuid4()}",
                model=config.model.value,
                embedding_type=EmbeddingType.TEXT,
                vector=embedding_vector,
                dimension=len(embedding_vector),
                normalized=config.normalize
            )
            
            return EmbeddingResult(
                content_id=embedding.content_id,
                embeddings=[embedding],
                processing_time=0.8,
                model_used=config.model.value,
                embedding_type=EmbeddingType.TEXT,
                total_embeddings=1
            )
            
        except Exception as e:
            logger.error(f"Text embedding generation failed: {str(e)}")
            raise
    
    async def generate_image_embedding(self, image_id: str, config: EmbeddingConfig) -> EmbeddingResult:
        """Generate embedding for image content."""
        try:
            logger.info(f"Generating image embedding for {image_id} with model {config.model}")
            
            # Generate image embedding
            if config.model in [EmbeddingModel.CLIP_VIT_B_32, EmbeddingModel.CLIP_VIT_L_14, EmbeddingModel.CLIP_VIT_L_14_336]:
                embedding_vector = await self.clip_processor.encode_image(image_id, config.model)
            else:
                embedding_vector = await self.resnet_processor.encode_image(image_id, config.model)
            
            # Create embedding
            embedding = Embedding(
                content_id=image_id,
                model=config.model.value,
                embedding_type=EmbeddingType.IMAGE,
                vector=embedding_vector,
                dimension=len(embedding_vector),
                normalized=config.normalize
            )
            
            return EmbeddingResult(
                content_id=image_id,
                embeddings=[embedding],
                processing_time=1.2,
                model_used=config.model.value,
                embedding_type=EmbeddingType.IMAGE,
                total_embeddings=1
            )
            
        except Exception as e:
            logger.error(f"Image embedding generation failed: {str(e)}")
            raise
    
    async def get_embedding_status(self, job_id: str) -> EmbeddingJobStatus:
        """Get the status of an embedding job."""
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        return self.active_jobs[job_id]
    
    async def cancel_embedding(self, job_id: str):
        """Cancel an ongoing embedding job."""
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job_status = self.active_jobs[job_id]
        
        if job_status.status in [EmbeddingStatus.COMPLETED, EmbeddingStatus.FAILED, EmbeddingStatus.CANCELLED]:
            raise ValueError(f"Cannot cancel job in status: {job_status.status}")
        
        job_status.status = EmbeddingStatus.CANCELLED
        job_status.message = "Job cancelled by user"
        job_status.completed_at = datetime.utcnow()
        
        logger.info(f"Cancelled embedding job {job_id}")
    
    async def list_models(self) -> List[ModelInfo]:
        """List available embedding models."""
        models = [
            ModelInfo(
                name="CLIP ViT-B/32",
                version="1.0",
                description="CLIP Vision Transformer Base/32 - balanced model",
                embedding_dimension=512,
                model_size="151M",
                inference_time=0.3,
                supported_types=[EmbeddingType.IMAGE, EmbeddingType.TEXT, EmbeddingType.MULTIMODAL],
                supported_devices=["cpu", "cuda"]
            ),
            ModelInfo(
                name="CLIP ViT-L/14",
                version="1.0",
                description="CLIP Vision Transformer Large/14 - accurate model",
                embedding_dimension=768,
                model_size="427M",
                inference_time=0.8,
                supported_types=[EmbeddingType.IMAGE, EmbeddingType.TEXT, EmbeddingType.MULTIMODAL],
                supported_devices=["cpu", "cuda"]
            ),
            ModelInfo(
                name="CLIP ViT-L/14@336px",
                version="1.0",
                description="CLIP Vision Transformer Large/14 at 336px - high resolution",
                embedding_dimension=768,
                model_size="427M",
                inference_time=1.2,
                supported_types=[EmbeddingType.IMAGE, EmbeddingType.TEXT, EmbeddingType.MULTIMODAL],
                supported_devices=["cpu", "cuda"]
            ),
            ModelInfo(
                name="ResNet-50",
                version="1.0",
                description="ResNet-50 - classic CNN for image features",
                embedding_dimension=2048,
                model_size="25.6M",
                inference_time=0.2,
                supported_types=[EmbeddingType.IMAGE],
                supported_devices=["cpu", "cuda"]
            ),
            ModelInfo(
                name="ResNet-101",
                version="1.0",
                description="ResNet-101 - deeper CNN for better features",
                embedding_dimension=2048,
                model_size="44.5M",
                inference_time=0.4,
                supported_types=[EmbeddingType.IMAGE],
                supported_devices=["cpu", "cuda"]
            ),
            ModelInfo(
                name="EfficientNet-B0",
                version="1.0",
                description="EfficientNet-B0 - efficient CNN architecture",
                embedding_dimension=1280,
                model_size="29M",
                inference_time=0.15,
                supported_types=[EmbeddingType.IMAGE],
                supported_devices=["cpu", "cuda"]
            ),
            ModelInfo(
                name="EfficientNet-B4",
                version="1.0",
                description="EfficientNet-B4 - larger efficient model",
                embedding_dimension=1792,
                model_size="19M",
                inference_time=0.3,
                supported_types=[EmbeddingType.IMAGE],
                supported_devices=["cpu", "cuda"]
            )
        ]
        
        return models
    
    async def batch_embed(self, content_ids: List[str], config: EmbeddingConfig) -> List[str]:
        """Start batch embedding for multiple content items."""
        job_ids = []
        
        for content_id in content_ids:
            # Create embedding request
            request = EmbeddingRequest(
                content_id=content_id,
                organization_id="",  # Would come from context
                model=config.model,
                embedding_type=config.embedding_type,
                content_type="image",  # Would be determined from content
                config=config.dict()
            )
            
            # Start job
            job_id = await self.start_embedding(request)
            job_ids.append(job_id)
            
            # Start processing in background
            asyncio.create_task(self.process_embedding(job_id))
        
        return job_ids
    
    async def calculate_similarity(self, embedding1: List[float], embedding2: List[float], 
                                 metric: str = "cosine") -> float:
        """Calculate similarity between two embeddings."""
        try:
            if metric == "cosine":
                return self._cosine_similarity(embedding1, embedding2)
            elif metric == "euclidean":
                return self._euclidean_similarity(embedding1, embedding2)
            elif metric == "dot_product":
                return self._dot_product_similarity(embedding1, embedding2)
            else:
                raise ValueError(f"Unsupported similarity metric: {metric}")
                
        except Exception as e:
            logger.error(f"Similarity calculation failed: {str(e)}")
            raise
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _euclidean_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate Euclidean similarity (1 / (1 + distance))."""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        distance = np.linalg.norm(vec1 - vec2)
        return 1.0 / (1.0 + distance)
    
    def _dot_product_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate dot product similarity."""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        return float(np.dot(vec1, vec2))
