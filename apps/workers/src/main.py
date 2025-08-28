"""Main FastAPI application for image search workers."""

import uvicorn
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .routers import ingest, preprocess, detect, embed, index, search, report, export, cdn, security, audit, billing
from .observability.telemetry import init_telemetry
from .observability.prometheus import init_prometheus_metrics, get_prometheus_metrics
from .observability.sentry import init_sentry
from .services.audit_logger import init_audit_logger

app = FastAPI(
    title="Image Search Workers",
    description="Python workers for image-based product search",
    version="0.1.0",
)

# Initialize observability
if settings.enable_telemetry:
    telemetry_config = {
        'service_name': 'image-search-workers',
        'service_version': '0.1.0',
        'environment': settings.sentry_environment,
        'otlp_endpoint': settings.otlp_endpoint,
        'otlp_headers': settings.otlp_headers,
        'instrument_fastapi': True,
        'instrument_requests': True,
        'instrument_postgresql': True,
        'instrument_redis': True,
        'instrument_boto3': True
    }
    init_telemetry(telemetry_config)

if settings.enable_prometheus:
    init_prometheus_metrics()

if settings.enable_sentry:
    sentry_config = {
        'sentry_dsn': settings.sentry_dsn,
        'environment': settings.sentry_environment,
        'service_name': 'image-search-workers',
        'service_version': '0.1.0',
        'traces_sample_rate': settings.sentry_traces_sample_rate,
        'profiles_sample_rate': settings.sentry_profiles_sample_rate
    }
    init_sentry(sentry_config)

# Initialize audit logging
if settings.enable_audit_logging:
    audit_config = {
        'enabled': settings.enable_audit_logging,
        'log_level': settings.audit_log_level,
        'retention_days': settings.audit_retention_days,
        'batch_size': settings.audit_batch_size,
        'flush_interval': settings.audit_flush_interval,
        'file_enabled': settings.audit_file_enabled,
        'database_enabled': settings.audit_database_enabled,
        'elasticsearch_enabled': settings.audit_elasticsearch_enabled,
        'log_file_path': settings.audit_log_file_path
    }
    init_audit_logger(audit_config)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Record metrics
    metrics = get_prometheus_metrics()
    if metrics:
        metrics.record_http_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=process_time
        )
    
    return response

# Include routers
app.include_router(ingest.router, prefix="/api/v1/ingest", tags=["ingest"])
app.include_router(preprocess.router, prefix="/api/v1/preprocess", tags=["preprocess"])
app.include_router(detect.router, prefix="/api/v1/detect", tags=["detect"])
app.include_router(embed.router, prefix="/api/v1/embed", tags=["embed"])
app.include_router(index.router, prefix="/api/v1/index", tags=["index"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(report.router, prefix="/api/v1/report", tags=["report"])
app.include_router(export.router, prefix="/api/v1/export", tags=["export"])
app.include_router(cdn.router, prefix="/api/v1", tags=["cdn"])
app.include_router(security.router, prefix="/api/v1", tags=["security"])
app.include_router(audit.router, prefix="/api/v1", tags=["audit"])
app.include_router(billing.router, prefix="/api/v1", tags=["billing"])

# Include observability endpoints
from .observability.prometheus import router as prometheus_router
app.include_router(prometheus_router, prefix="/observability", tags=["observability"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "image-search-workers"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with Sentry integration"""
    from .observability.sentry import capture_exception
    
    # Capture exception in Sentry
    capture_exception(exc, {
        "request_method": request.method,
        "request_url": str(request.url),
        "request_path": request.url.path
    })
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
