# Testing Authentication Flow

## Current Status
✅ Backend running on: http://localhost:8001
✅ Database recreated with correct schema (includes user_id column)
✅ Authentication endpoints working

## How to Test

### Step 1: Start Frontend (if not already running)
```bash
cd frontend
npm run dev
```
Frontend will run on: http://localhost:3000

### Step 2: Test the Complete Flow

#### A. Register a New User
1. Open browser: http://localhost:3000
2. You'll be redirected to login page (since not authenticated)
3. Click "Sign up" or go to: http://localhost:3000/register
4. Fill in the registration form:
   - Email: bushra@example.com
   - Password: bushra123
   - Name: Bushra (optional)
5. Click "Sign Up"
6. You'll be automatically logged in and redirected to dashboard

#### B. Login with Existing User
1. Go to: http://localhost:3000/login
2. Enter credentials:
   - Email: bushra@example.com
   - Password: bushra123
3. Click "Sign In"
4. You'll be redirected to the todo dashboard

#### C. Use the Todo App
Once logged in, you can:
- ✅ Add new tasks
- ✅ Mark tasks as complete/incomplete
- ✅ Edit tasks
- ✅ Delete tasks
- ✅ Search tasks
- ✅ Filter by status, priority, category
- ✅ Sort tasks

#### D. Test User Isolation
1. Logout (click user menu in top right → Logout)
2. Register a second user with different email
3. Add some tasks for the second user
4. Logout and login as first user
5. Verify: Each user only sees their own tasks ✅

### Step 3: Verify Backend Logs
Check the backend terminal for SQL queries showing user_id filtering:
```
SELECT task.* FROM task WHERE task.user_id = ?
```

## Expected Behavior

### Authentication Flow
```
User visits http://localhost:3000
    ↓
Not authenticated? → Redirect to /login
    ↓
User clicks "Sign up" → /register
    ↓
Fill form → POST /api/auth/register
    ↓
Success → JWT token stored in localStorage
    ↓
Redirect to / (dashboard)
    ↓
All API requests include: Authorization: Bearer <token>
    ↓
Backend verifies JWT and extracts user_id
    ↓
All tasks filtered by user_id
```

### Protected Routes
- `/` (dashboard) - Requires authentication
- `/login` - Public
- `/register` - Public

## Troubleshooting

### Frontend not connecting to backend?
Check `frontend/.env`:
```
NEXT_PUBLIC_API_URL=http://localhost:8001
```

### Backend not running?
```bash
cd backend
uvicorn src.main:app --reload --port 8001
```

### Database issues?
Delete and recreate:
```bash
cd backend
rm todo_app.db
# Restart backend - it will recreate the database
```

### CORS errors?
Backend should have CORS enabled for http://localhost:3000
Check `backend/src/main.py` for CORS middleware.

## API Endpoints

### Authentication
- POST `/api/auth/register` - Register new user
- POST `/api/auth/login` - Login user
- GET `/api/auth/me` - Get current user (requires auth)

### Tasks (all require authentication)
- GET `/api/tasks` - Get all tasks for current user
- POST `/api/tasks` - Create new task
- GET `/api/tasks/{id}` - Get specific task
- PUT `/api/tasks/{id}` - Update task
- DELETE `/api/tasks/{id}` - Delete task
- PATCH `/api/tasks/{id}/complete` - Toggle completion

### Categories
- GET `/api/categories` - Get all categories
- POST `/api/categories` - Create category
