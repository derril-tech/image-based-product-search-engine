import { z } from 'zod';

// Product
export const ProductSchema = z.object({
    id: z.string().uuid(),
    organizationId: z.string().uuid(),
    externalId: z.string().optional(),
    name: z.string(),
    description: z.string().optional(),
    brand: z.string().optional(),
    category: z.string().optional(),
    tags: z.array(z.string()).default([]),
    metadata: z.record(z.unknown()).default({}),
    createdAt: z.string().datetime(),
    updatedAt: z.string().datetime(),
});

export type Product = z.infer<typeof ProductSchema>;

// Product Variant
export const ProductVariantSchema = z.object({
    id: z.string().uuid(),
    productId: z.string().uuid(),
    sku: z.string().optional(),
    name: z.string().optional(),
    price: z.number().positive().optional(),
    currency: z.string().default('USD'),
    attributes: z.record(z.unknown()).default({}),
    createdAt: z.string().datetime(),
    updatedAt: z.string().datetime(),
});

export type ProductVariant = z.infer<typeof ProductVariantSchema>;

// Image
export const ImageSchema = z.object({
    id: z.string().uuid(),
    productId: z.string().uuid().optional(),
    variantId: z.string().uuid().optional(),
    organizationId: z.string().uuid(),
    url: z.string().url(),
    filename: z.string(),
    mimeType: z.string(),
    size: z.number().positive(),
    width: z.number().positive().optional(),
    height: z.number().positive().optional(),
    altText: z.string().optional(),
    isPrimary: z.boolean().default(false),
    createdAt: z.string().datetime(),
    updatedAt: z.string().datetime(),
});

export type Image = z.infer<typeof ImageSchema>;

// Embedding
export const EmbeddingSchema = z.object({
    id: z.string().uuid(),
    imageId: z.string().uuid(),
    organizationId: z.string().uuid(),
    model: z.string(),
    vector: z.array(z.number()),
    dimension: z.number().positive(),
    metadata: z.record(z.unknown()).default({}),
    createdAt: z.string().datetime(),
});

export type Embedding = z.infer<typeof EmbeddingSchema>;

// Region (for object detection)
export const RegionSchema = z.object({
    id: z.string().uuid(),
    imageId: z.string().uuid(),
    x: z.number().min(0),
    y: z.number().min(0),
    width: z.number().positive(),
    height: z.number().positive(),
    confidence: z.number().min(0).max(1),
    label: z.string().optional(),
    metadata: z.record(z.unknown()).default({}),
    createdAt: z.string().datetime(),
});

export type Region = z.infer<typeof RegionSchema>;

// Catalog Import
export const CatalogImportSchema = z.object({
    id: z.string().uuid(),
    organizationId: z.string().uuid(),
    type: z.enum(['shopify', 'bigcommerce', 'woocommerce', 'csv']),
    status: z.enum(['pending', 'processing', 'completed', 'failed']),
    config: z.record(z.unknown()),
    stats: z.object({
        total: z.number().default(0),
        processed: z.number().default(0),
        failed: z.number().default(0),
    }).default({}),
    error: z.string().optional(),
    createdAt: z.string().datetime(),
    updatedAt: z.string().datetime(),
});

export type CatalogImport = z.infer<typeof CatalogImportSchema>;
