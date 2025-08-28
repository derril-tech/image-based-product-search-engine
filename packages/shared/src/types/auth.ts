import { z } from 'zod';

// User
export const UserSchema = z.object({
    id: z.string().uuid(),
    email: z.string().email(),
    firstName: z.string().optional(),
    lastName: z.string().optional(),
    role: z.enum(['admin', 'user']).default('user'),
    createdAt: z.string().datetime(),
    updatedAt: z.string().datetime(),
});

export type User = z.infer<typeof UserSchema>;

// Organization
export const OrganizationSchema = z.object({
    id: z.string().uuid(),
    name: z.string(),
    slug: z.string(),
    plan: z.enum(['free', 'pro', 'enterprise']).default('free'),
    createdAt: z.string().datetime(),
    updatedAt: z.string().datetime(),
});

export type Organization = z.infer<typeof OrganizationSchema>;

// Auth Requests
export const LoginRequestSchema = z.object({
    email: z.string().email(),
    password: z.string().min(8),
});

export const RegisterRequestSchema = z.object({
    email: z.string().email(),
    password: z.string().min(8),
    firstName: z.string().optional(),
    lastName: z.string().optional(),
    organizationName: z.string().optional(),
});

export const RefreshTokenRequestSchema = z.object({
    refreshToken: z.string(),
});

// Auth Responses
export const AuthResponseSchema = z.object({
    accessToken: z.string(),
    refreshToken: z.string(),
    user: UserSchema,
    organization: OrganizationSchema.optional(),
});

export type LoginRequest = z.infer<typeof LoginRequestSchema>;
export type RegisterRequest = z.infer<typeof RegisterRequestSchema>;
export type RefreshTokenRequest = z.infer<typeof RefreshTokenRequestSchema>;
export type AuthResponse = z.infer<typeof AuthResponseSchema>;
