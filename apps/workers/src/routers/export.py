"""FastAPI router for export session endpoints."""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json

from ..models.export_models import (
    ExportRequest, ExportResponse, ExportJobStatus, ExportType, ExportFormat,
    ExportTemplate, BatchExportRequest, BatchExportResponse, ExportConfig
)
from ..services.export_service import ExportService

router = APIRouter(prefix="/export", tags=["Export"])

# Initialize service
export_service = ExportService()

@router.post("/", response_model=ExportResponse)
async def create_export_job(request: ExportRequest):
    """Create a new export job."""
    try:
        job_id = await export_service.create_export_job(request)
        return ExportResponse(
            job_id=job_id,
            status="started",
            message=f"Export job {job_id} created successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}", response_model=ExportJobStatus)
async def get_export_status(job_id: str):
    """Get the status of an export job."""
    try:
        return await export_service.get_export_status(job_id)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cancel/{job_id}")
async def cancel_export_job(job_id: str):
    """Cancel an export job."""
    try:
        await export_service.cancel_export_job(job_id)
        return {"message": f"Export job {job_id} cancelled successfully"}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", response_model=BatchExportResponse)
async def process_batch_export(request: BatchExportRequest):
    """Process batch export requests."""
    try:
        return await export_service.process_batch_export(request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates")
async def create_export_template(template: ExportTemplate):
    """Create an export template."""
    try:
        await export_service.create_export_template(template)
        return {"message": f"Export template {template.template_id} created successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def list_export_templates(organization_id: str):
    """List export templates for an organization."""
    try:
        return await export_service.list_export_templates(organization_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_id}")
async def get_export_template(template_id: str):
    """Get an export template."""
    try:
        return await export_service.get_export_template(template_id)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/templates/{template_id}")
async def delete_export_template(template_id: str):
    """Delete an export template."""
    try:
        await export_service.delete_export_template(template_id)
        return {"message": f"Export template {template_id} deleted successfully"}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_export_config():
    """Get export configuration."""
    try:
        return await export_service.get_export_config()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/config")
async def update_export_config(config: ExportConfig):
    """Update export configuration."""
    try:
        await export_service.update_export_config(config)
        return {"message": "Export configuration updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-sessions")
async def export_search_sessions(
    organization_id: str,
    session_id: Optional[str] = None,
    format: ExportFormat = ExportFormat.JSON,
    include_metadata: bool = Query(True),
    filters: Optional[str] = None  # JSON string
):
    """Export search sessions."""
    try:
        # Parse filters
        filters_dict = {}
        if filters:
            filters_dict = json.loads(filters)
        
        request = ExportRequest(
            export_type=ExportType.SEARCH_SESSION,
            format=format,
            organization_id=organization_id,
            session_id=session_id,
            include_metadata=include_metadata,
            filters=filters_dict
        )
        
        job_id = await export_service.create_export_job(request)
        return ExportResponse(
            job_id=job_id,
            status="started",
            message=f"Search sessions export job {job_id} created successfully"
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in filters parameter")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-results")
async def export_search_results(
    organization_id: str,
    session_id: Optional[str] = None,
    format: ExportFormat = ExportFormat.JSON,
    include_metadata: bool = Query(True),
    filters: Optional[str] = None  # JSON string
):
    """Export search results."""
    try:
        # Parse filters
        filters_dict = {}
        if filters:
            filters_dict = json.loads(filters)
        
        request = ExportRequest(
            export_type=ExportType.SEARCH_RESULTS,
            format=format,
            organization_id=organization_id,
            session_id=session_id,
            include_metadata=include_metadata,
            filters=filters_dict
        )
        
        job_id = await export_service.create_export_job(request)
        return ExportResponse(
            job_id=job_id,
            status="started",
            message=f"Search results export job {job_id} created successfully"
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in filters parameter")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/catalog")
async def export_catalog_data(
    organization_id: str,
    format: ExportFormat = ExportFormat.JSON,
    include_metadata: bool = Query(True),
    filters: Optional[str] = None  # JSON string
):
    """Export catalog data."""
    try:
        # Parse filters
        filters_dict = {}
        if filters:
            filters_dict = json.loads(filters)
        
        request = ExportRequest(
            export_type=ExportType.CATALOG_DATA,
            format=format,
            organization_id=organization_id,
            include_metadata=include_metadata,
            filters=filters_dict
        )
        
        job_id = await export_service.create_export_job(request)
        return ExportResponse(
            job_id=job_id,
            status="started",
            message=f"Catalog data export job {job_id} created successfully"
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in filters parameter")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def export_analytics_data(
    organization_id: str,
    format: ExportFormat = ExportFormat.JSON,
    include_metadata: bool = Query(True),
    filters: Optional[str] = None  # JSON string
):
    """Export analytics data."""
    try:
        # Parse filters
        filters_dict = {}
        if filters:
            filters_dict = json.loads(filters)
        
        request = ExportRequest(
            export_type=ExportType.ANALYTICS_DATA,
            format=format,
            organization_id=organization_id,
            include_metadata=include_metadata,
            filters=filters_dict
        )
        
        job_id = await export_service.create_export_job(request)
        return ExportResponse(
            job_id=job_id,
            status="started",
            message=f"Analytics data export job {job_id} created successfully"
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in filters parameter")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-behavior")
async def export_user_behavior(
    organization_id: str,
    format: ExportFormat = ExportFormat.JSON,
    include_metadata: bool = Query(True),
    filters: Optional[str] = None  # JSON string
):
    """Export user behavior data."""
    try:
        # Parse filters
        filters_dict = {}
        if filters:
            filters_dict = json.loads(filters)
        
        request = ExportRequest(
            export_type=ExportType.USER_BEHAVIOR,
            format=format,
            organization_id=organization_id,
            include_metadata=include_metadata,
            filters=filters_dict
        )
        
        job_id = await export_service.create_export_job(request)
        return ExportResponse(
            job_id=job_id,
            status="started",
            message=f"User behavior export job {job_id} created successfully"
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in filters parameter")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{job_id}")
async def download_export(job_id: str):
    """Download exported file."""
    try:
        job_status = await export_service.get_export_status(job_id)
        
        if job_status.status != ExportJobStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Export job not completed")
        
        if not job_status.download_url:
            raise HTTPException(status_code=404, detail="Download URL not available")
        
        # Mock file download - in real implementation would serve actual file
        mock_file_content = f"Mock export file for job {job_id}"
        
        return {
            "job_id": job_id,
            "download_url": job_status.download_url,
            "file_size_bytes": job_status.file_size_bytes,
            "expires_at": job_status.expires_at,
            "content": mock_file_content
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs")
async def list_export_jobs(
    organization_id: str,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100)
):
    """List export jobs for an organization."""
    try:
        jobs = []
        for job_id, job_status in export_service.active_jobs.items():
            # In a real implementation, would filter by organization_id
            if status and job_status.status.value != status:
                continue
            jobs.append(job_status)
        
        # Sort by created date (newest first)
        jobs.sort(key=lambda x: x.started_at or datetime.min, reverse=True)
        
        return {
            "jobs": jobs[:limit],
            "total_jobs": len(jobs),
            "organization_id": organization_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup")
async def cleanup_expired_exports():
    """Clean up expired export files."""
    try:
        await export_service.cleanup_expired_exports()
        return {"message": "Expired exports cleaned up successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/formats")
async def get_supported_formats():
    """Get supported export formats."""
    formats = {
        "json": {
            "description": "JavaScript Object Notation",
            "best_for": "Data analysis, API integration",
            "compression": True
        },
        "csv": {
            "description": "Comma-Separated Values",
            "best_for": "Spreadsheet applications, data import",
            "compression": True
        },
        "excel": {
            "description": "Microsoft Excel format",
            "best_for": "Business reporting, data visualization",
            "compression": False
        },
        "parquet": {
            "description": "Columnar storage format",
            "best_for": "Big data processing, analytics",
            "compression": True
        }
    }
    
    return formats

@router.get("/types")
async def get_export_types():
    """Get available export types."""
    types = {
        "search_session": {
            "description": "Export search session data",
            "fields": ["session_id", "user_id", "start_time", "end_time", "total_searches", "search_queries", "clicked_items"],
            "filters": ["start_date", "end_date", "user_id", "session_id"]
        },
        "search_results": {
            "description": "Export search result data",
            "fields": ["query_id", "session_id", "query_text", "query_image_url", "timestamp", "results", "search_time_ms"],
            "filters": ["start_date", "end_date", "session_id", "query_text"]
        },
        "catalog_data": {
            "description": "Export product catalog data",
            "fields": ["products", "categories", "brands", "metadata"],
            "filters": ["category", "brand", "price_range", "in_stock"]
        },
        "analytics_data": {
            "description": "Export analytics and metrics data",
            "fields": ["metrics", "reports", "user_behaviors", "metadata"],
            "filters": ["start_date", "end_date", "metric_type", "report_type"]
        },
        "user_behavior": {
            "description": "Export user behavior and interaction data",
            "fields": ["users", "sessions", "interactions", "conversions"],
            "filters": ["start_date", "end_date", "user_id", "session_id"]
        }
    }
    
    return types

@router.get("/health")
async def export_health():
    """Get export service health status."""
    try:
        health_status = {
            "status": "healthy",
            "services": {
                "export_service": "available",
                "file_storage": "available",
                "compression": "available"
            },
            "metrics": {
                "active_jobs": len(export_service.active_jobs),
                "total_templates": len(export_service.export_templates),
                "completed_jobs": len([j for j in export_service.active_jobs.values() if j.status == ExportJobStatus.COMPLETED]),
                "failed_jobs": len([j for j in export_service.active_jobs.values() if j.status == ExportJobStatus.FAILED])
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
