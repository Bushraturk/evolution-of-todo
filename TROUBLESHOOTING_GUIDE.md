# 🔧 QUICK FIX GUIDE - Chatbot Not Showing

## Problem Identified

1. ✅ Backend port changed: 8000 → 8002
2. ❌ Frontend pe kuch show nahi ho raha

## Solution: Complete Restart

### Step 1: Stop Everything

**Close all terminals** running backend/frontend

Ya phir:
```bash
# Kill all Node processes (frontend)
taskkill /F /IM node.exe

# Kill all Python processes (backend)
taskkill /F /IM python.exe
```

### Step 2: Start Phase IV Chatbot Backend (Port 8002)

**Terminal 1:**
```bash
cd C:\Users\admin\Desktop\b-todo-app\evolution-of-todo\phase4-chatbot\backend
uvicorn src.main:app --reload --port 8002
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8002
INFO:     Application startup complete
```

**Test backend:**
```bash
curl http://localhost:8002/health
```

Should return:
```json
{"status":"healthy","service":"todo-chatbot-backend","version":"1.0.0"}
```

### Step 3: Start Frontend (Port 3000)

**Terminal 2:**
```bash
cd C:\Users\admin\Desktop\b-todo-app\evolution-of-todo\frontend

# Clear Next.js cache
rmdir /s /q .next

# Start fresh
npm run dev
```

**Expected output:**
```
- ready started server on 0.0.0.0:3000
- Local:        http://localhost:3000
```

### Step 4: Clear Browser Cache

**Important!** Browser cache can cause issues.

**Chrome/Edge:**
1. Press `Ctrl + Shift + Delete`
2. Select "Cached images and files"
3. Click "Clear data"

**Or use Incognito/Private mode:**
- Chrome: `Ctrl + Shift + N`
- Edge: `Ctrl + Shift + P`

### Step 5: Open Fresh Browser Tab

1. Open: **http://localhost:3000**
2. You should see the landing page
3. Click **Login** or **Sign Up**
4. After login, you should see the **Dashboard**
5. Look for **purple robot icon** in bottom-right corner 🤖

---

## If Still Not Showing

### Check 1: Frontend Running?

```bash
# Check if port 3000 is listening
netstat -ano | findstr :3000
```

Should show:
```
TCP    0.0.0.0:3000    LISTENING
```

### Check 2: Backend Running?

```bash
# Check if port 8002 is listening
netstat -ano | findstr :8002
```

Should show:
```
TCP    0.0.0.0:8002    LISTENING
```

### Check 3: Browser Console

1. Open browser: http://localhost:3000
2. Press `F12` (Developer Tools)
3. Go to **Console** tab
4. Look for any **red errors**

**Common errors:**
- "Failed to fetch" → Backend not running
- "Network error" → Wrong port in .env.local
- "404 Not Found" → Wrong API URL

### Check 4: Environment File

```bash
cd C:\Users\admin\Desktop\b-todo-app\evolution-of-todo\frontend
cat .env.local
```

Should show:
```
NEXT_PUBLIC_API_URL=http://localhost:8002
```

---

## Complete Fresh Start (Nuclear Option)

Agar phir bhi kaam nahi kar raha:

```bash
# 1. Stop everything
taskkill /F /IM node.exe
taskkill /F /IM python.exe

# 2. Clean frontend
cd C:\Users\admin\Desktop\b-todo-app\evolution-of-todo\frontend
rmdir /s /q .next
rmdir /s /q node_modules
npm install

# 3. Start backend (Phase IV Chatbot)
cd C:\Users\admin\Desktop\b-todo-app\evolution-of-todo\phase4-chatbot\backend
uvicorn src.main:app --reload --port 8002

# 4. Start frontend (new terminal)
cd C:\Users\admin\Desktop\b-todo-app\evolution-of-todo\frontend
npm run dev

# 5. Open browser in incognito mode
# Chrome: Ctrl+Shift+N
# Go to: http://localhost:3000
```

---

## What You Should See

