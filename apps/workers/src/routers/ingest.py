"""Data ingestion router for image search workers."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import logging

from ..services.ingest_service import IngestService
from ..models.ingest_models import IngestRequest, IngestResponse, IngestStatus

logger = logging.getLogger(__name__)
router = APIRouter()

class IngestRequestModel(BaseModel):
    """Request model for data ingestion."""
    connector_id: str
    feed_id: Optional[str] = None
    config: Dict[str, Any]
    priority: str = "normal"  # low, normal, high

class IngestStatusResponse(BaseModel):
    """Response model for ingestion status."""
    job_id: str
    status: str
    progress: float
    message: str
    stats: Dict[str, Any]

@router.post("/start", response_model=IngestResponse)
async def start_ingestion(
    request: IngestRequestModel,
    background_tasks: BackgroundTasks
):
    """Start a new data ingestion job."""
    try:
        ingest_service = IngestService()
        
        # Create ingestion request
        ingest_request = IngestRequest(
            connector_id=request.connector_id,
            feed_id=request.feed_id,
            config=request.config,
            priority=request.priority
        )
        
        # Start ingestion in background
        job_id = await ingest_service.start_ingestion(ingest_request)
        
        # Add background task for processing
        background_tasks.add_task(ingest_service.process_ingestion, job_id)
        
        return IngestResponse(
            job_id=job_id,
            status="started",
            message="Ingestion job started successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to start ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}", response_model=IngestStatusResponse)
async def get_ingestion_status(job_id: str):
    """Get the status of an ingestion job."""
    try:
        ingest_service = IngestService()
        status = await ingest_service.get_ingestion_status(job_id)
        
        return IngestStatusResponse(
            job_id=job_id,
            status=status.status,
            progress=status.progress,
            message=status.message,
            stats=status.stats
        )
        
    except Exception as e:
        logger.error(f"Failed to get ingestion status: {str(e)}")
        raise HTTPException(status_code=404, detail="Job not found")

@router.post("/cancel/{job_id}")
async def cancel_ingestion(job_id: str):
    """Cancel an ongoing ingestion job."""
    try:
        ingest_service = IngestService()
        await ingest_service.cancel_ingestion(job_id)
        
        return {"message": "Ingestion job cancelled successfully"}
        
    except Exception as e:
        logger.error(f"Failed to cancel ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connectors")
async def list_connectors():
    """List available data connectors."""
    try:
        ingest_service = IngestService()
        connectors = await ingest_service.list_connectors()
        
        return {
            "connectors": connectors
        }
        
    except Exception as e:
        logger.error(f"Failed to list connectors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-connection")
async def test_connection(request: IngestRequestModel):
    """Test connection to a data source."""
    try:
        ingest_service = IngestService()
        result = await ingest_service.test_connection(request.connector_id, request.config)
        
        return {
            "success": result.success,
            "message": result.message,
            "details": result.details
        }
        
    except Exception as e:
        logger.error(f"Failed to test connection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
