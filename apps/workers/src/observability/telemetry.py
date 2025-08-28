# Telemetry module for OpenTelemetry tracing and metrics
# Created automatically by Cursor AI (2024-12-19)

import os
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager
import time
from functools import wraps

# OpenTelemetry imports
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.boto3 import Boto3Instrumentor

logger = logging.getLogger(__name__)

class TelemetryManager:
    """Manages OpenTelemetry tracing and metrics"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.service_name = config.get('service_name', 'image-search-workers')
        self.service_version = config.get('service_version', '0.1.0')
        self.environment = config.get('environment', 'development')
        
        # Initialize providers
        self.tracer_provider = None
        self.meter_provider = None
        self.tracer = None
        self.meter = None
        
        # Initialize telemetry
        self._setup_tracing()
        self._setup_metrics()
        self._setup_instrumentation()
    
    def _setup_tracing(self):
        """Setup OpenTelemetry tracing"""
        try:
            # Create tracer provider
            self.tracer_provider = TracerProvider()
            
            # Add span processors
            if self.config.get('otlp_endpoint'):
                # OTLP exporter for production
                otlp_exporter = OTLPSpanExporter(
                    endpoint=self.config['otlp_endpoint'],
                    headers=self.config.get('otlp_headers', {})
                )
                self.tracer_provider.add_span_processor(
                    BatchSpanProcessor(otlp_exporter)
                )
            else:
                # Console exporter for development
                console_exporter = ConsoleSpanExporter()
                self.tracer_provider.add_span_processor(
                    BatchSpanProcessor(console_exporter)
                )
            
            # Set global tracer provider
            trace.set_tracer_provider(self.tracer_provider)
            
            # Create tracer
            self.tracer = trace.get_tracer(self.service_name, self.service_version)
            
            logger.info("Tracing setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup tracing: {e}")
    
    def _setup_metrics(self):
        """Setup OpenTelemetry metrics"""
        try:
            # Create metric reader
            if self.config.get('otlp_endpoint'):
                # OTLP exporter for production
                metric_exporter = OTLPMetricExporter(
                    endpoint=self.config['otlp_endpoint'],
                    headers=self.config.get('otlp_headers', {})
                )
                metric_reader = PeriodicExportingMetricReader(metric_exporter)
            else:
                # Console exporter for development
                console_exporter = ConsoleMetricExporter()
                metric_reader = PeriodicExportingMetricReader(console_exporter)
            
            # Create meter provider
            self.meter_provider = MeterProvider(metric_readers=[metric_reader])
            
            # Set global meter provider
            metrics.set_meter_provider(self.meter_provider)
            
            # Create meter
            self.meter = metrics.get_meter(self.service_name, self.service_version)
            
            # Create common metrics
            self._create_common_metrics()
            
            logger.info("Metrics setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup metrics: {e}")
    
    def _create_common_metrics(self):
        """Create common metrics for the application"""
        if not self.meter:
            return
        
        # Request metrics
        self.request_counter = self.meter.create_counter(
            name="http_requests_total",
            description="Total number of HTTP requests",
            unit="1"
        )
        
        self.request_duration = self.meter.create_histogram(
            name="http_request_duration_seconds",
            description="HTTP request duration in seconds",
            unit="s"
        )
        
        # Image processing metrics
        self.image_processing_counter = self.meter.create_counter(
            name="image_processing_total",
            description="Total number of images processed",
            unit="1"
        )
        
        self.image_processing_duration = self.meter.create_histogram(
            name="image_processing_duration_seconds",
            description="Image processing duration in seconds",
            unit="s"
        )
        
        # Search metrics
        self.search_counter = self.meter.create_counter(
            name="search_requests_total",
            description="Total number of search requests",
            unit="1"
        )
        
        self.search_duration = self.meter.create_histogram(
            name="search_duration_seconds",
            description="Search duration in seconds",
            unit="s"
        )
        
        # Error metrics
        self.error_counter = self.meter.create_counter(
            name="errors_total",
            description="Total number of errors",
            unit="1"
        )
        
        # Queue metrics
        self.queue_size = self.meter.create_up_down_counter(
            name="queue_size",
            description="Current queue size",
            unit="1"
        )
    
    def _setup_instrumentation(self):
        """Setup automatic instrumentation"""
        try:
            # Instrument FastAPI
            if self.config.get('instrument_fastapi', True):
                FastAPIInstrumentor.instrument()
            
            # Instrument HTTP requests
            if self.config.get('instrument_requests', True):
                RequestsInstrumentor().instrument()
            
            # Instrument PostgreSQL
            if self.config.get('instrument_postgresql', True):
                Psycopg2Instrumentor().instrument()
            
            # Instrument Redis
            if self.config.get('instrument_redis', True):
                RedisInstrumentor().instrument()
            
            # Instrument AWS SDK
            if self.config.get('instrument_boto3', True):
                Boto3Instrumentor().instrument()
            
            logger.info("Instrumentation setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup instrumentation: {e}")
    
    def get_tracer(self):
        """Get the tracer instance"""
        return self.tracer
    
    def get_meter(self):
        """Get the meter instance"""
        return self.meter
    
    @contextmanager
    def trace_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Context manager for creating spans"""
        if not self.tracer:
            yield
            return
        
        with self.tracer.start_as_current_span(name, attributes=attributes or {}) as span:
            try:
                yield span
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise
    
    def trace_function(self, name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None):
        """Decorator for tracing functions"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                span_name = name or f"{func.__module__}.{func.__name__}"
                with self.trace_span(span_name, attributes) as span:
                    try:
                        result = func(*args, **kwargs)
                        span.set_status(trace.Status(trace.StatusCode.OK))
                        return result
                    except Exception as e:
                        span.record_exception(e)
                        span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                        raise
            return wrapper
        return decorator
    
    def record_request(self, method: str, path: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        if not self.request_counter or not self.request_duration:
            return
        
        # Record request count
        self.request_counter.add(1, {
            "method": method,
            "path": path,
            "status_code": str(status_code)
        })
        
        # Record request duration
        self.request_duration.record(duration, {
            "method": method,
            "path": path,
            "status_code": str(status_code)
        })
    
    def record_image_processing(self, operation: str, duration: float, success: bool = True):
        """Record image processing metrics"""
        if not self.image_processing_counter or not self.image_processing_duration:
            return
        
        # Record processing count
        self.image_processing_counter.add(1, {
            "operation": operation,
            "success": str(success).lower()
        })
        
        # Record processing duration
        self.image_processing_duration.record(duration, {
            "operation": operation,
            "success": str(success).lower()
        })
    
    def record_search(self, query_type: str, duration: float, result_count: int = 0):
        """Record search metrics"""
        if not self.search_counter or not self.search_duration:
            return
        
        # Record search count
        self.search_counter.add(1, {
            "query_type": query_type
        })
        
        # Record search duration
        self.search_duration.record(duration, {
            "query_type": query_type,
            "result_count": str(result_count)
        })
    
    def record_error(self, error_type: str, error_message: str = ""):
        """Record error metrics"""
        if not self.error_counter:
            return
        
        self.error_counter.add(1, {
            "error_type": error_type,
            "error_message": error_message[:100]  # Truncate long messages
        })
    
    def update_queue_size(self, queue_name: str, size: int):
        """Update queue size metric"""
        if not self.queue_size:
            return
        
        self.queue_size.add(size, {"queue_name": queue_name})
    
    def shutdown(self):
        """Shutdown telemetry"""
        try:
            if self.tracer_provider:
                self.tracer_provider.shutdown()
            
            if self.meter_provider:
                self.meter_provider.shutdown()
            
            logger.info("Telemetry shutdown completed")
            
        except Exception as e:
            logger.error(f"Failed to shutdown telemetry: {e}")

# Global telemetry manager instance
_telemetry_manager: Optional[TelemetryManager] = None

def init_telemetry(config: Dict[str, Any]) -> TelemetryManager:
    """Initialize telemetry globally"""
    global _telemetry_manager
    
    if _telemetry_manager is None:
        _telemetry_manager = TelemetryManager(config)
    
    return _telemetry_manager

def get_telemetry() -> Optional[TelemetryManager]:
    """Get the global telemetry manager"""
    return _telemetry_manager

def get_tracer():
    """Get the global tracer"""
    telemetry = get_telemetry()
    return telemetry.get_tracer() if telemetry else None

def get_meter():
    """Get the global meter"""
    telemetry = get_telemetry()
    return telemetry.get_meter() if telemetry else None