### 1. Landing Page (http://localhost:3000)
```
┌─────────────────────────────────────┐
│                                     │
│         Todo App                    │
│    Phase III - Multi-User Support   │
│                                     │
│     [Get Started]  [Login]          │
│                                     │
└─────────────────────────────────────┘
```

### 2. After Login - Dashboard
```
┌─────────────────────────────────────┐
│  Todo App              [+ Add Task] │
│  Phase III             [User Menu]  │
├─────────────────────────────────────┤
│  [Search Bar]                       │
│  [Filter Bar]                       │
│                                     │
│  Task List:                         │
│  ☐ Task 1                           │
│  ☐ Task 2                           │
│                                     │
│                          ┌────┐     │
│                          │ 🤖 │ ← Robot Icon
│                          └────┘     │
└─────────────────────────────────────┘
```

### 3. Click Robot Icon - Chat Opens
```
┌─────────────────────────────────────┐
│  Dashboard (blurred)                │
│                                     │
│              ┌────────────────┐     │
│              │ 🤖 AI Assistant│     │
│              ├────────────────┤     │
│              │ 👋 Hi! I'm your│     │
│              │ AI assistant.  │     │
│              │                │     │
│              │ Try saying:    │     │
│              │ "Add a task..."│     │
│              ├────────────────┤     │
│              │ [Type here...] │     │
│              └────────────────┘     │
└─────────────────────────────────────┘
```

---

## Troubleshooting Specific Issues

### Issue: "Cannot GET /"

**Problem:** Frontend not running properly

**Fix:**
```bash
cd frontend
npm run dev
```

### Issue: Blank white page

**Problem:** JavaScript error or build issue

**Fix:**
```bash
cd frontend
rmdir /s /q .next
npm run dev
```

### Issue: Robot icon not showing

**Problem:**
- Not logged in
- Dashboard not loaded
- Browser cache

**Fix:**
1. Make sure you're logged in
2. Clear browser cache
3. Hard refresh: `Ctrl + Shift + R`

### Issue: "Not authenticated" in chat

**Problem:** JWT token missing

**Fix:**
1. Logout
2. Login again
3. Try chatbot again

---

## Quick Verification Commands

Run these to verify everything:

```bash
# 1. Check backend health
curl http://localhost:8002/health

# 2. Check frontend
curl http://localhost:3000

# 3. Check ports
netstat -ano | findstr :8002
netstat -ano | findstr :3000

# 4. Check environment
cd frontend && cat .env.local
```

---

## Expected Terminal Outputs

### Backend Terminal (Port 8002)
```
INFO:     Will watch for changes in these directories: [...]
INFO:     Uvicorn running on http://127.0.0.1:8002 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Frontend Terminal (Port 3000)
```
  ▲ Next.js 14.2.16
  - Local:        http://localhost:3000
  - Environments: .env.local, .env

 ✓ Ready in 2.3s
```

---

## Still Having Issues?

### Send me this info:

1. **Backend terminal output:**
   ```bash
   cd phase4-chatbot/backend
   uvicorn src.main:app --reload --port 8002
   # Copy the output
   ```

2. **Frontend terminal output:**
   ```bash
   cd frontend
   npm run dev
   # Copy the output
   ```

3. **Browser console errors:**
   - Open http://localhost:3000
   - Press F12
   - Go to Console tab
   - Copy any red errors

4. **Environment file:**
   ```bash
   cd frontend
   cat .env.local
   # Copy the output
   ```

---

## Summary

**To fix your issues:**

1. ✅ Updated `.env.local` → Backend now points to port 8002
2. 🔄 Restart backend on port 8002
3. 🔄 Restart frontend (clear .next cache)
4. 🔄 Clear browser cache
5. ✅ Open http://localhost:3000 in fresh browser tab

**Commands:**
```bash
# Terminal 1: Backend
cd phase4-chatbot/backend
uvicorn src.main:app --reload --port 8002

# Terminal 2: Frontend
cd frontend
rmdir /s /q .next
npm run dev

# Browser: http://localhost:3000
```

---

**Yeh karo aur batao kya dikha raha hai!** 🚀
