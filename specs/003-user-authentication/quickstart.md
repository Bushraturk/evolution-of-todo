# Quickstart: User Authentication & Multi-User Support

**Feature**: 003-user-authentication
**Date**: 2025-12-28

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.13+ with UV package manager (for backend)
- PostgreSQL database (Neon DB recommended)
- Phase 2 completed (full-stack todo app working)

## Setup Steps

### Step 1: Install Better Auth Dependencies (Frontend)

```bash
cd frontend

# Install Better Auth and plugins
npm install better-auth

# Install database adapter (using existing PostgreSQL)
npm install @better-auth/pg
```

### Step 2: Configure Better Auth (Frontend)

Create/update `.env.local`:
```env
# Better Auth
BETTER_AUTH_SECRET=<generate-32-char-random-string>
BETTER_AUTH_URL=http://localhost:3000

# Database (same as backend)
DATABASE_URL=postgresql://user:pass@host.neon.tech/dbname?sslmode=require

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Generate a secure secret:
```bash
openssl rand -base64 32
```

### Step 3: Create Auth Configuration (Frontend)

Create `frontend/src/lib/auth.ts`:
```typescript
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"
import { Pool } from "pg"

export const auth = betterAuth({
  database: new Pool({
    connectionString: process.env.DATABASE_URL
  }),
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8
  },
  plugins: [jwt()]
})
```

Create `frontend/src/lib/auth-client.ts`:
```typescript
import { createAuthClient } from "better-auth/react"
import { jwtClient } from "better-auth/client/plugins"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_AUTH_URL || "http://localhost:3000",
  plugins: [jwtClient()]
})
```

### Step 4: Create Auth API Route (Frontend)

Create `frontend/src/app/api/auth/[...all]/route.ts`:
```typescript
import { auth } from "@/lib/auth"
import { toNextJsHandler } from "better-auth/next-js"

export const { GET, POST } = toNextJsHandler(auth)
```

### Step 5: Run Better Auth Migrations

```bash
cd frontend
npx @better-auth/cli migrate
```

This creates the `user`, `session`, `account`, and `verification` tables.

### Step 6: Install JWT Dependencies (Backend)

```bash
cd backend

# Add to pyproject.toml dependencies
uv add python-jose[cryptography] httpx
```

### Step 7: Configure Backend Environment

Update `backend/.env`:
```env
DATABASE_URL=postgresql://user:pass@host.neon.tech/dbname?sslmode=require
CORS_ORIGINS=http://localhost:3000
JWKS_URL=http://localhost:3000/api/auth/jwks
JWT_ISSUER=http://localhost:3000
DEBUG=true
```

### Step 8: Update Backend Database Schema

Add `user_id` column to tasks table:
```bash
cd backend

# Option A: Direct SQL (via psql or Neon console)
psql $DATABASE_URL -c "
  ALTER TABLE task ADD COLUMN user_id TEXT;
  DELETE FROM task;  -- Remove existing tasks
  ALTER TABLE task ALTER COLUMN user_id SET NOT NULL;
  CREATE INDEX idx_task_user_id ON task(user_id);
"

# Option B: Using SQLModel migration (if using Alembic)
# Create migration file and run alembic upgrade head
```

### Step 9: Start the Application

Terminal 1 - Backend:
```bash
cd backend
uv run uvicorn src.main:app --reload --port 8000
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

### Step 10: Verify Setup

1. **Check JWKS endpoint**: `curl http://localhost:3000/api/auth/jwks`
   - Should return JSON with `keys` array

2. **Create test user**: Navigate to `http://localhost:3000/register`
   - Fill in email, password (8+ chars), name
   - Should redirect to dashboard

3. **Verify token**: Open browser console on dashboard:
   ```javascript
   const { data } = await authClient.token()
   console.log(data.token)
   ```

4. **Test protected API**:
   ```bash
   TOKEN="<paste-token-here>"
   curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tasks
   ```
   - Should return `{"data": [], "count": 0}` (empty task list for new user)

## Development Workflow

### Creating Pages

```typescript
// Protected page - checks auth
import { authClient } from "@/lib/auth-client"

export default function Dashboard() {
  const { data: session, isPending } = authClient.useSession()

  if (isPending) return <div>Loading...</div>
  if (!session) redirect("/login")

  return <div>Welcome, {session.user.name}</div>
}
```

### Making Authenticated API Calls

```typescript
// In frontend/src/services/api.ts
import { authClient } from "@/lib/auth-client"

async function fetchWithAuth<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const { data } = await authClient.token()

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${data?.token}`,
      ...options.headers
    }
  })

  if (!response.ok) {
    if (response.status === 401) {
      // Token expired, redirect to login
      window.location.href = "/login"
    }
    throw new Error(`HTTP ${response.status}`)
  }

  return response.json()
}
```

## Troubleshooting

### "Invalid token" errors
- Check JWKS_URL in backend .env matches frontend URL
- Verify Better Auth migrations ran successfully
- Ensure BETTER_AUTH_SECRET is set in frontend .env.local

### "CORS blocked" errors
- Add frontend URL to CORS_ORIGINS in backend .env
- Restart backend after changing .env

### "User not found" when creating tasks
- Ensure user_id column exists in task table
- Check JWT sub claim matches user.id format

### Database connection issues
- Verify DATABASE_URL is correct in both frontend and backend
- Check SSL mode for Neon DB (`?sslmode=require`)

## Test Scenarios

1. **Registration Flow**
   - Navigate to /register
   - Enter valid email + password (8+ chars)
   - Verify redirect to dashboard
   - Verify user in database

2. **Login Flow**
   - Navigate to /login
   - Enter credentials
   - Verify redirect to dashboard
   - Verify session cookie set

3. **Task Isolation**
   - Create task as User A
   - Logout, login as User B
   - Verify User A's task not visible

4. **Protected Route**
   - Clear cookies
   - Try accessing /dashboard directly
   - Verify redirect to /login

5. **API Authentication**
   - Make request without token
   - Verify 401 response
   - Make request with valid token
   - Verify 200 response with user's data
