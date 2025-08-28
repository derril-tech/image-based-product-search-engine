"""Data ingestion service for image search workers."""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from ..models.ingest_models import (
    IngestRequest, IngestJobStatus, IngestStatus, ConnectorInfo,
    ConnectionTestResult, ConnectorType
)
from ..connectors.shopify_connector import ShopifyConnector
from ..connectors.bigcommerce_connector import BigCommerceConnector
from ..connectors.woocommerce_connector import WooCommerceConnector
from ..connectors.csv_connector import CSVConnector
from ..connectors.api_connector import APIConnector

logger = logging.getLogger(__name__)

class IngestService:
    """Service for managing data ingestion jobs."""
    
    def __init__(self):
        self.active_jobs: Dict[str, IngestJobStatus] = {}
        self.connectors = {
            ConnectorType.SHOPIFY: ShopifyConnector(),
            ConnectorType.BIGCOMMERCE: BigCommerceConnector(),
            ConnectorType.WOOCOMMERCE: WooCommerceConnector(),
            ConnectorType.CSV: CSVConnector(),
            ConnectorType.API: APIConnector(),
        }
    
    async def start_ingestion(self, request: IngestRequest) -> str:
        """Start a new ingestion job."""
        job_id = str(uuid.uuid4())
        
        # Create job status
        job_status = IngestJobStatus(
            job_id=job_id,
            status=IngestStatus.PENDING,
            progress=0.0,
            message="Job created",
            started_at=datetime.utcnow()
        )
        
        self.active_jobs[job_id] = job_status
        
        logger.info(f"Started ingestion job {job_id} for connector {request.connector_id}")
        
        return job_id
    
    async def process_ingestion(self, job_id: str):
        """Process an ingestion job."""
        if job_id not in self.active_jobs:
            logger.error(f"Job {job_id} not found")
            return
        
        job_status = self.active_jobs[job_id]
        job_status.status = IngestStatus.PROCESSING
        job_status.message = "Processing started"
        
        try:
            # Get connector type from job configuration
            # This would typically come from the database
            connector_type = ConnectorType.SHOPIFY  # Default for now
            
            if connector_type not in self.connectors:
                raise ValueError(f"Unsupported connector type: {connector_type}")
            
            connector = self.connectors[connector_type]
            
            # Process the ingestion
            await self._process_with_connector(connector, job_id)
            
            # Mark as completed
            job_status.status = IngestStatus.COMPLETED
            job_status.progress = 100.0
            job_status.message = "Processing completed successfully"
            job_status.completed_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            job_status.status = IngestStatus.FAILED
            job_status.message = f"Processing failed: {str(e)}"
            job_status.error = str(e)
            job_status.completed_at = datetime.utcnow()
    
    async def _process_with_connector(self, connector, job_id: str):
        """Process ingestion with a specific connector."""
        job_status = self.active_jobs[job_id]
        
        # Update progress
        job_status.progress = 10.0
        job_status.message = "Connecting to data source"
        
        # Test connection
        connection_result = await connector.test_connection()
        if not connection_result.success:
            raise Exception(f"Connection failed: {connection_result.message}")
        
        # Update progress
        job_status.progress = 20.0
        job_status.message = "Fetching data"
        
        # Fetch data
        data = await connector.fetch_data()
        
        # Update progress
        job_status.progress = 50.0
        job_status.message = "Processing data"
        
        # Process and normalize data
        processed_data = await connector.process_data(data)
        
        # Update progress
        job_status.progress = 80.0
        job_status.message = "Saving to database"
        
        # Save to database
        await connector.save_data(processed_data)
        
        # Update stats
        job_status.stats = {
            "total_products": len(processed_data.get("products", [])),
            "total_images": len(processed_data.get("images", [])),
            "processing_time": (datetime.utcnow() - job_status.started_at).total_seconds()
        }
    
    async def get_ingestion_status(self, job_id: str) -> IngestJobStatus:
        """Get the status of an ingestion job."""
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        return self.active_jobs[job_id]
    
    async def cancel_ingestion(self, job_id: str):
        """Cancel an ongoing ingestion job."""
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job_status = self.active_jobs[job_id]
        
        if job_status.status in [IngestStatus.COMPLETED, IngestStatus.FAILED, IngestStatus.CANCELLED]:
            raise ValueError(f"Cannot cancel job in status: {job_status.status}")
        
        job_status.status = IngestStatus.CANCELLED
        job_status.message = "Job cancelled by user"
        job_status.completed_at = datetime.utcnow()
        
        logger.info(f"Cancelled ingestion job {job_id}")
    
    async def list_connectors(self) -> List[ConnectorInfo]:
        """List available data connectors."""
        connectors = []
        
        for connector_type, connector in self.connectors.items():
            info = await connector.get_info()
            connectors.append(info)
        
        return connectors
    
    async def test_connection(self, connector_id: str, config: Dict[str, Any]) -> ConnectionTestResult:
        """Test connection to a data source."""
        try:
            connector_type = ConnectorType(connector_id)
            
            if connector_type not in self.connectors:
                return ConnectionTestResult(
                    success=False,
                    message=f"Unsupported connector type: {connector_id}"
                )
            
            connector = self.connectors[connector_type]
            result = await connector.test_connection(config)
            
            return result
            
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return ConnectionTestResult(
                success=False,
                message=f"Connection test failed: {str(e)}"
            )
