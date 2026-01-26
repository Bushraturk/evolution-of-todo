# 🚀 Deployment Guide: Todo App to Production

## Quick Summary

**Backend**: Hugging Face Spaces (Docker)
**Frontend**: Vercel (Next.js)
**Database**: Neon DB (already configured)

**Total Time**: ~30-45 minutes

---

## 🔐 Production Secrets (Generated)

Save these securely - you'll need them during deployment:

```bash
# Backend JWT Secret (for Hugging Face)
JWT_SECRET=1e2d3b277e18b3a2bc2f590c5c949b327e28cbf69f2869d7d0757f3c36746249

# Frontend Better Auth Secret (for Vercel)
BETTER_AUTH_SECRET=84476a02f1a5c65ae889d6bc950a3ec8de250723632c06d17bf547201756e31e

# Database URL (existing Neon DB)
DATABASE_URL=postgresql://neondb_owner:npg_DJvwsZ97ikxH@ep-delicate-hill-adi5oaai-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
```

---

## Part 1: Deploy Backend to Hugging Face Spaces

### Step 1: Create Hugging Face Account

1. Go to https://huggingface.co/join
2. Sign up with email or GitHub
3. Verify your email

### Step 2: Create New Space

1. Visit https://huggingface.co/new-space
2. Fill in the form:
   - **Owner**: Your username
   - **Space name**: `todo-app-backend`
   - **License**: MIT
   - **Select the Space SDK**: Docker
   - **Space hardware**: CPU basic - 2 vCPU - 16GB RAM (FREE)
   - **Visibility**: Public (or Private if you prefer)
3. Click **"Create Space"**

### Step 3: Upload Backend Files

**Option A: Web Upload (Easiest)**

1. In your new Space, you'll see an empty repository
2. Click **"Files and versions"** tab
3. Click **"Add file"** → **"Upload files"**
4. Upload these files from `C:\Users\admin\Desktop\b-todo-app\evolution-of-todo\backend\`:
   - `Dockerfile`
   - `requirements.txt`
   - `pyproject.toml`
   - Entire `src/` folder (drag and drop the folder)
5. Add commit message: "Initial backend deployment"
6. Click **"Commit changes to main"**

**Option B: Git Push (After fixing authentication)**

```bash
cd C:\Users\admin\Desktop\b-todo-app\evolution-of-todo\backend

# Add Hugging Face remote
git init
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/todo-app-backend
git add .
git commit -m "Initial backend deployment"
git push hf main
```

### Step 4: Configure Environment Variables

1. In your Space, click **"Settings"** tab
2. Scroll to **"Repository secrets"**
3. Add these secrets (click "New secret" for each):

```
Name: DATABASE_URL
Value: postgresql://neondb_owner:npg_DJvwsZ97ikxH@ep-delicate-hill-adi5oaai-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require

Name: JWT_SECRET
Value: 1e2d3b277e18b3a2bc2f590c5c949b327e28cbf69f2869d7d0757f3c36746249

Name: CORS_ORIGINS
Value: http://localhost:3000
(Note: Will update this after getting Vercel URL)

Name: DEBUG
Value: false
```

### Step 5: Wait for Build

1. Go back to **"App"** tab
2. Hugging Face will automatically build your Docker container
3. Build takes ~5-10 minutes
4. You'll see build logs in real-time
5. Once complete, your API will be live at:
   ```
   https://YOUR_USERNAME-todo-app-backend.hf.space
   ```

### Step 6: Verify Backend Deployment

Test these URLs in your browser:

1. **Health Check**:
   ```
   https://YOUR_USERNAME-todo-app-backend.hf.space/health
   ```
   Should return: `{"status":"healthy"}`

2. **API Documentation**:
   ```
   https://YOUR_USERNAME-todo-app-backend.hf.space/docs
   ```
   Should show FastAPI Swagger UI

**Save your backend URL** - you'll need it for frontend configuration!

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Create Vercel Account

1. Go to https://vercel.com/signup
2. Sign up with GitHub (recommended) or email
3. Authorize Vercel to access your GitHub account

### Step 2: Import Project

1. Click **"Add New..."** → **"Project"**
2. Click **"Import Git Repository"**
3. If you see your `evolution-of-todo` repo, click **"Import"**
4. If not, click **"Adjust GitHub App Permissions"** and grant access

### Step 3: Configure Build Settings

**Framework Preset**: Next.js (auto-detected)

**Root Directory**: Click **"Edit"** and set to `frontend`

**Build Settings** (should auto-fill):
- Build Command: `npm run build`
- Output Directory: `.next`
- Install Command: `npm install`

### Step 4: Add Environment Variables

Click **"Environment Variables"** and add these:

```
Name: NEXT_PUBLIC_API_URL
Value: https://YOUR_USERNAME-todo-app-backend.hf.space
(Use your Hugging Face Space URL from Part 1)

