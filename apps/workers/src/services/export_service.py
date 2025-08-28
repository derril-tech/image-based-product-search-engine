"""Export service for session and data export functionality."""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import uuid
import json
import csv
import io
import gzip
import base64
import time

from ..models.export_models import (
    ExportRequest, ExportResponse, ExportJobStatus, ExportStatus, ExportType, ExportFormat,
    SearchSessionExport, SearchResultExport, CatalogDataExport, AnalyticsDataExport,
    UserBehaviorExport, ExportConfig, ExportTemplate, BatchExportRequest, BatchExportResponse
)

logger = logging.getLogger(__name__)

class ExportService:
    """Service for export session and data functionality."""
    
    def __init__(self):
        self.active_jobs: Dict[str, ExportJobStatus] = {}
        self.export_templates: Dict[str, ExportTemplate] = {}
        self.export_config = ExportConfig()
        
        # Mock data storage
        self.mock_search_sessions: Dict[str, SearchSessionExport] = {}
        self.mock_search_results: Dict[str, SearchResultExport] = {}
        self.mock_catalog_data: Dict[str, CatalogDataExport] = {}
        self.mock_analytics_data: Dict[str, AnalyticsDataExport] = {}
        self.mock_user_behaviors: Dict[str, UserBehaviorExport] = {}
        
        # Initialize mock data
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize mock data for testing."""
        # Mock search sessions
        for i in range(10):
            session_id = f"session_{i}"
            self.mock_search_sessions[session_id] = SearchSessionExport(
                session_id=session_id,
                organization_id="org_1",
                user_id=f"user_{i}",
                start_time=datetime.utcnow() - timedelta(hours=i),
                end_time=datetime.utcnow() - timedelta(hours=i-1) if i > 0 else None,
                total_searches=i + 1,
                total_results=(i + 1) * 10,
                search_queries=[
                    {"query": f"product {j}", "timestamp": datetime.utcnow() - timedelta(minutes=j)}
                    for j in range(i + 1)
                ],
                clicked_items=[
                    {"item_id": f"item_{j}", "position": j, "timestamp": datetime.utcnow() - timedelta(minutes=j)}
                    for j in range(min(i + 1, 5))
                ],
                conversion_items=[
                    {"item_id": f"item_{j}", "revenue": 100 + j * 10, "timestamp": datetime.utcnow() - timedelta(minutes=j)}
                    for j in range(min(i + 1, 2))
                ],
                metadata={"device": "desktop", "location": "US"}
            )
        
        # Mock search results
        for i in range(20):
            query_id = f"query_{i}"
            self.mock_search_results[query_id] = SearchResultExport(
                query_id=query_id,
                session_id=f"session_{i % 10}",
                organization_id="org_1",
                query_text=f"search query {i}",
                query_image_url=f"https://example.com/image_{i}.jpg" if i % 3 == 0 else None,
                timestamp=datetime.utcnow() - timedelta(minutes=i),
                results=[
                    {
                        "id": f"result_{j}",
                        "score": 0.9 - j * 0.1,
                        "title": f"Product {j}",
                        "price": 100 + j * 10,
                        "image_url": f"https://example.com/product_{j}.jpg"
                    }
                    for j in range(10)
                ],
                total_results=10,
                search_time_ms=50 + i * 5,
                filters_applied={"category": "electronics", "price_range": "100-500"},
                metadata={"search_type": "text" if i % 2 == 0 else "image"}
            )
        
        # Mock catalog data
        self.mock_catalog_data["org_1"] = CatalogDataExport(
            organization_id="org_1",
            export_date=datetime.utcnow(),
            total_products=1000,
            products=[
                {
                    "id": f"product_{i}",
                    "name": f"Product {i}",
                    "description": f"Description for product {i}",
                    "price": 100 + i * 10,
                    "category": f"Category {i % 10}",
                    "brand": f"Brand {i % 5}",
                    "image_url": f"https://example.com/product_{i}.jpg",
                    "sku": f"SKU_{i:06d}",
                    "in_stock": i % 3 != 0
                }
                for i in range(100)
            ],
            categories=[
                {"id": f"cat_{i}", "name": f"Category {i}", "product_count": 100}
                for i in range(10)
            ],
            brands=[
                {"id": f"brand_{i}", "name": f"Brand {i}", "product_count": 200}
                for i in range(5)
            ],
            metadata={"export_version": "1.0", "total_categories": 10, "total_brands": 5}
        )
        
        # Mock analytics data
        self.mock_analytics_data["org_1"] = AnalyticsDataExport(
            organization_id="org_1",
            export_date=datetime.utcnow(),
            time_range={
                "start_time": datetime.utcnow() - timedelta(days=7),
                "end_time": datetime.utcnow()
            },
            metrics=[
                {
                    "metric_type": "recall_at_k",
                    "k": k,
                    "value": 0.8 + k * 0.02,
                    "timestamp": datetime.utcnow() - timedelta(days=i)
                }
                for i in range(7)
                for k in [1, 3, 5, 10]
            ],
            reports=[
                {
                    "report_id": f"report_{i}",
                    "type": "search_performance",
                    "generated_at": datetime.utcnow() - timedelta(days=i),
                    "summary": {"total_searches": 1000 + i * 100}
                }
                for i in range(5)
            ],
            user_behaviors=[
                {
                    "user_id": f"user_{i}",
                    "total_sessions": i + 1,
                    "avg_session_duration": 5 + i * 0.5,
                    "conversion_rate": 0.02 + i * 0.001
                }
                for i in range(50)
            ],
            metadata={"export_type": "analytics", "data_points": 1000}
        )
        
        # Mock user behavior data
        self.mock_user_behaviors["org_1"] = UserBehaviorExport(
            organization_id="org_1",
            export_date=datetime.utcnow(),
            users=[
                {
                    "user_id": f"user_{i}",
                    "email": f"user{i}@example.com",
                    "created_at": datetime.utcnow() - timedelta(days=i * 10),
                    "last_activity": datetime.utcnow() - timedelta(hours=i)
                }
                for i in range(100)
            ],
            sessions=[
                {
                    "session_id": f"session_{i}",
                    "user_id": f"user_{i % 100}",
                    "start_time": datetime.utcnow() - timedelta(hours=i),
                    "duration_minutes": 10 + i % 20,
                    "total_searches": 1 + i % 10
                }
                for i in range(500)
            ],
            interactions=[
                {
                    "interaction_id": f"interaction_{i}",
                    "user_id": f"user_{i % 100}",
                    "session_id": f"session_{i % 500}",
                    "type": "search" if i % 3 == 0 else "click" if i % 3 == 1 else "view",
                    "timestamp": datetime.utcnow() - timedelta(minutes=i)
                }
                for i in range(1000)
            ],
            conversions=[
                {
                    "conversion_id": f"conversion_{i}",
                    "user_id": f"user_{i % 100}",
                    "session_id": f"session_{i % 500}",
                    "amount": 100 + i * 10,
                    "timestamp": datetime.utcnow() - timedelta(hours=i)
                }
                for i in range(50)
            ],
            metadata={"total_users": 100, "total_sessions": 500, "total_conversions": 50}
        )
    
    async def create_export_job(self, request: ExportRequest) -> str:
        """Create a new export job."""
        job_id = str(uuid.uuid4())
        
        job_status = ExportJobStatus(
            job_id=job_id,
            status=ExportStatus.PENDING,
            progress=0.0,
            message=f"Export job created for {request.export_type.value}",
            started_at=datetime.utcnow()
        )
        self.active_jobs[job_id] = job_status
        
        logger.info(f"Created export job {job_id} for {request.export_type.value}")
        
        # Start background processing
        asyncio.create_task(self._process_export_job(job_id, request))
        
        return job_id
    
    async def _process_export_job(self, job_id: str, request: ExportRequest):
        """Process export job in background."""
        job_status = self.active_jobs[job_id]
        
        try:
            job_status.status = ExportStatus.PROCESSING
            job_status.progress = 10.0
            job_status.message = "Processing export data..."
            
            # Simulate processing time
            await asyncio.sleep(2)
            
            # Generate export data based on type
            export_data = await self._generate_export_data(request)
            
            job_status.progress = 50.0
            job_status.message = "Formatting data..."
            
            # Format data based on requested format
            formatted_data = await self._format_export_data(export_data, request.format)
            
            job_status.progress = 80.0
            job_status.message = "Compressing and uploading..."
            
            # Simulate file creation and upload
            await asyncio.sleep(1)
            
            # Generate download URL and file info
            file_size = len(formatted_data.encode('utf-8')) if isinstance(formatted_data, str) else len(formatted_data)
            download_url = f"/exports/{job_id}/download"
            expires_at = datetime.utcnow() + timedelta(days=self.export_config.retention_days)
            
            job_status.status = ExportStatus.COMPLETED
            job_status.progress = 100.0
            job_status.message = "Export completed successfully"
            job_status.file_size_bytes = file_size
            job_status.download_url = download_url
            job_status.expires_at = expires_at
            job_status.completed_at = datetime.utcnow()
            
            logger.info(f"Export job {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Export job {job_id} failed: {str(e)}")
            job_status.status = ExportStatus.FAILED
            job_status.message = f"Export failed: {str(e)}"
            job_status.error = str(e)
            job_status.completed_at = datetime.utcnow()
    
    async def _generate_export_data(self, request: ExportRequest) -> Dict[str, Any]:
        """Generate export data based on export type."""
        if request.export_type == ExportType.SEARCH_SESSION:
            return await self._generate_search_session_data(request)
        elif request.export_type == ExportType.SEARCH_RESULTS:
            return await self._generate_search_results_data(request)
        elif request.export_type == ExportType.CATALOG_DATA:
            return await self._generate_catalog_data(request)
        elif request.export_type == ExportType.ANALYTICS_DATA:
            return await self._generate_analytics_data(request)
        elif request.export_type == ExportType.USER_BEHAVIOR:
            return await self._generate_user_behavior_data(request)
        else:
            raise ValueError(f"Unsupported export type: {request.export_type}")
    
    async def _generate_search_session_data(self, request: ExportRequest) -> Dict[str, Any]:
        """Generate search session export data."""
        sessions = []
        
        # Filter sessions by organization and session_id if specified
        for session in self.mock_search_sessions.values():
            if session.organization_id == request.organization_id:
                if request.session_id and session.session_id != request.session_id:
                    continue
                
                session_data = session.dict()
                
                # Apply filters
                if request.filters:
                    if "start_date" in request.filters:
                        start_date = datetime.fromisoformat(request.filters["start_date"])
                        if session.start_time < start_date:
                            continue
                    if "end_date" in request.filters:
                        end_date = datetime.fromisoformat(request.filters["end_date"])
                        if session.end_time and session.end_time > end_date:
                            continue
                
                # Include/exclude fields based on request
                if not request.include_metadata:
                    session_data.pop("metadata", None)
                
                sessions.append(session_data)
        
        return {
            "export_type": "search_session",
            "organization_id": request.organization_id,
            "export_date": datetime.utcnow().isoformat(),
            "total_sessions": len(sessions),
            "sessions": sessions
        }
    
    async def _generate_search_results_data(self, request: ExportRequest) -> Dict[str, Any]:
        """Generate search results export data."""
        results = []
        
        for result in self.mock_search_results.values():
            if result.organization_id == request.organization_id:
                if request.session_id and result.session_id != request.session_id:
                    continue
                
                result_data = result.dict()
                
                # Apply filters
                if request.filters:
                    if "start_date" in request.filters:
                        start_date = datetime.fromisoformat(request.filters["start_date"])
                        if result.timestamp < start_date:
                            continue
                    if "end_date" in request.filters:
                        end_date = datetime.fromisoformat(request.filters["end_date"])
                        if result.timestamp > end_date:
                            continue
                
                # Include/exclude fields based on request
                if not request.include_metadata:
                    result_data.pop("metadata", None)
                
                results.append(result_data)
        
        return {
            "export_type": "search_results",
            "organization_id": request.organization_id,
            "export_date": datetime.utcnow().isoformat(),
            "total_results": len(results),
            "results": results
        }
    
    async def _generate_catalog_data(self, request: ExportRequest) -> Dict[str, Any]:
        """Generate catalog data export."""
        catalog_data = self.mock_catalog_data.get(request.organization_id)
        if not catalog_data:
            return {
                "export_type": "catalog_data",
                "organization_id": request.organization_id,
                "export_date": datetime.utcnow().isoformat(),
                "total_products": 0,
                "products": [],
                "categories": [],
                "brands": []
            }
        
        catalog_dict = catalog_data.dict()
        
        # Apply filters
        if request.filters:
            if "category" in request.filters:
                category_filter = request.filters["category"]
                catalog_dict["products"] = [
                    p for p in catalog_dict["products"]
                    if p["category"] == category_filter
                ]
        
        return catalog_dict
    
    async def _generate_analytics_data(self, request: ExportRequest) -> Dict[str, Any]:
        """Generate analytics data export."""
        analytics_data = self.mock_analytics_data.get(request.organization_id)
        if not analytics_data:
            return {
                "export_type": "analytics_data",
                "organization_id": request.organization_id,
                "export_date": datetime.utcnow().isoformat(),
                "metrics": [],
                "reports": [],
                "user_behaviors": []
            }
        
        return analytics_data.dict()
    
    async def _generate_user_behavior_data(self, request: ExportRequest) -> Dict[str, Any]:
        """Generate user behavior data export."""
        behavior_data = self.mock_user_behaviors.get(request.organization_id)
        if not behavior_data:
            return {
                "export_type": "user_behavior",
                "organization_id": request.organization_id,
                "export_date": datetime.utcnow().isoformat(),
                "users": [],
                "sessions": [],
                "interactions": [],
                "conversions": []
            }
        
        return behavior_data.dict()
    
    async def _format_export_data(self, data: Dict[str, Any], format: ExportFormat) -> Union[str, bytes]:
        """Format export data based on requested format."""
        if format == ExportFormat.JSON:
            return json.dumps(data, indent=2, default=str)
        elif format == ExportFormat.CSV:
            return await self._convert_to_csv(data)
        elif format == ExportFormat.EXCEL:
            return await self._convert_to_excel(data)
        elif format == ExportFormat.PARQUET:
            return await self._convert_to_parquet(data)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def _convert_to_csv(self, data: Dict[str, Any]) -> str:
        """Convert data to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        if "sessions" in data:
            if data["sessions"]:
                writer.writerow(data["sessions"][0].keys())
                for session in data["sessions"]:
                    writer.writerow(session.values())
        elif "results" in data:
            if data["results"]:
                writer.writerow(data["results"][0].keys())
                for result in data["results"]:
                    writer.writerow(result.values())
        elif "products" in data:
            if data["products"]:
                writer.writerow(data["products"][0].keys())
                for product in data["products"]:
                    writer.writerow(product.values())
        
        return output.getvalue()
    
    async def _convert_to_excel(self, data: Dict[str, Any]) -> bytes:
        """Convert data to Excel format (mock implementation)."""
        # Mock Excel conversion - in real implementation would use openpyxl or xlsxwriter
        excel_data = json.dumps(data, default=str).encode('utf-8')
        return excel_data
    
    async def _convert_to_parquet(self, data: Dict[str, Any]) -> bytes:
        """Convert data to Parquet format (mock implementation)."""
        # Mock Parquet conversion - in real implementation would use pyarrow
        parquet_data = json.dumps(data, default=str).encode('utf-8')
        return parquet_data
    
    async def get_export_status(self, job_id: str) -> ExportJobStatus:
        """Get the status of an export job."""
        if job_id not in self.active_jobs:
            raise ValueError(f"Export job {job_id} not found")
        
        return self.active_jobs[job_id]
    
    async def cancel_export_job(self, job_id: str):
        """Cancel an export job."""
        if job_id not in self.active_jobs:
            raise ValueError(f"Export job {job_id} not found")
        
        job_status = self.active_jobs[job_id]
        if job_status.status in [ExportStatus.COMPLETED, ExportStatus.FAILED, ExportStatus.CANCELLED]:
            raise ValueError(f"Cannot cancel job in status: {job_status.status}")
        
        job_status.status = ExportStatus.CANCELLED
        job_status.message = "Export job cancelled by user"
        job_status.completed_at = datetime.utcnow()
        
        logger.info(f"Export job {job_id} cancelled")
    
    async def create_export_template(self, template: ExportTemplate):
        """Create an export template."""
        self.export_templates[template.template_id] = template
        logger.info(f"Created export template: {template.template_id}")
    
    async def get_export_template(self, template_id: str) -> ExportTemplate:
        """Get an export template."""
        if template_id not in self.export_templates:
            raise ValueError(f"Export template {template_id} not found")
        
        return self.export_templates[template_id]
    
    async def list_export_templates(self, organization_id: str) -> List[ExportTemplate]:
        """List export templates for an organization."""
        return [
            template for template in self.export_templates.values()
            if template.organization_id == organization_id
        ]
    
    async def delete_export_template(self, template_id: str):
        """Delete an export template."""
        if template_id not in self.export_templates:
            raise ValueError(f"Export template {template_id} not found")
        
        del self.export_templates[template_id]
        logger.info(f"Deleted export template: {template_id}")
    
    async def process_batch_export(self, request: BatchExportRequest) -> BatchExportResponse:
        """Process batch export requests."""
        batch_id = str(uuid.uuid4())
        created_jobs = []
        failed_jobs = []
        
        for export_request in request.requests:
            try:
                job_id = await self.create_export_job(export_request)
                created_jobs.append(job_id)
            except Exception as e:
                failed_jobs.append({
                    "request": export_request.dict(),
                    "error": str(e)
                })
        
        return BatchExportResponse(
            batch_id=batch_id,
            total_jobs=len(request.requests),
            created_jobs=created_jobs,
            failed_jobs=failed_jobs,
            status="completed" if not failed_jobs else "completed_with_errors",
            created_at=datetime.utcnow()
        )
    
    async def get_export_config(self) -> ExportConfig:
        """Get export configuration."""
        return self.export_config
    
    async def update_export_config(self, config: ExportConfig):
        """Update export configuration."""
        self.export_config = config
        logger.info("Updated export configuration")
    
    async def cleanup_expired_exports(self):
        """Clean up expired export files."""
        current_time = datetime.utcnow()
        expired_jobs = []
        
        for job_id, job_status in self.active_jobs.items():
            if (job_status.status == ExportStatus.COMPLETED and 
                job_status.expires_at and 
                job_status.expires_at < current_time):
                expired_jobs.append(job_id)
        
        for job_id in expired_jobs:
            del self.active_jobs[job_id]
        
        logger.info(f"Cleaned up {len(expired_jobs)} expired export jobs")
