# Prometheus metrics endpoint
# Created automatically by Cursor AI (2024-12-19)

import logging
from typing import Dict, Any
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, 
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, multiprocess
)
from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse

logger = logging.getLogger(__name__)

class PrometheusMetrics:
    """Prometheus metrics collector"""
    
    def __init__(self, registry: CollectorRegistry = None):
        self.registry = registry or CollectorRegistry()
        
        # HTTP metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total number of HTTP requests',
            ['method', 'path', 'status_code'],
            registry=self.registry
        )
        
        self.http_request_duration_seconds = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'path', 'status_code'],
            registry=self.registry
        )
        
        # Image processing metrics
        self.image_processing_total = Counter(
            'image_processing_total',
            'Total number of images processed',
            ['operation', 'status'],
            registry=self.registry
        )
        
        self.image_processing_duration_seconds = Histogram(
            'image_processing_duration_seconds',
            'Image processing duration in seconds',
            ['operation', 'status'],
            registry=self.registry
        )
        
        # Search metrics
        self.search_requests_total = Counter(
            'search_requests_total',
            'Total number of search requests',
            ['query_type', 'status'],
            registry=self.registry
        )
        
        self.search_duration_seconds = Histogram(
            'search_duration_seconds',
            'Search duration in seconds',
            ['query_type', 'status'],
            registry=self.registry
        )
        
        # Error metrics
        self.errors_total = Counter(
            'errors_total',
            'Total number of errors',
            ['error_type', 'service'],
            registry=self.registry
        )
        
        # Queue metrics
        self.queue_size = Gauge(
            'queue_size',
            'Current queue size',
            ['queue_name'],
            registry=self.registry
        )
        
        # System metrics
        self.memory_usage_bytes = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes',
            ['service'],
            registry=self.registry
        )
        
        self.cpu_usage_percent = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage',
            ['service'],
            registry=self.registry
        )
        
        # Database metrics
        self.db_connections_active = Gauge(
            'db_connections_active',
            'Active database connections',
            ['database'],
            registry=self.registry
        )
        
        self.db_query_duration_seconds = Histogram(
            'db_query_duration_seconds',
            'Database query duration in seconds',
            ['database', 'query_type'],
            registry=self.registry
        )
        
        # Cache metrics
        self.cache_hits_total = Counter(
            'cache_hits_total',
            'Total number of cache hits',
            ['cache_type'],
            registry=self.registry
        )
        
        self.cache_misses_total = Counter(
            'cache_misses_total',
            'Total number of cache misses',
            ['cache_type'],
            registry=self.registry
        )
        
        # Vector search metrics
        self.vector_search_total = Counter(
            'vector_search_total',
            'Total number of vector searches',
            ['index_name', 'status'],
            registry=self.registry
        )
        
        self.vector_search_duration_seconds = Histogram(
            'vector_search_duration_seconds',
            'Vector search duration in seconds',
            ['index_name', 'status'],
            registry=self.registry
        )
        
        # Embedding generation metrics
        self.embedding_generation_total = Counter(
            'embedding_generation_total',
            'Total number of embeddings generated',
            ['model_name', 'input_type'],
            registry=self.registry
        )
        
        self.embedding_generation_duration_seconds = Histogram(
            'embedding_generation_duration_seconds',
            'Embedding generation duration in seconds',
            ['model_name', 'input_type'],
            registry=self.registry
        )
    
    def record_http_request(self, method: str, path: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        self.http_requests_total.labels(
            method=method,
            path=path,
            status_code=str(status_code)
        ).inc()
        
        self.http_request_duration_seconds.labels(
            method=method,
            path=path,
            status_code=str(status_code)
        ).observe(duration)
    
    def record_image_processing(self, operation: str, duration: float, success: bool = True):
        """Record image processing metrics"""
        status = 'success' if success else 'failure'
        
        self.image_processing_total.labels(
            operation=operation,
            status=status
        ).inc()
        
        self.image_processing_duration_seconds.labels(
            operation=operation,
            status=status
        ).observe(duration)
    
    def record_search(self, query_type: str, duration: float, success: bool = True):
        """Record search metrics"""
        status = 'success' if success else 'failure'
        
        self.search_requests_total.labels(
            query_type=query_type,
            status=status
        ).inc()
        
        self.search_duration_seconds.labels(
            query_type=query_type,
            status=status
        ).observe(duration)
    
    def record_error(self, error_type: str, service: str = 'unknown'):
        """Record error metrics"""
        self.errors_total.labels(
            error_type=error_type,
            service=service
        ).inc()
    
    def update_queue_size(self, queue_name: str, size: int):
        """Update queue size metric"""
        self.queue_size.labels(queue_name=queue_name).set(size)
    
    def update_memory_usage(self, service: str, bytes_used: int):
        """Update memory usage metric"""
        self.memory_usage_bytes.labels(service=service).set(bytes_used)
    
    def update_cpu_usage(self, service: str, percent: float):
        """Update CPU usage metric"""
        self.cpu_usage_percent.labels(service=service).set(percent)
    
    def update_db_connections(self, database: str, connections: int):
        """Update database connections metric"""
        self.db_connections_active.labels(database=database).set(connections)
    
    def record_db_query(self, database: str, query_type: str, duration: float):
        """Record database query metrics"""
        self.db_query_duration_seconds.labels(
            database=database,
            query_type=query_type
        ).observe(duration)
    
    def record_cache_hit(self, cache_type: str):
        """Record cache hit"""
        self.cache_hits_total.labels(cache_type=cache_type).inc()
    
    def record_cache_miss(self, cache_type: str):
        """Record cache miss"""
        self.cache_misses_total.labels(cache_type=cache_type).inc()
    
    def record_vector_search(self, index_name: str, duration: float, success: bool = True):
        """Record vector search metrics"""
        status = 'success' if success else 'failure'
        
        self.vector_search_total.labels(
            index_name=index_name,
            status=status
        ).inc()
        
        self.vector_search_duration_seconds.labels(
            index_name=index_name,
            status=status
        ).observe(duration)
    
    def record_embedding_generation(self, model_name: str, input_type: str, duration: float):
        """Record embedding generation metrics"""
        self.embedding_generation_total.labels(
            model_name=model_name,
            input_type=input_type
        ).inc()
        
        self.embedding_generation_duration_seconds.labels(
            model_name=model_name,
            input_type=input_type
        ).observe(duration)

# Global metrics instance
_metrics: PrometheusMetrics = None

def init_prometheus_metrics(registry: CollectorRegistry = None) -> PrometheusMetrics:
    """Initialize Prometheus metrics globally"""
    global _metrics
    
    if _metrics is None:
        _metrics = PrometheusMetrics(registry)
    
    return _metrics

def get_prometheus_metrics() -> PrometheusMetrics:
    """Get the global Prometheus metrics instance"""
    return _metrics

# FastAPI router for metrics endpoint
router = APIRouter()

@router.get("/metrics")
async def metrics_endpoint():
    """Prometheus metrics endpoint"""
    try:
        # Generate metrics
        if _metrics:
            metrics_data = generate_latest(_metrics.registry)
        else:
            # Fallback to default registry
            metrics_data = generate_latest()
        
        return Response(
            content=metrics_data,
            media_type=CONTENT_TYPE_LATEST
        )
        
    except Exception as e:
        logger.error(f"Failed to generate metrics: {e}")
        return PlainTextResponse(
            content=f"Error generating metrics: {str(e)}",
            status_code=500
        )

@router.get("/health")
async def health_check():
    """Health check endpoint with basic metrics"""
    try:
        # Basic health check
        health_status = {
            "status": "healthy",
            "service": "image-search-workers",
            "metrics_available": _metrics is not None
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
