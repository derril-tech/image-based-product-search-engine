# Dependencies for Worker Services
# Created automatically by Cursor AI (2024-12-19)

import os
from typing import Optional
from .config import get_settings
from .services.cdn_service import CDNService
from .services.thumbnailing_pipeline import ThumbnailingPipeline
from .services.security_scanner import SecurityScanner, SecurityPolicy
from .services.audit_logger import AuditLogger
from .services.advanced_search import AdvancedSearchService
from .services.billing_service import BillingService

# Global service instances
_cdn_service: Optional[CDNService] = None
_thumbnailing_pipeline: Optional[ThumbnailingPipeline] = None
_security_scanner: Optional[SecurityScanner] = None
_security_policy: Optional[SecurityPolicy] = None
_audit_logger: Optional[AuditLogger] = None
_advanced_search_service: Optional[AdvancedSearchService] = None
_billing_service: Optional[BillingService] = None

def get_cdn_service() -> CDNService:
    """Get CDN service instance"""
    global _cdn_service
    
    if _cdn_service is None:
        settings = get_settings()
        
        cdn_config = {
            'aws_access_key_id': settings.aws_access_key_id,
            'aws_secret_access_key': settings.aws_secret_access_key,
            'aws_region': settings.aws_region,
            's3_bucket_name': settings.s3_bucket_name,
            'cdn_domain': settings.cdn_domain,
            'cloudfront_distribution_id': settings.cloudfront_distribution_id,
            'jpeg_quality': settings.jpeg_quality,
            'png_optimize': settings.png_optimize
        }
        
        _cdn_service = CDNService(cdn_config)
    
    return _cdn_service

def get_thumbnailing_pipeline() -> ThumbnailingPipeline:
    """Get thumbnailing pipeline instance"""
    global _thumbnailing_pipeline
    
    if _thumbnailing_pipeline is None:
        settings = get_settings()
        cdn_service = get_cdn_service()
        
        pipeline_config = {
            'max_workers': settings.thumbnailing_max_workers,
            'enable_enhancement': settings.enable_image_enhancement,
            'enable_watermark': settings.enable_watermark,
            'watermark_path': settings.watermark_path,
            'enhancement_settings': {
                'sharpness': settings.image_sharpness,
                'contrast': settings.image_contrast,
                'brightness': settings.image_brightness,
                'saturation': settings.image_saturation
            }
        }
        
        _thumbnailing_pipeline = ThumbnailingPipeline(cdn_service, pipeline_config)
    
    return _thumbnailing_pipeline

def get_security_scanner() -> SecurityScanner:
    """Get security scanner instance"""
    global _security_scanner
    
    if _security_scanner is None:
        settings = get_settings()
        
        scanner_config = {
            'enable_nsfw_detection': settings.enable_nsfw_detection,
            'enable_virus_scanning': settings.enable_virus_scanning,
            'nsfw_threshold': settings.nsfw_threshold,
            'max_file_size': settings.max_file_size,
            'allowed_mime_types': settings.allowed_mime_types
        }
        
        _security_scanner = SecurityScanner(scanner_config)
    
    return _security_scanner

def get_security_policy() -> SecurityPolicy:
    """Get security policy instance"""
    global _security_policy
    
    if _security_policy is None:
        settings = get_settings()
        
        policy_config = {
            'block_nsfw': settings.block_nsfw,
            'block_virus': settings.block_virus,
            'quarantine_suspicious': settings.quarantine_suspicious,
            'allow_list': settings.security_allow_list,
            'block_list': settings.security_block_list
        }
        
        _security_policy = SecurityPolicy(policy_config)
    
    return _security_policy

def get_audit_logger() -> AuditLogger:
    """Get audit logger instance"""
    global _audit_logger
    
    if _audit_logger is None:
        settings = get_settings()
        
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
        
        _audit_logger = AuditLogger(audit_config)
    
    return _audit_logger

def get_billing_service() -> BillingService:
    """Get billing service instance"""
    global _billing_service
    
    if _billing_service is None:
        _billing_service = BillingService()
    
    return _billing_service
def get_advanced_search_service() -> AdvancedSearchService:
    """Get advanced search service instance"""
    global _advanced_search_service
    
    if _advanced_search_service is None:
        _advanced_search_service = AdvancedSearchService()
    
    return _advanced_search_service
