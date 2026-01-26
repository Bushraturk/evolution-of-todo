# 🚀 Quick Deployment Checklist

## ✅ Pre-Deployment (COMPLETED)

- [x] JWT secret configuration added
- [x] Deployment files created (Dockerfile, requirements.txt)
- [x] Production secrets generated
- [x] All changes committed locally

## 📦 Step 1: Deploy Backend to Hugging Face (15 minutes)

### 1.1 Create Hugging Face Space

1. Go to: https://huggingface.co/new-space
2. Settings:
   - Space name: `todo-app-backend`
   - SDK: **Docker**
   - Hardware: **CPU basic (FREE)**
3. Click "Create Space"

### 1.2 Upload Backend Files

**Files to upload from `backend/` folder:**
- ✅ `Dockerfile`
- ✅ `requirements.txt`
- ✅ `pyproject.toml`
- ✅ `src/` (entire folder with all subfolders)

**How to upload:**
1. In your Space, click "Files and versions"
2. Click "Add file" → "Upload files"
3. Drag and drop the files listed above
4. Commit message: "Initial deployment"
5. Click "Commit"

### 1.3 Add Environment Secrets

In Space Settings → Repository secrets, add:

```
DATABASE_URL = postgresql://neondb_owner:npg_DJvwsZ97ikxH@ep-delicate-hill-adi5oaai-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require

JWT_SECRET = 1e2d3b277e18b3a2bc2f590c5c949b327e28cbf69f2869d7d0757f3c36746249

CORS_ORIGINS = http://localhost:3000

DEBUG = false
```

### 1.4 Wait for Build (5-10 minutes)

- Watch build logs in "App" tab
- When complete, test: `https://YOUR_USERNAME-todo-app-backend.hf.space/health`
- Should return: `{"status":"healthy"}`

**✏️ Write down your backend URL:**
```
Backend URL: https://_____________________________.hf.space
```

---

## 🌐 Step 2: Deploy Frontend to Vercel (10 minutes)

### 2.1 Import to Vercel

1. Go to: https://vercel.com/new
2. Import `evolution-of-todo` repository
3. **Root Directory**: Set to `frontend`
4. Framework: Next.js (auto-detected)

### 2.2 Add Environment Variables

```
NEXT_PUBLIC_API_URL = [YOUR BACKEND URL FROM STEP 1.4]

BETTER_AUTH_SECRET = 84476a02f1a5c65ae889d6bc950a3ec8de250723632c06d17bf547201756e31e

BETTER_AUTH_URL = https://YOUR_PROJECT_NAME.vercel.app

DATABASE_URL = postgresql://neondb_owner:npg_DJvwsZ97ikxH@ep-delicate-hill-adi5oaai-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
```

### 2.3 Deploy

- Click "Deploy"
- Wait 3-5 minutes
- Copy your Vercel URL

**✏️ Write down your frontend URL:**
```
Frontend URL: https://_____________________________.vercel.app
```

---

## 🔄 Step 3: Update CORS (5 minutes)

### 3.1 Update Backend CORS

1. Go to Hugging Face Space → Settings → Repository secrets
2. Edit `CORS_ORIGINS` to:
   ```
   https://YOUR_VERCEL_URL.vercel.app,http://localhost:3000
   ```
3. Save (backend will auto-restart)

### 3.2 Update Frontend Auth URL

1. Go to Vercel → Project Settings → Environment Variables
2. Edit `BETTER_AUTH_URL` to your actual Vercel URL
3. Save and redeploy

---

## ✅ Step 4: Test Everything (5 minutes)

1. Visit your Vercel URL
2. Register new account
3. Create a task
4. Toggle completion
5. Edit task
6. Delete task
7. Logout and login again

**If all works → 🎉 DEPLOYMENT COMPLETE!**

---

## 🆘 Quick Fixes

**CORS Error?**
→ Update CORS_ORIGINS in Hugging Face to include your Vercel URL

**Can't connect to API?**
→ Check NEXT_PUBLIC_API_URL in Vercel matches your Hugging Face URL

**Authentication fails?**
→ Verify JWT_SECRET in Hugging Face and BETTER_AUTH_SECRET in Vercel

---

## 📍 Current Status

- Local commits: 3 commits ready (deployment configs)
- Backend files: Ready in `backend/` folder
- Frontend files: Ready in `frontend/` folder
- Secrets: Generated and documented above

**Next Action:** Go to https://huggingface.co/new-space and start Step 1.1
