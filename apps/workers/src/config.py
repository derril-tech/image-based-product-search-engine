"""Configuration settings for image search workers."""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/image_search"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Milvus
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    
    # NATS
    NATS_URL: str = "nats://localhost:4222"
    
    # S3/Storage
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "image-search"
    
    # AWS/CDN Configuration
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "image-search-cdn"
    CDN_DOMAIN: str = ""
    CLOUDFRONT_DISTRIBUTION_ID: str = ""
    
    # Image Processing
    JPEG_QUALITY: int = 85
    PNG_OPTIMIZE: bool = True
    THUMBNAILING_MAX_WORKERS: int = 4
    ENABLE_IMAGE_ENHANCEMENT: bool = True
    ENABLE_WATERMARK: bool = False
    WATERMARK_PATH: str = ""
    
    # Image Enhancement Settings
    IMAGE_SHARPNESS: float = 1.2
    IMAGE_CONTRAST: float = 1.1
    IMAGE_BRIGHTNESS: float = 1.05
    IMAGE_SATURATION: float = 1.1
    
    # Observability Configuration
    OTLP_ENDPOINT: str = ""
    OTLP_HEADERS: str = ""
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.1
    ENABLE_TELEMETRY: bool = True
    ENABLE_PROMETHEUS: bool = True
    ENABLE_SENTRY: bool = True
    
    # Security Configuration
    ENABLE_NSFW_DETECTION: bool = True
    ENABLE_VIRUS_SCANNING: bool = True
    NSFW_THRESHOLD: float = 0.6
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_MIME_TYPES: str = "image/jpeg,image/png,image/gif,image/webp,image/bmp,image/tiff"
    BLOCK_NSFW: bool = True
    BLOCK_VIRUS: bool = True
    QUARANTINE_SUSPICIOUS: bool = True
    SECURITY_ALLOW_LIST: str = ""
    SECURITY_BLOCK_LIST: str = ""
    
    # Audit Logging Configuration
    ENABLE_AUDIT_LOGGING: bool = True
    AUDIT_LOG_LEVEL: str = "INFO"
    AUDIT_RETENTION_DAYS: int = 90
    AUDIT_BATCH_SIZE: int = 100
    AUDIT_FLUSH_INTERVAL: int = 60
    AUDIT_FILE_ENABLED: bool = True
    AUDIT_DATABASE_ENABLED: bool = True
    AUDIT_ELASTICSEARCH_ENABLED: bool = False
    AUDIT_LOG_FILE_PATH: str = "logs/audit.log"
    
    # Billing Configuration
    ENABLE_BILLING: bool = True
    BILLING_SNS_TOPIC_ARN: str = ""
    ENVIRONMENT: str = "development"
    
    # AI Models
    CLIP_MODEL: str = "openai/clip-vit-base-patch32"
    YOLO_MODEL: str = "yolov8n.pt"
    
    # Processing
    MAX_IMAGE_SIZE: int = 1024
    BATCH_SIZE: int = 32
    VECTOR_DIMENSION: int = 512
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def aws_access_key_id(self) -> str:
        return self.AWS_ACCESS_KEY_ID or self.S3_ACCESS_KEY
    
    @property
    def aws_secret_access_key(self) -> str:
        return self.AWS_SECRET_ACCESS_KEY or self.S3_SECRET_KEY
    
    @property
    def aws_region(self) -> str:
        return self.AWS_REGION
    
    @property
    def s3_bucket_name(self) -> str:
        return self.S3_BUCKET_NAME or self.S3_BUCKET
    
    @property
    def cdn_domain(self) -> str:
        return self.CDN_DOMAIN
    
    @property
    def cloudfront_distribution_id(self) -> str:
        return self.CLOUDFRONT_DISTRIBUTION_ID
    
    @property
    def jpeg_quality(self) -> int:
        return self.JPEG_QUALITY
    
    @property
    def png_optimize(self) -> bool:
        return self.PNG_OPTIMIZE
    
    @property
    def thumbnailing_max_workers(self) -> int:
        return self.THUMBNAILING_MAX_WORKERS
    
    @property
    def enable_image_enhancement(self) -> bool:
        return self.ENABLE_IMAGE_ENHANCEMENT
    
    @property
    def enable_watermark(self) -> bool:
        return self.ENABLE_WATERMARK
    
    @property
    def watermark_path(self) -> str:
        return self.WATERMARK_PATH
    
    @property
    def image_sharpness(self) -> float:
        return self.IMAGE_SHARPNESS
    
    @property
    def image_contrast(self) -> float:
        return self.IMAGE_CONTRAST
    
    @property
    def image_brightness(self) -> float:
        return self.IMAGE_BRIGHTNESS
    
    @property
    def image_saturation(self) -> float:
        return self.IMAGE_SATURATION
    
    @property
    def otlp_endpoint(self) -> str:
        return self.OTLP_ENDPOINT
    
    @property
    def otlp_headers(self) -> Dict[str, str]:
        if not self.OTLP_HEADERS:
            return {}
        try:
            import json
            return json.loads(self.OTLP_HEADERS)
        except:
            return {}
    
    @property
    def sentry_dsn(self) -> str:
        return self.SENTRY_DSN
    
    @property
    def sentry_environment(self) -> str:
        return self.SENTRY_ENVIRONMENT
    
    @property
    def sentry_traces_sample_rate(self) -> float:
        return self.SENTRY_TRACES_SAMPLE_RATE
    
    @property
    def sentry_profiles_sample_rate(self) -> float:
        return self.SENTRY_PROFILES_SAMPLE_RATE
    
    @property
    def enable_telemetry(self) -> bool:
        return self.ENABLE_TELEMETRY
    
    @property
    def enable_prometheus(self) -> bool:
        return self.ENABLE_PROMETHEUS
    
    @property
    def enable_sentry(self) -> bool:
        return self.ENABLE_SENTRY
    
    @property
    def enable_nsfw_detection(self) -> bool:
        return self.ENABLE_NSFW_DETECTION
    
    @property
    def enable_virus_scanning(self) -> bool:
        return self.ENABLE_VIRUS_SCANNING
    
    @property
    def nsfw_threshold(self) -> float:
        return self.NSFW_THRESHOLD
    
    @property
    def max_file_size(self) -> int:
        return self.MAX_FILE_SIZE
    
    @property
    def allowed_mime_types(self) -> List[str]:
        return [t.strip() for t in self.ALLOWED_MIME_TYPES.split(',') if t.strip()]
    
    @property
    def block_nsfw(self) -> bool:
        return self.BLOCK_NSFW
    
    @property
    def block_virus(self) -> bool:
        return self.BLOCK_VIRUS
    
    @property
    def quarantine_suspicious(self) -> bool:
        return self.QUARANTINE_SUSPICIOUS
    
    @property
    def security_allow_list(self) -> List[str]:
        return [h.strip() for h in self.SECURITY_ALLOW_LIST.split(',') if h.strip()]
    
    @property
    def security_block_list(self) -> List[str]:
        return [h.strip() for h in self.SECURITY_BLOCK_LIST.split(',') if h.strip()]
    
    @property
    def enable_audit_logging(self) -> bool:
        return self.ENABLE_AUDIT_LOGGING
    
    @property
    def audit_log_level(self) -> str:
        return self.AUDIT_LOG_LEVEL
    
    @property
    def audit_retention_days(self) -> int:
        return self.AUDIT_RETENTION_DAYS
    
    @property
    def audit_batch_size(self) -> int:
        return self.AUDIT_BATCH_SIZE
    
    @property
    def audit_flush_interval(self) -> int:
        return self.AUDIT_FLUSH_INTERVAL
    
    @property
    def audit_file_enabled(self) -> bool:
        return self.AUDIT_FILE_ENABLED
    
    @property
    def audit_database_enabled(self) -> bool:
        return self.AUDIT_DATABASE_ENABLED
    
    @property
    def audit_elasticsearch_enabled(self) -> bool:
        return self.AUDIT_ELASTICSEARCH_ENABLED
    
    @property
    def audit_log_file_path(self) -> str:
        return self.AUDIT_LOG_FILE_PATH


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


settings = get_settings()
