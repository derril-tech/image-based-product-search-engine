import { z } from 'zod';

// File validation
export const validateImageFile = (file: File): string | null => {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];

    if (file.size > maxSize) {
        return 'File size must be less than 10MB';
    }

    if (!allowedTypes.includes(file.type)) {
        return 'File must be a JPEG, PNG, or WebP image';
    }

    return null;
};

// URL validation
export const isValidUrl = (url: string): boolean => {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
};

// Email validation
export const isValidEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

// UUID validation
export const isValidUuid = (uuid: string): boolean => {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    return uuidRegex.test(uuid);
};

// Base64 image validation
export const isValidBase64Image = (data: string): boolean => {
    const base64Regex = /^data:image\/(jpeg|png|webp);base64,/;
    return base64Regex.test(data);
};

// Search query validation
export const SearchQueryValidationSchema = z.object({
    query: z.string().optional(),
    imageUrl: z.string().url().optional(),
    imageData: z.string().optional(),
    filters: z.object({
        category: z.array(z.string()).optional(),
        brand: z.array(z.string()).optional(),
        priceMin: z.number().min(0).optional(),
        priceMax: z.number().min(0).optional(),
        tags: z.array(z.string()).optional(),
    }).optional(),
    limit: z.number().min(1).max(100).default(20),
    offset: z.number().min(0).default(0),
    sortBy: z.enum(['relevance', 'price_asc', 'price_desc', 'newest']).default('relevance'),
}).refine(
    (data) => data.query || data.imageUrl || data.imageData,
    {
        message: 'At least one of query, imageUrl, or imageData must be provided',
        path: ['query'],
    }
);
