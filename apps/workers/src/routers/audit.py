# Audit Router for Audit Logging Operations
# Created automatically by Cursor AI (2024-12-19)

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict
import logging
from pydantic import BaseModel
from datetime import datetime, timedelta

from ..services.audit_logger import AuditLogger, AuditEventType, AuditSeverity, AuditEvent
from ..dependencies import get_audit_logger

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit", tags=["Audit"])

class AuditEventResponse(BaseModel):
    event_id: str
    event_type: str
    timestamp: str
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource_type: Optional[str]
    resource_id: Optional[str]
    action: str
    details: Dict
    severity: str
    success: bool
    error_message: Optional[str]
    duration_ms: Optional[int]
    metadata: Dict

class AuditStatisticsResponse(BaseModel):
    total_events: int
    events_by_type: Dict[str, int]
    events_by_severity: Dict[str, int]
    events_by_user: Dict[str, int]
    success_rate: float
    average_duration_ms: float

class AuditSearchRequest(BaseModel):
    user_id: Optional[str] = None
    event_type: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    severity: Optional[str] = None
    limit: int = 100
    offset: int = 0

@router.get("/events", response_model=List[AuditEventResponse])
async def get_audit_events(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(100, description="Number of events to return"),
    offset: int = Query(0, description="Number of events to skip"),
    audit_logger: AuditLogger = Depends(get_audit_logger)
):
    """Get audit events with optional filtering"""
    try:
        if not audit_logger:
            raise HTTPException(status_code=503, detail="Audit logging not available")
        
        # Parse datetime strings
        start_dt = None
        end_dt = None
        
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_time format")
        
        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_time format")
        
        # Parse event type and severity
        event_type_enum = None
        if event_type:
            try:
                event_type_enum = AuditEventType(event_type)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid event_type")
        
        severity_enum = None
        if severity:
            try:
                severity_enum = AuditSeverity(severity)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid severity")
        
        # Search events
        events = await audit_logger.search_events(
            user_id=user_id,
            event_type=event_type_enum,
            resource_type=resource_type,
            resource_id=resource_id,
            start_time=start_dt,
            end_time=end_dt,
            severity=severity_enum,
            limit=limit,
            offset=offset
        )
        
        # Convert to response format
        response_events = []
        for event in events:
            response_events.append(AuditEventResponse(
                event_id=event.event_id,
                event_type=event.event_type.value,
                timestamp=event.timestamp.isoformat(),
                user_id=event.user_id,
                session_id=event.session_id,
                ip_address=event.ip_address,
                user_agent=event.user_agent,
                resource_type=event.resource_type,
                resource_id=event.resource_id,
                action=event.action,
                details=event.details,
                severity=event.severity.value,
                success=event.success,
                error_message=event.error_message,
                duration_ms=event.duration_ms,
                metadata=event.metadata
            ))
        
        return response_events
        
    except Exception as e:
        logger.error(f"Failed to get audit events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/search", response_model=List[AuditEventResponse])
