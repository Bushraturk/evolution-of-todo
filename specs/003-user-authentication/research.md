# Research: User Authentication & Multi-User Support

**Feature**: 003-user-authentication
**Date**: 2025-12-28

## Research Questions Resolved

### 1. Better Auth + Next.js Integration

**Decision**: Use Better Auth with JWT plugin for Next.js 14 App Router

**Rationale**:
- Better Auth provides native Next.js integration via `toNextJsHandler`
- JWT plugin enables token-based authentication for external API verification
- JWKS endpoint allows stateless JWT verification without database calls
- Active development and modern TypeScript support

**Alternatives Considered**:
- **NextAuth.js/Auth.js**: More mature but merging with Better Auth ecosystem
- **Custom JWT implementation**: More control but significant development overhead
- **Auth0/Clerk**: SaaS solutions with vendor lock-in and cost considerations

**Implementation**:
```typescript
// lib/auth.ts (server)
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"

export const auth = betterAuth({
  plugins: [jwt()]
})

// lib/auth-client.ts (client)
import { createAuthClient } from "better-auth/client"
import { jwtClient } from "better-auth/client/plugins"

export const authClient = createAuthClient({
  plugins: [jwtClient()]
})
```

**Source**: [Better Auth JWT Plugin](https://www.better-auth.com/docs/plugins/jwt)

---

### 2. FastAPI JWT Verification

**Decision**: Use `jose` library (Python) with JWKS endpoint for JWT verification

**Rationale**:
- JWKS verification allows stateless authentication
- No shared secret needed between frontend and backend
- Public key can be cached for performance
- Standard approach compatible with any JWT issuer

**Alternatives Considered**:
- **python-jose with shared secret**: Requires secret synchronization, less secure
- **PyJWT**: Similar functionality, jose has better JWKS support
- **Database session lookup**: Adds latency and database dependency per request

**Implementation**:
```python
# backend/src/auth/jwt_verifier.py
from jose import jwt, JWTError
import httpx

JWKS_URL = "http://localhost:3000/api/auth/jwks"
ISSUER = "http://localhost:3000"

async def verify_jwt(token: str) -> dict:
    # Fetch JWKS (cache in production)
    async with httpx.AsyncClient() as client:
        response = await client.get(JWKS_URL)
        jwks = response.json()

    # Verify token
    payload = jwt.decode(
        token,
        jwks,
        algorithms=["EdDSA", "RS256"],
        issuer=ISSUER
    )
    return payload
```

**Source**: [FastAPI JWT Tutorial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

---

### 3. Token Flow Architecture

**Decision**: Frontend manages auth, Backend verifies JWT on each request

**Flow**:
```
1. User logs in on Frontend → Better Auth creates session + JWT
2. Frontend stores JWT token (via jwtClient plugin)
3. Frontend API calls include Authorization: Bearer <token>
4. FastAPI middleware extracts + verifies JWT via JWKS
5. User ID from JWT payload used to filter database queries
```

**Rationale**:
- Separation of concerns: Frontend handles auth UX, Backend validates
- Stateless backend: No session storage needed on API server
- Scalable: Any backend instance can verify tokens independently

---

### 4. Database Schema for Multi-User

**Decision**: Add `user_id` column to tasks table with foreign key constraint

**Rationale**:
- Simple one-to-many relationship (User → Tasks)
- Foreign key ensures referential integrity
- Index on user_id for query performance

**Migration Strategy**:
- Existing Phase 2 tasks will need user assignment
- Option 1: Assign to default "system" user
- Option 2: Delete existing tasks (recommended for clean start)

---

### 5. Better Auth Database Requirements

**Decision**: Better Auth manages its own tables (user, session, account, verification)

**Tables Created by Better Auth**:
- `user` - User profiles (id, email, name, emailVerified, image, createdAt, updatedAt)
- `session` - Active sessions (id, expiresAt, token, createdAt, updatedAt, userId)
- `account` - OAuth accounts (if using social login)
- `verification` - Email verification tokens

**Integration**:
- Our Task table references Better Auth's user.id
- No need to create separate user management
- Better Auth CLI handles migrations: `npx @better-auth/cli migrate`

---

### 6. Frontend Route Protection

**Decision**: Use Next.js middleware for route protection

**Rationale**:
- Intercepts requests before rendering
- Redirects unauthenticated users to login
- Server-side check prevents flash of protected content

**Implementation**:
```typescript
// middleware.ts
import { auth } from "@/lib/auth"
import { NextResponse } from "next/server"

export default auth((req) => {
  if (!req.auth && req.nextUrl.pathname !== "/login") {
    return NextResponse.redirect(new URL("/login", req.url))
  }
})

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"]
}
```

---

### 7. Environment Variables

**Decision**: Separate env files for frontend and backend

**Frontend (.env.local)**:
```
BETTER_AUTH_SECRET=<32+ character random string>
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://... (for Better Auth tables)
```

**Backend (.env)**:
```
DATABASE_URL=postgresql://...
JWKS_URL=http://localhost:3000/api/auth/jwks
JWT_ISSUER=http://localhost:3000
CORS_ORIGINS=http://localhost:3000
```

---

## Technology Stack Summary

| Component | Technology | Version |
|-----------|------------|---------|
| Frontend Auth | Better Auth | latest |
| JWT Plugin | better-auth/plugins/jwt | latest |
| Backend JWT | python-jose | 3.3.0+ |
| HTTP Client | httpx | 0.25+ |
| Database ORM | SQLModel | (existing) |
| Password Hashing | Better Auth (argon2) | built-in |

## Security Considerations

1. **JWT Expiry**: Default 15 minutes access token, 7 day refresh
2. **JWKS Caching**: Cache JWKS response for 24 hours, refresh on unknown kid
3. **CORS**: Strict origin checking in FastAPI
4. **HTTPS**: Required for production (JWT in Authorization header)
5. **Password Storage**: Better Auth uses argon2 hashing by default

## Open Questions (Resolved)

| Question | Resolution |
|----------|------------|
| How does frontend get JWT? | `authClient.token()` or `set-auth-jwt` header |
| How does backend verify JWT? | JWKS endpoint + jose library |
| Shared secret needed? | No - JWKS uses public key verification |
| Database for Better Auth? | Same PostgreSQL (Neon DB), separate tables |
