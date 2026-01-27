/**
 * Better Auth API route handler.
 * This handles all Better Auth endpoints including JWKS.
 * Note: We're using custom JWT authentication for the app,
 * but Better Auth is kept for potential future use.
 */

import { auth } from "@/lib/auth";

export const { GET, POST } = auth.handler;
