import { z } from 'zod';

// Base API Response
export const ApiResponseSchema = z.object({
    success: z.boolean(),
    data: z.unknown().optional(),
    error: z.string().optional(),
    message: z.string().optional(),
});

export type ApiResponse<T = unknown> = {
    success: boolean;
    data?: T;
    error?: string;
    message?: string;
};

// Pagination
export const PaginationSchema = z.object({
    page: z.number().min(1).default(1),
    limit: z.number().min(1).max(100).default(20),
    total: z.number().optional(),
    hasNext: z.boolean().optional(),
    hasPrev: z.boolean().optional(),
});

export type Pagination = z.infer<typeof PaginationSchema>;

// Error Response
export const ErrorResponseSchema = z.object({
    type: z.string(),
    title: z.string(),
    status: z.number(),
    detail: z.string().optional(),
    instance: z.string().optional(),
});

export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;
