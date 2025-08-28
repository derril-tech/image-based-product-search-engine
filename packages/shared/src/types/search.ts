import { z } from 'zod';

// Search Query
export const SearchQuerySchema = z.object({
    query: z.string().optional(),
    imageUrl: z.string().url().optional(),
    imageData: z.string().optional(), // base64 encoded image
    filters: z.object({
        category: z.array(z.string()).optional(),
        brand: z.array(z.string()).optional(),
        priceMin: z.number().optional(),
        priceMax: z.number().optional(),
        tags: z.array(z.string()).optional(),
    }).optional(),
    limit: z.number().min(1).max(100).default(20),
    offset: z.number().min(0).default(0),
    sortBy: z.enum(['relevance', 'price_asc', 'price_desc', 'newest']).default('relevance'),
});

export type SearchQuery = z.infer<typeof SearchQuerySchema>;

// Search Result
export const SearchResultSchema = z.object({
    id: z.string().uuid(),
    productId: z.string().uuid(),
    imageId: z.string().uuid(),
    score: z.number().min(0).max(1),
    product: z.object({
        id: z.string().uuid(),
        name: z.string(),
        description: z.string().optional(),
        brand: z.string().optional(),
        category: z.string().optional(),
        tags: z.array(z.string()),
    }),
    image: z.object({
        id: z.string().uuid(),
        url: z.string().url(),
        altText: z.string().optional(),
        width: z.number().positive().optional(),
        height: z.number().positive().optional(),
    }),
    variant: z.object({
        id: z.string().uuid(),
        sku: z.string().optional(),
        name: z.string().optional(),
        price: z.number().positive().optional(),
        currency: z.string(),
    }).optional(),
    regions: z.array(z.object({
        id: z.string().uuid(),
        x: z.number(),
        y: z.number(),
        width: z.number(),
        height: z.number(),
        confidence: z.number(),
        label: z.string().optional(),
    })).optional(),
});

export type SearchResult = z.infer<typeof SearchResultSchema>;

// Search Response
export const SearchResponseSchema = z.object({
    query: SearchQuerySchema,
    results: z.array(SearchResultSchema),
    total: z.number(),
    pagination: z.object({
        page: z.number(),
        limit: z.number(),
        total: z.number(),
        hasNext: z.boolean(),
        hasPrev: z.boolean(),
    }),
    metadata: z.object({
        searchTime: z.number(),
        model: z.string(),
        filters: z.record(z.unknown()),
    }),
});

export type SearchResponse = z.infer<typeof SearchResponseSchema>;

// Search Session
export const SearchSessionSchema = z.object({
    id: z.string().uuid(),
    organizationId: z.string().uuid(),
    userId: z.string().uuid().optional(),
    query: SearchQuerySchema,
    results: z.array(SearchResultSchema),
    metadata: z.record(z.unknown()).default({}),
    createdAt: z.string().datetime(),
});

export type SearchSession = z.infer<typeof SearchSessionSchema>;

// Search Feedback
export const SearchFeedbackSchema = z.object({
    id: z.string().uuid(),
    sessionId: z.string().uuid(),
    resultId: z.string().uuid(),
    type: z.enum(['click', 'purchase', 'like', 'dislike']),
    metadata: z.record(z.unknown()).default({}),
    createdAt: z.string().datetime(),
});

export type SearchFeedback = z.infer<typeof SearchFeedbackSchema>;
