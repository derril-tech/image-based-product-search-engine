"""FastAPI router for analytics and reporting endpoints."""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional, Union
import json

from ..models.analytics_models import (
    AnalyticsRequest, AnalyticsResponse, MetricType, TimeGranularity, ReportType,
    ReportRequest, ReportResponse, SearchEvent, UserBehavior, PerformanceAlert,
    DashboardConfig, ABTestConfig, ABTestResult, RealTimeMetric,
    BatchAnalyticsRequest, BatchAnalyticsResponse
)
from ..services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics & Reporting"])

# Initialize service
analytics_service = AnalyticsService()

@router.post("/", response_model=AnalyticsResponse)
async def get_analytics(request: AnalyticsRequest):
    """Get analytics data for specified metrics and time range."""
    try:
        return await analytics_service.get_analytics(request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reports", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """Generate comprehensive report."""
    try:
        return await analytics_service.generate_report(request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/{metric_type}")
async def get_metric_data(
    metric_type: MetricType,
    organization_id: str,
    start_time: str,  # ISO format datetime string
    end_time: str,    # ISO format datetime string
    granularity: TimeGranularity = TimeGranularity.DAY,
    limit: int = Query(100, ge=1, le=1000)
):
    """Get specific metric data."""
    try:
        from datetime import datetime
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        request = AnalyticsRequest(
            organization_id=organization_id,
            metric_types=[metric_type],
            time_range={"start_time": start_dt, "end_time": end_dt},
            granularity=granularity,
            limit=limit
        )
        
        return await analytics_service.get_analytics(request)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/track")
async def track_search_event(event: SearchEvent):
    """Track search event for analytics."""
    try:
        await analytics_service.track_search_event(event)
        return {"message": "Event tracked successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-behavior/{user_id}")
async def get_user_behavior(user_id: str, organization_id: str):
    """Get user behavior analytics."""
    try:
        return await analytics_service.get_user_behavior(user_id, organization_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts")
async def create_performance_alert(alert: PerformanceAlert):
    """Create performance alert."""
    try:
        await analytics_service.create_performance_alert(alert)
        return {"message": f"Alert {alert.alert_id} created successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_performance_alerts(
    organization_id: str,
    severity: Optional[str] = None
):
    """Get performance alerts."""
    try:
        return await analytics_service.get_performance_alerts(organization_id, severity)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dashboards")
async def create_dashboard(dashboard: DashboardConfig):
    """Create dashboard configuration."""
    try:
        await analytics_service.create_dashboard(dashboard)
        return {"message": f"Dashboard {dashboard.dashboard_id} created successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboards/{dashboard_id}")
async def get_dashboard(dashboard_id: str):
    """Get dashboard configuration."""
    try:
        return await analytics_service.get_dashboard(dashboard_id)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ab-tests")
async def create_ab_test(test: ABTestConfig):
    """Create A/B test configuration."""
    try:
        await analytics_service.create_ab_test(test)
        return {"message": f"AB test {test.test_id} created successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ab-tests/{test_id}/results")
async def get_ab_test_results(test_id: str):
    """Get A/B test results."""
    try:
        return await analytics_service.get_ab_test_results(test_id)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/real-time")
async def get_real_time_metrics(
    organization_id: str,
    metric_types: str  # Comma-separated metric types
):
    """Get real-time metrics."""
    try:
        # Parse metric types
        metric_type_list = [MetricType(mt.strip()) for mt in metric_types.split(",")]
        
        return await analytics_service.get_real_time_metrics(organization_id, metric_type_list)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid metric types")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch")
async def process_batch_analytics(request: BatchAnalyticsRequest):
    """Process batch analytics requests."""
    try:
        return await analytics_service.process_batch_analytics(request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recall-at-k")
async def get_recall_at_k_metrics(
    organization_id: str,
    k_values: str = "1,3,5,10,20",  # Comma-separated K values
    start_time: str = None,
    end_time: str = None
):
    """Get recall@K metrics."""
    try:
        from datetime import datetime, timedelta
        
        # Default to last 7 days if not specified
        if not start_time:
            start_time = (datetime.utcnow() - timedelta(days=7)).isoformat()
        if not end_time:
            end_time = datetime.utcnow().isoformat()
        
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        request = AnalyticsRequest(
            organization_id=organization_id,
            metric_types=[MetricType.RECALL_AT_K],
            time_range={"start_time": start_dt, "end_time": end_dt},
            granularity=TimeGranularity.DAY
        )
        
        response = await analytics_service.get_analytics(request)
        
        # Filter by K values if specified
        k_list = [int(k.strip()) for k in k_values.split(",")]
        filtered_data = [
            item for item in response.data 
            if item.get("k") in k_list
        ]
        
        return {
            "organization_id": organization_id,
            "k_values": k_list,
            "time_range": response.time_range,
            "data": filtered_data,
            "total_records": len(filtered_data)
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid parameters")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latency")
async def get_latency_metrics(
    organization_id: str,
    start_time: str = None,
    end_time: str = None,
    granularity: TimeGranularity = TimeGranularity.HOUR
):
    """Get latency metrics."""
    try:
        from datetime import datetime, timedelta
        
        # Default to last 24 hours if not specified
        if not start_time:
            start_time = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        if not end_time:
            end_time = datetime.utcnow().isoformat()
        
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        request = AnalyticsRequest(
            organization_id=organization_id,
            metric_types=[MetricType.LATENCY],
            time_range={"start_time": start_dt, "end_time": end_dt},
            granularity=granularity
        )
        
        return await analytics_service.get_analytics(request)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ctr")
async def get_ctr_metrics(
    organization_id: str,
    start_time: str = None,
    end_time: str = None,
    granularity: TimeGranularity = TimeGranularity.DAY
):
    """Get Click-Through Rate metrics."""
    try:
        from datetime import datetime, timedelta
        
        # Default to last 7 days if not specified
        if not start_time:
            start_time = (datetime.utcnow() - timedelta(days=7)).isoformat()
        if not end_time:
            end_time = datetime.utcnow().isoformat()
        
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        request = AnalyticsRequest(
            organization_id=organization_id,
            metric_types=[MetricType.CTR],
            time_range={"start_time": start_dt, "end_time": end_dt},
            granularity=granularity
        )
        
        return await analytics_service.get_analytics(request)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversion")
async def get_conversion_metrics(
    organization_id: str,
    start_time: str = None,
    end_time: str = None,
    granularity: TimeGranularity = TimeGranularity.DAY
):
    """Get conversion metrics."""
    try:
        from datetime import datetime, timedelta
        
        # Default to last 30 days if not specified
        if not start_time:
            start_time = (datetime.utcnow() - timedelta(days=30)).isoformat()
        if not end_time:
            end_time = datetime.utcnow().isoformat()
        
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        request = AnalyticsRequest(
            organization_id=organization_id,
            metric_types=[MetricType.CONVERSION_RATE],
            time_range={"start_time": start_dt, "end_time": end_dt},
            granularity=granularity
        )
        
        return await analytics_service.get_analytics(request)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/revenue")
async def get_revenue_metrics(
    organization_id: str,
    start_time: str = None,
    end_time: str = None,
    granularity: TimeGranularity = TimeGranularity.DAY
):
    """Get revenue metrics."""
    try:
        from datetime import datetime, timedelta
        
        # Default to last 30 days if not specified
        if not start_time:
            start_time = (datetime.utcnow() - timedelta(days=30)).isoformat()
        if not end_time:
            end_time = datetime.utcnow().isoformat()
        
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        request = AnalyticsRequest(
            organization_id=organization_id,
            metric_types=[MetricType.REVENUE],
            time_range={"start_time": start_dt, "end_time": end_dt},
            granularity=granularity
        )
        
        return await analytics_service.get_analytics(request)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-volume")
async def get_search_volume_metrics(
    organization_id: str,
    start_time: str = None,
    end_time: str = None,
    granularity: TimeGranularity = TimeGranularity.DAY
):
    """Get search volume metrics."""
    try:
        from datetime import datetime, timedelta
        
        # Default to last 7 days if not specified
        if not start_time:
            start_time = (datetime.utcnow() - timedelta(days=7)).isoformat()
        if not end_time:
            end_time = datetime.utcnow().isoformat()
        
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        request = AnalyticsRequest(
            organization_id=organization_id,
            metric_types=[MetricType.SEARCH_VOLUME],
            time_range={"start_time": start_dt, "end_time": end_dt},
            granularity=granularity
        )
        
        return await analytics_service.get_analytics(request)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quality")
async def get_quality_metrics(
    organization_id: str,
    start_time: str = None,
    end_time: str = None,
    granularity: TimeGranularity = TimeGranularity.DAY
):
    """Get search quality metrics."""
    try:
        from datetime import datetime, timedelta
        
        # Default to last 7 days if not specified
        if not start_time:
            start_time = (datetime.utcnow() - timedelta(days=7)).isoformat()
        if not end_time:
            end_time = datetime.utcnow().isoformat()
        
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        request = AnalyticsRequest(
            organization_id=organization_id,
            metric_types=[MetricType.QUALITY_SCORE],
            time_range={"start_time": start_dt, "end_time": end_dt},
            granularity=granularity
        )
        
        return await analytics_service.get_analytics(request)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/configs")
async def get_analytics_configs():
    """Get available analytics configurations."""
    configs = {
        "metric_types": {
            "recall_at_k": {
                "description": "Recall at K positions",
                "k_values": [1, 3, 5, 10, 20],
                "best_for": "Search quality assessment"
            },
            "latency": {
                "description": "Search response time metrics",
                "percentiles": [50, 95, 99],
                "best_for": "Performance monitoring"
            },
            "ctr": {
                "description": "Click-Through Rate metrics",
                "metrics": ["total_impressions", "total_clicks", "ctr"],
                "best_for": "User engagement analysis"
            },
            "conversion_rate": {
                "description": "Search to purchase conversion",
                "metrics": ["total_searches", "total_conversions", "revenue"],
                "best_for": "Revenue attribution"
            },
            "revenue": {
                "description": "Revenue metrics from search",
                "metrics": ["total_revenue", "avg_order_value", "revenue_per_search"],
                "best_for": "Business impact measurement"
            },
            "search_volume": {
                "description": "Search activity volume",
                "metrics": ["total_searches", "unique_queries", "unique_users"],
                "best_for": "Usage analytics"
            },
            "quality_score": {
                "description": "Search quality assessment",
                "metrics": ["relevance", "diversity", "user_satisfaction"],
                "best_for": "Quality optimization"
            }
        },
        "time_granularities": {
            "minute": "For real-time monitoring",
            "hour": "For hourly trends",
            "day": "For daily analysis",
            "week": "For weekly patterns",
            "month": "For monthly trends"
        },
        "report_types": {
            "search_performance": "Search quality and performance metrics",
            "user_behavior": "User interaction and engagement patterns",
            "revenue_analytics": "Revenue attribution and business impact",
            "quality_metrics": "Search quality and relevance metrics",
            "system_health": "System performance and health monitoring",
            "custom": "Custom report with selected metrics"
        }
    }
    
    return configs

@router.get("/health")
async def analytics_health():
    """Get analytics service health status."""
    try:
        health_status = {
            "status": "healthy",
            "services": {
                "analytics_service": "available",
                "data_storage": "available",
                "real_time_processing": "available"
            },
            "metrics": {
                "total_events": len(analytics_service.search_events),
                "total_alerts": len(analytics_service.performance_alerts),
                "total_dashboards": len(analytics_service.dashboards),
                "total_ab_tests": len(analytics_service.ab_tests)
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