Name: BETTER_AUTH_SECRET
Value: 84476a02f1a5c65ae889d6bc950a3ec8de250723632c06d17bf547201756e31e

Name: BETTER_AUTH_URL
Value: https://YOUR_PROJECT_NAME.vercel.app
(Vercel will show you this URL, or leave blank for now and add after deployment)

Name: DATABASE_URL
Value: postgresql://neondb_owner:npg_DJvwsZ97ikxH@ep-delicate-hill-adi5oaai-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
```

### Step 5: Deploy

1. Click **"Deploy"**
2. Wait 3-5 minutes for build
3. Once complete, Vercel will show your live URL:
   ```
   https://YOUR_PROJECT_NAME.vercel.app
   ```

### Step 6: Update BETTER_AUTH_URL

1. Copy your Vercel URL
2. Go to Vercel dashboard → Your project → **"Settings"** → **"Environment Variables"**
3. Find `BETTER_AUTH_URL` and click **"Edit"**
4. Update value to your actual Vercel URL
5. Click **"Save"**
6. Go to **"Deployments"** tab → Click **"..."** on latest deployment → **"Redeploy"**

### Step 7: Update Backend CORS

1. Go back to your Hugging Face Space
2. Click **"Settings"** → **"Repository secrets"**
3. Find `CORS_ORIGINS` and click **"Edit"**
4. Update value to:
   ```
   https://YOUR_PROJECT_NAME.vercel.app,http://localhost:3000
   ```
5. Click **"Save"**
6. Hugging Face will automatically restart your backend (~1 minute)

---

## Part 3: Test Your Deployment

### Test 1: Visit Your App

1. Open your Vercel URL: `https://YOUR_PROJECT_NAME.vercel.app`
2. You should see the landing page with "Get Started" button

### Test 2: Register New User

1. Click **"Get Started"** or **"Register"**
2. Fill in:
   - Email: `test@example.com`
   - Password: `TestPassword123!`
   - Name: `Test User`
3. Click **"Register"**
4. ✅ Should redirect to dashboard

### Test 3: Create Task

1. In the dashboard, click **"Add Task"** or use the form
2. Fill in:
   - Title: "Test production deployment"
   - Description: "Verify everything works"
   - Priority: High
3. Click **"Add Task"**
4. ✅ Task should appear in the list

### Test 4: Task Operations

1. ✅ Toggle completion (click checkbox)
2. ✅ Edit task (click edit icon)
3. ✅ Delete task (click delete icon)

### Test 5: Session Persistence

1. Logout
2. Close browser
3. Open new browser tab
4. Visit your app URL
5. Login with same credentials
6. ✅ Should see your tasks

---

## 🎉 Success Criteria

- ✅ Backend API accessible at Hugging Face URL
- ✅ Frontend accessible at Vercel URL
- ✅ User registration works
- ✅ User login works
- ✅ Tasks can be created, edited, deleted
- ✅ Session persists across browser restarts
- ✅ No CORS errors in browser console

---

## 🔧 Troubleshooting

### Backend Issues

**Problem**: "Connection refused" or "Cannot connect to database"
**Solution**: Check DATABASE_URL in Hugging Face secrets

**Problem**: "CORS error" in browser console
**Solution**: Update CORS_ORIGINS in Hugging Face to include your Vercel URL

**Problem**: "Invalid token" errors
**Solution**: Verify JWT_SECRET is set correctly in Hugging Face

### Frontend Issues

**Problem**: "Failed to fetch" or "Network error"
**Solution**: Check NEXT_PUBLIC_API_URL points to your Hugging Face URL

**Problem**: "Authentication failed"
**Solution**: Verify BETTER_AUTH_SECRET is set in Vercel

**Problem**: Build fails with "Module not found"
**Solution**: Ensure Root Directory is set to `frontend` in Vercel settings

---

## 📝 Next Steps

1. **Custom Domain** (Optional):
   - Vercel: Settings → Domains → Add your domain
   - Hugging Face: Settings → Custom domain

2. **Monitoring**:
   - Vercel: Analytics tab for performance metrics
   - Hugging Face: Logs tab for backend errors

3. **Update README**:
   - Add your production URLs to the main README.md

---

## 🔗 Quick Links

- **Frontend**: https://YOUR_PROJECT_NAME.vercel.app
- **Backend API**: https://YOUR_USERNAME-todo-app-backend.hf.space
- **API Docs**: https://YOUR_USERNAME-todo-app-backend.hf.space/docs
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Hugging Face Dashboard**: https://huggingface.co/spaces

---

## 📞 Support

If you encounter issues:
1. Check browser console for errors (F12)
2. Check Hugging Face logs (Logs tab in your Space)
3. Check Vercel deployment logs (Deployments tab)

**Common Issues**:
- CORS errors → Update CORS_ORIGINS
- Database connection → Check DATABASE_URL format
- Authentication errors → Verify secrets are set correctly
