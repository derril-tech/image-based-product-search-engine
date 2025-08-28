# Sentry integration for error tracking
# Created automatically by Cursor AI (2024-12-19)

import os
import logging
from typing import Optional, Dict, Any
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration

logger = logging.getLogger(__name__)

class SentryManager:
    """Manages Sentry error tracking and monitoring"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dsn = config.get('sentry_dsn')
        self.environment = config.get('environment', 'development')
        self.service_name = config.get('service_name', 'image-search-workers')
        self.service_version = config.get('service_version', '0.1.0')
        self.traces_sample_rate = config.get('traces_sample_rate', 0.1)
        self.profiles_sample_rate = config.get('profiles_sample_rate', 0.1)
        
        # Initialize Sentry if DSN is provided
        if self.dsn:
            self._init_sentry()
        else:
            logger.warning("Sentry DSN not provided, error tracking disabled")
    
    def _init_sentry(self):
        """Initialize Sentry SDK"""
        try:
            sentry_sdk.init(
                dsn=self.dsn,
                environment=self.environment,
                service_name=self.service_name,
                service_version=self.service_version,
                traces_sample_rate=self.traces_sample_rate,
                profiles_sample_rate=self.profiles_sample_rate,
                
                # Integrations
                integrations=[
                    FastApiIntegration(),
                    RedisIntegration(),
                    SqlalchemyIntegration(),
                    HttpxIntegration(),
                    ThreadingIntegration(),
                    AsyncioIntegration(),
                ],
                
                # Additional configuration
                send_default_pii=False,  # Don't send personal data
                before_send=self._before_send,
                before_breadcrumb=self._before_breadcrumb,
                
                # Performance monitoring
                enable_tracing=True,
                
                # Debug mode for development
                debug=self.environment == 'development'
            )
            
            logger.info(f"Sentry initialized for environment: {self.environment}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {e}")
    
    def _before_send(self, event, hint):
        """Filter events before sending to Sentry"""
        try:
            # Filter out certain error types
            if 'exception' in hint:
                exc_type = type(hint['exception']).__name__
                
                # Ignore certain exceptions
                ignored_exceptions = [
                    'ConnectionError',
                    'TimeoutError',
                    'KeyboardInterrupt'
                ]
                
                if exc_type in ignored_exceptions:
                    return None
            
            # Add custom context
            event.setdefault('tags', {}).update({
                'service': self.service_name,
                'version': self.service_version
            })
            
            return event
            
        except Exception as e:
            logger.error(f"Error in before_send: {e}")
            return event
    
    def _before_breadcrumb(self, breadcrumb, hint):
        """Filter breadcrumbs before sending to Sentry"""
        try:
            # Filter out certain breadcrumb types
            if breadcrumb.get('category') in ['http', 'db']:
                # Only include error-level breadcrumbs for these categories
                if breadcrumb.get('level') != 'error':
                    return None
            
            return breadcrumb
            
        except Exception as e:
            logger.error(f"Error in before_breadcrumb: {e}")
            return breadcrumb
    
    def capture_exception(self, exception: Exception, context: Optional[Dict[str, Any]] = None):
        """Capture an exception with additional context"""
        if not self.dsn:
            return
        
        try:
            with sentry_sdk.push_scope() as scope:
                if context:
                    scope.set_context("custom", context)
                
                sentry_sdk.capture_exception(exception)
                
        except Exception as e:
            logger.error(f"Failed to capture exception: {e}")
    
    def capture_message(self, message: str, level: str = 'info', context: Optional[Dict[str, Any]] = None):
        """Capture a message with specified level"""
        if not self.dsn:
            return
        
        try:
            with sentry_sdk.push_scope() as scope:
                if context:
                    scope.set_context("custom", context)
                
                sentry_sdk.capture_message(message, level=level)
                
        except Exception as e:
            logger.error(f"Failed to capture message: {e}")
    
    def set_user(self, user_id: str, email: Optional[str] = None, username: Optional[str] = None):
        """Set user context for error tracking"""
        if not self.dsn:
            return
        
        try:
            sentry_sdk.set_user({
                "id": user_id,
                "email": email,
                "username": username
            })
            
        except Exception as e:
            logger.error(f"Failed to set user: {e}")
    
    def set_tag(self, key: str, value: str):
        """Set a tag for error tracking"""
        if not self.dsn:
            return
        
        try:
            sentry_sdk.set_tag(key, value)
            
        except Exception as e:
            logger.error(f"Failed to set tag: {e}")
    
    def set_context(self, name: str, data: Dict[str, Any]):
        """Set context data for error tracking"""
        if not self.dsn:
            return
        
        try:
            sentry_sdk.set_context(name, data)
            
        except Exception as e:
            logger.error(f"Failed to set context: {e}")
    
    def add_breadcrumb(self, message: str, category: str = 'info', level: str = 'info', data: Optional[Dict[str, Any]] = None):
        """Add a breadcrumb for debugging"""
        if not self.dsn:
            return
        
        try:
            sentry_sdk.add_breadcrumb(
                message=message,
                category=category,
                level=level,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Failed to add breadcrumb: {e}")
    
    def start_transaction(self, name: str, operation: str = 'http.request'):
        """Start a performance transaction"""
        if not self.dsn:
            return None
        
        try:
            return sentry_sdk.start_transaction(
                name=name,
                op=operation
            )
            
        except Exception as e:
            logger.error(f"Failed to start transaction: {e}")
            return None
    
    def set_extra(self, key: str, value: Any):
        """Set extra data for error tracking"""
        if not self.dsn:
            return
        
        try:
            sentry_sdk.set_extra(key, value)
            
        except Exception as e:
            logger.error(f"Failed to set extra: {e}")
    
    def flush(self, timeout: float = 2.0):
        """Flush pending events to Sentry"""
        if not self.dsn:
            return
        
        try:
            sentry_sdk.flush(timeout=timeout)
            
        except Exception as e:
            logger.error(f"Failed to flush Sentry: {e}")
    
    def close(self):
        """Close Sentry SDK"""
        if not self.dsn:
            return
        
        try:
            sentry_sdk.close()
            logger.info("Sentry closed")
            
        except Exception as e:
            logger.error(f"Failed to close Sentry: {e}")

# Global Sentry manager instance
_sentry_manager: Optional[SentryManager] = None

def init_sentry(config: Dict[str, Any]) -> SentryManager:
    """Initialize Sentry globally"""
    global _sentry_manager
    
    if _sentry_manager is None:
        _sentry_manager = SentryManager(config)
    
    return _sentry_manager

def get_sentry() -> Optional[SentryManager]:
    """Get the global Sentry manager"""
    return _sentry_manager

# Utility functions for easy access
def capture_exception(exception: Exception, context: Optional[Dict[str, Any]] = None):
    """Capture an exception with Sentry"""
    sentry = get_sentry()
    if sentry:
        sentry.capture_exception(exception, context)

def capture_message(message: str, level: str = 'info', context: Optional[Dict[str, Any]] = None):
    """Capture a message with Sentry"""
    sentry = get_sentry()
    if sentry:
        sentry.capture_message(message, level, context)

def set_user(user_id: str, email: Optional[str] = None, username: Optional[str] = None):
    """Set user context in Sentry"""
    sentry = get_sentry()
    if sentry:
        sentry.set_user(user_id, email, username)

def set_tag(key: str, value: str):
    """Set a tag in Sentry"""
    sentry = get_sentry()
    if sentry:
        sentry.set_tag(key, value)

def set_context(name: str, data: Dict[str, Any]):
    """Set context data in Sentry"""
    sentry = get_sentry()
    if sentry:
        sentry.set_context(name, data)

def add_breadcrumb(message: str, category: str = 'info', level: str = 'info', data: Optional[Dict[str, Any]] = None):
    """Add a breadcrumb in Sentry"""
    sentry = get_sentry()
    if sentry:
        sentry.add_breadcrumb(message, category, level, data)