async def search_audit_events(
    request: AuditSearchRequest,
    audit_logger: AuditLogger = Depends(get_audit_logger)
):
    """Search audit events with complex criteria"""
    try:
        if not audit_logger:
            raise HTTPException(status_code=503, detail="Audit logging not available")
        
        # Parse datetime strings
        start_dt = None
        end_dt = None
        
        if request.start_time:
            try:
                start_dt = datetime.fromisoformat(request.start_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_time format")
        
        if request.end_time:
            try:
                end_dt = datetime.fromisoformat(request.end_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_time format")
        
        # Parse event type and severity
        event_type_enum = None
        if request.event_type:
            try:
                event_type_enum = AuditEventType(request.event_type)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid event_type")
        
        severity_enum = None
        if request.severity:
            try:
                severity_enum = AuditSeverity(request.severity)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid severity")
        
        # Search events
        events = await audit_logger.search_events(
            user_id=request.user_id,
            event_type=event_type_enum,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            start_time=start_dt,
            end_time=end_dt,
            severity=severity_enum,
            limit=request.limit,
            offset=request.offset
        )
        
        # Convert to response format
        response_events = []
        for event in events:
            response_events.append(AuditEventResponse(
                event_id=event.event_id,
                event_type=event.event_type.value,
                timestamp=event.timestamp.isoformat(),
                user_id=event.user_id,
                session_id=event.session_id,
                ip_address=event.ip_address,
                user_agent=event.user_agent,
                resource_type=event.resource_type,
                resource_id=event.resource_id,
                action=event.action,
                details=event.details,
                severity=event.severity.value,
                success=event.success,
                error_message=event.error_message,
                duration_ms=event.duration_ms,
                metadata=event.metadata
            ))
        
        return response_events
        
    except Exception as e:
        logger.error(f"Failed to search audit events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics", response_model=AuditStatisticsResponse)
async def get_audit_statistics(
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    audit_logger: AuditLogger = Depends(get_audit_logger)
):
    """Get audit event statistics"""
    try:
        if not audit_logger:
            raise HTTPException(status_code=503, detail="Audit logging not available")
        
        # Parse datetime strings
        start_dt = None
        end_dt = None
        
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_time format")
        
        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_time format")
        
        # Get statistics
        stats = await audit_logger.get_event_statistics(
            start_time=start_dt,
            end_time=end_dt,
            user_id=user_id
        )
        
        return AuditStatisticsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Failed to get audit statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/types")
async def get_event_types():
    """Get available audit event types"""
    try:
        event_types = [event_type.value for event_type in AuditEventType]
        return {
            "event_types": event_types,
            "count": len(event_types)
        }
        
    except Exception as e:
        logger.error(f"Failed to get event types: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/severities")
async def get_severity_levels():
    """Get available severity levels"""
    try:
        severities = [severity.value for severity in AuditSeverity]
        return {
            "severities": severities,
            "count": len(severities)
        }
        
    except Exception as e:
        logger.error(f"Failed to get severity levels: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/cleanup")
async def cleanup_old_events(
    audit_logger: AuditLogger = Depends(get_audit_logger)
):
    """Clean up old audit events based on retention policy"""
    try:
        if not audit_logger:
            raise HTTPException(status_code=503, detail="Audit logging not available")
        
        await audit_logger.cleanup_old_events()
        
        return {
            "message": "Audit event cleanup completed",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup old events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_audit_status(
    audit_logger: AuditLogger = Depends(get_audit_logger)
):
    """Get audit logger status"""
    try:
        if not audit_logger:
            return {
                "enabled": False,
                "message": "Audit logging not available"
            }
        
        status = audit_logger.get_status()
        return status
        
    except Exception as e:
        logger.error(f"Failed to get audit status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/flush")
async def flush_audit_events(
    audit_logger: AuditLogger = Depends(get_audit_logger)
):
    """Manually flush queued audit events"""
    try:
        if not audit_logger:
            raise HTTPException(status_code=503, detail="Audit logging not available")
        
        await audit_logger.flush()
        
        return {
            "message": "Audit events flushed successfully",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Failed to flush audit events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/recent")
async def get_recent_events(
    hours: int = Query(24, description="Number of hours to look back"),
    limit: int = Query(50, description="Number of events to return"),
    audit_logger: AuditLogger = Depends(get_audit_logger)
):
    """Get recent audit events"""
    try:
        if not audit_logger:
            raise HTTPException(status_code=503, detail="Audit logging not available")
        
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # Search events
        events = await audit_logger.search_events(
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=0
        )
        
        # Convert to response format
        response_events = []
        for event in events:
            response_events.append(AuditEventResponse(
                event_id=event.event_id,
                event_type=event.event_type.value,
                timestamp=event.timestamp.isoformat(),
                user_id=event.user_id,
                session_id=event.session_id,
                ip_address=event.ip_address,
                user_agent=event.user_agent,
                resource_type=event.resource_type,
                resource_id=event.resource_id,
                action=event.action,
                details=event.details,
                severity=event.severity.value,
                success=event.success,
                error_message=event.error_message,
                duration_ms=event.duration_ms,
                metadata=event.metadata
            ))
        
        return {
            "events": response_events,
            "count": len(response_events),
            "time_range": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "hours": hours
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get recent events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/user/{user_id}")
async def get_user_events(
    user_id: str,
    limit: int = Query(100, description="Number of events to return"),
    offset: int = Query(0, description="Number of events to skip"),
    audit_logger: AuditLogger = Depends(get_audit_logger)
):
    """Get audit events for a specific user"""
    try:
        if not audit_logger:
            raise HTTPException(status_code=503, detail="Audit logging not available")
        
        # Search events for user
        events = await audit_logger.search_events(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        # Convert to response format
        response_events = []
        for event in events:
            response_events.append(AuditEventResponse(
                event_id=event.event_id,
                event_type=event.event_type.value,
                timestamp=event.timestamp.isoformat(),
                user_id=event.user_id,
                session_id=event.session_id,
                ip_address=event.ip_address,
                user_agent=event.user_agent,
                resource_type=event.resource_type,
                resource_id=event.resource_id,
                action=event.action,
                details=event.details,
                severity=event.severity.value,
                success=event.success,
                error_message=event.error_message,
                duration_ms=event.duration_ms,
                metadata=event.metadata
            ))
        
        return {
            "user_id": user_id,
            "events": response_events,
            "count": len(response_events)
        }
        
    except Exception as e:
        logger.error(f"Failed to get user events: {e}")
        raise HTTPException(status_code=500, detail=str(e))
