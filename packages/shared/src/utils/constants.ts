// API Constants
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
export const API_VERSION = 'v1';
export const API_PREFIX = `/api/${API_VERSION}`;

// File Upload
export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
export const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
export const MAX_IMAGE_DIMENSION = 2048;

// Search
export const DEFAULT_SEARCH_LIMIT = 20;
export const MAX_SEARCH_LIMIT = 100;
export const SEARCH_TIMEOUT = 30000; // 30 seconds

// Pagination
export const DEFAULT_PAGE_SIZE = 20;
export const MAX_PAGE_SIZE = 100;

// Cache
export const CACHE_TTL = 300; // 5 minutes
export const SEARCH_CACHE_TTL = 600; // 10 minutes

// Models
export const CLIP_MODEL = 'openai/clip-vit-base-patch32';
export const YOLO_MODEL = 'yolov8n.pt';
export const VECTOR_DIMENSION = 512;

// Status Codes
export const STATUS_PENDING = 'pending';
export const STATUS_PROCESSING = 'processing';
export const STATUS_COMPLETED = 'completed';
export const STATUS_FAILED = 'failed';

// User Roles
export const ROLE_ADMIN = 'admin';
export const ROLE_USER = 'user';

// Organization Plans
export const PLAN_FREE = 'free';
export const PLAN_PRO = 'pro';
export const PLAN_ENTERPRISE = 'enterprise';
