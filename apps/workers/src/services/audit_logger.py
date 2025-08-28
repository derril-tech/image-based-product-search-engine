# Audit Logging Service
# Created automatically by Cursor AI (2024-12-19)

import os
import logging
import json
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timezone, timedelta
import asyncio
from contextlib import asynccontextmanager
import hashlib
import uuid

logger = logging.getLogger(__name__)

class AuditEventType(Enum):
    """Types of audit events"""
    # Authentication events
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    
    # User management
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    ROLE_CHANGED = "role_changed"
    
    # Data access
    DATA_VIEWED = "data_viewed"
    DATA_CREATED = "data_created"
    DATA_UPDATED = "data_updated"
    DATA_DELETED = "data_deleted"
    DATA_EXPORTED = "data_exported"
    
    # File operations
    FILE_UPLOADED = "file_uploaded"
    FILE_DOWNLOADED = "file_downloaded"
    FILE_DELETED = "file_deleted"
    FILE_SCANNED = "file_scanned"
    
    # Search operations
    SEARCH_PERFORMED = "search_performed"
    SEARCH_RESULTS_VIEWED = "search_results_viewed"
    
    # System events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    CONFIGURATION_CHANGED = "configuration_changed"
    BACKUP_CREATED = "backup_created"
    RESTORE_PERFORMED = "restore_performed"
    
    # Security events
    SECURITY_SCAN = "security_scan"
    SECURITY_VIOLATION = "security_violation"
    ACCESS_DENIED = "access_denied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    
    # API events
    API_CALL = "api_call"
    API_ERROR = "api_error"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

class AuditSeverity(Enum):
    """Severity levels for audit events"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AuditEvent:
    """Audit event data structure"""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource_type: Optional[str]
    resource_id: Optional[str]
    action: str
    details: Dict[str, Any]
    severity: AuditSeverity
    success: bool
    error_message: Optional[str]
    duration_ms: Optional[int]
    metadata: Dict[str, Any]

class AuditLogger:
    """Audit logging service"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.log_level = config.get('log_level', 'INFO')
        self.retention_days = config.get('retention_days', 90)
        self.batch_size = config.get('batch_size', 100)
        self.flush_interval = config.get('flush_interval', 60)  # seconds
        
        # Storage backends
        self.file_enabled = config.get('file_enabled', True)
        self.database_enabled = config.get('database_enabled', True)
        self.elasticsearch_enabled = config.get('elasticsearch_enabled', False)
        
        # File logging
        self.log_file_path = config.get('log_file_path', 'logs/audit.log')
        self.file_logger = None
        if self.file_enabled:
            self._setup_file_logging()
        
        # Database connection
        self.db_connection = None
        if self.database_enabled:
            self._setup_database()
        
        # Elasticsearch connection
        self.es_client = None
        if self.elasticsearch_enabled:
            self._setup_elasticsearch()
        
        # Event queue for batching
        self.event_queue: List[AuditEvent] = []
        self.last_flush = time.time()
        
        # Start background flush task
        if self.enabled:
            asyncio.create_task(self._background_flush())
    
    def _setup_file_logging(self):
        """Setup file-based audit logging"""
        try:
            # Create log directory if it doesn't exist
            log_dir = os.path.dirname(self.log_file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Create file handler
            file_handler = logging.FileHandler(self.log_file_path)
            file_handler.setLevel(getattr(logging, self.log_level))
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            # Create logger
            self.file_logger = logging.getLogger('audit')
            self.file_logger.addHandler(file_handler)
            self.file_logger.setLevel(getattr(logging, self.log_level))
            
            logger.info(f"File audit logging enabled: {self.log_file_path}")
            
        except Exception as e:
            logger.error(f"Failed to setup file audit logging: {e}")
    
    def _setup_database(self):
        """Setup database audit logging"""
        try:
            # This would be implemented based on the database being used
            # For now, we'll just log that it's enabled
            logger.info("Database audit logging enabled")
            
        except Exception as e:
            logger.error(f"Failed to setup database audit logging: {e}")
    
    def _setup_elasticsearch(self):
        """Setup Elasticsearch audit logging"""
        try:
            # This would be implemented if Elasticsearch is configured
            # For now, we'll just log that it's enabled
            logger.info("Elasticsearch audit logging enabled")
            
        except Exception as e:
            logger.error(f"Failed to setup Elasticsearch audit logging: {e}")
    
    async def log_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: str = "",
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.MEDIUM,
        success: bool = True,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log an audit event"""
        if not self.enabled:
            return
        
        try:
            # Create audit event
            event = AuditEvent(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                timestamp=datetime.now(timezone.utc),
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                details=details or {},
                severity=severity,
                success=success,
                error_message=error_message,
                duration_ms=duration_ms,
                metadata=metadata or {}
            )
            
            # Add to queue
            self.event_queue.append(event)
            
            # Flush if queue is full
            if len(self.event_queue) >= self.batch_size:
                await self.flush()
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
    
    async def flush(self):
        """Flush queued events to storage"""
        if not self.event_queue:
            return
        
        try:
            events = self.event_queue.copy()
            self.event_queue.clear()
            self.last_flush = time.time()
            
            # Log to file
            if self.file_enabled and self.file_logger:
                for event in events:
                    self._log_to_file(event)
            
            # Log to database
            if self.database_enabled:
                await self._log_to_database(events)
            
            # Log to Elasticsearch
            if self.elasticsearch_enabled:
                await self._log_to_elasticsearch(events)
            
            logger.debug(f"Flushed {len(events)} audit events")
            
        except Exception as e:
            logger.error(f"Failed to flush audit events: {e}")
            # Put events back in queue
            self.event_queue.extend(events)
    
    def _log_to_file(self, event: AuditEvent):
        """Log event to file"""
        try:
            event_dict = asdict(event)
            event_dict['event_type'] = event.event_type.value
            event_dict['severity'] = event.severity.value
            event_dict['timestamp'] = event.timestamp.isoformat()
            
            log_message = json.dumps(event_dict)
            
            if self.file_logger:
                self.file_logger.info(log_message)
            
        except Exception as e:
            logger.error(f"Failed to log event to file: {e}")
    
    async def _log_to_database(self, events: List[AuditEvent]):
        """Log events to database"""
        try:
            # This would be implemented based on the database being used
            # For now, we'll just log that it's being done
            logger.debug(f"Logging {len(events)} events to database")
            
        except Exception as e:
            logger.error(f"Failed to log events to database: {e}")
    
    async def _log_to_elasticsearch(self, events: List[AuditEvent]):
        """Log events to Elasticsearch"""
        try:
            # This would be implemented if Elasticsearch is configured
            # For now, we'll just log that it's being done
            logger.debug(f"Logging {len(events)} events to Elasticsearch")
            
        except Exception as e:
            logger.error(f"Failed to log events to Elasticsearch: {e}")
    
    async def _background_flush(self):
        """Background task to flush events periodically"""
        while True:
            try:
                await asyncio.sleep(self.flush_interval)
                
                # Check if it's time to flush
                if time.time() - self.last_flush >= self.flush_interval:
                    await self.flush()
                    
            except Exception as e:
                logger.error(f"Background flush error: {e}")
    
    @asynccontextmanager
    async def audit_context(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: str = "",
        severity: AuditSeverity = AuditSeverity.MEDIUM
    ):
        """Context manager for auditing operations"""
        start_time = time.time()
        success = True
        error_message = None
        
        try:
            yield
        except Exception as e:
            success = False
            error_message = str(e)
            raise
        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            
            await self.log_event(
                event_type=event_type,
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                severity=severity,
                success=success,
                error_message=error_message,
                duration_ms=duration_ms
            )
    
    async def search_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        severity: Optional[AuditSeverity] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditEvent]:
        """Search audit events"""
        try:
            # This would be implemented based on the storage backend
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Failed to search audit events: {e}")
            return []
    
    async def get_event_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get audit event statistics"""
        try:
            # This would be implemented based on the storage backend
            # For now, return empty statistics
            return {
                'total_events': 0,
                'events_by_type': {},
                'events_by_severity': {},
                'events_by_user': {},
                'success_rate': 0.0,
                'average_duration_ms': 0.0
            }
            
        except Exception as e:
            logger.error(f"Failed to get audit statistics: {e}")
            return {}
    
    async def cleanup_old_events(self):
        """Clean up old audit events based on retention policy"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
            
            # This would be implemented based on the storage backend
            # For now, just log that it's being done
            logger.info(f"Cleaning up audit events older than {cutoff_date}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old audit events: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get audit logger status"""
        return {
            'enabled': self.enabled,
            'file_enabled': self.file_enabled,
            'database_enabled': self.database_enabled,
            'elasticsearch_enabled': self.elasticsearch_enabled,
            'queue_size': len(self.event_queue),
            'last_flush': self.last_flush,
            'config': {
                'log_level': self.log_level,
                'retention_days': self.retention_days,
                'batch_size': self.batch_size,
                'flush_interval': self.flush_interval
            }
        }

# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None

def init_audit_logger(config: Dict[str, Any]) -> AuditLogger:
    """Initialize audit logger globally"""
    global _audit_logger
    
    if _audit_logger is None:
        _audit_logger = AuditLogger(config)
    
    return _audit_logger

def get_audit_logger() -> Optional[AuditLogger]:
    """Get the global audit logger"""
    return _audit_logger

# Utility functions for easy access
async def log_audit_event(
    event_type: AuditEventType,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    action: str = "",
    details: Optional[Dict[str, Any]] = None,
    severity: AuditSeverity = AuditSeverity.MEDIUM,
    success: bool = True,
    error_message: Optional[str] = None,
    duration_ms: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """Log an audit event using the global audit logger"""
    audit_logger = get_audit_logger()
    if audit_logger:
        await audit_logger.log_event(
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            details=details,
            severity=severity,
            success=success,
            error_message=error_message,
            duration_ms=duration_ms,
            metadata=metadata
        )
