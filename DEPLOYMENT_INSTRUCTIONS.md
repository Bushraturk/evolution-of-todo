# Phase IV Deployment Instructions

## Current Status
- ✅ Database migration completed (tables exist)
- ✅ Code committed and pushed to GitHub
- ✅ PR details prepared
- ⏳ Awaiting manual deployment steps

---

## Step 1: Create Pull Request

### Option A: GitHub Web Interface (Easiest)
1. Open your browser and go to:
   ```
   https://github.com/Bushraturk/evolution-of-todo/compare/002-fullstack-webapp...004-ai-chatbot
   ```

2. Click the green **"Create pull request"** button

3. Copy the title and description from `PR_DETAILS.md` file

4. Click **"Create pull request"**

### Option B: Using Git Command
```bash
# Push the branch (already done)
git push origin 004-ai-chatbot

# Then visit this URL in your browser:
https://github.com/Bushraturk/evolution-of-todo/pull/new/004-ai-chatbot
```

---

## Step 2: Deploy Chatbot Backend to Hugging Face Spaces

### Prerequisites
- Hugging Face account
- Space already created: `Ubushra/todo-chatbot-backend`

### Deployment Steps

#### 2.1: Prepare Files for Upload
The following files need to be uploaded to Hugging Face Spaces:
```
phase4-chatbot/backend/
├── Dockerfile
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   ├── models/
│   ├── services/
│   ├── mcp/
│   └── auth/
└── README.md (optional)
```

#### 2.2: Upload to Hugging Face

**Option A: Using Git (Recommended)**
```bash
cd phase4-chatbot/backend

# Add Hugging Face remote (if not already added)
git remote add hf-chatbot https://huggingface.co/spaces/Ubushra/todo-chatbot-backend

# Push to Hugging Face
git push hf-chatbot main
```

**Option B: Web Interface**
1. Go to: https://huggingface.co/spaces/Ubushra/todo-chatbot-backend
2. Click **"Files"** tab
3. Click **"Add file"** → **"Upload files"**
4. Upload all files from `phase4-chatbot/backend/`
5. Ensure `Dockerfile` is in the root directory

#### 2.3: Configure Environment Variables
1. Go to: https://huggingface.co/spaces/Ubushra/todo-chatbot-backend/settings
2. Click **"Variables and secrets"**
3. Add the following environment variables (from `.env.production`):

```
DATABASE_URL=postgresql://neondb_owner:npg_DJvwsZ97ikxH@ep-delicate-hill-adi5oaai-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
GEMINI_API_KEY=AIzaSyCS7xf51Oyk3E2psbalJaooAtJdc0-2ebs
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
GEMINI_MODEL=gemini-2.5-flash
JWT_SECRET=complex-secret-key-at-least-32-characters-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7
CORS_ORIGINS=http://localhost:3000
DEBUG=false
LOG_LEVEL=INFO
MAX_CONVERSATION_HISTORY=50
CONVERSATION_ARCHIVE_DAYS=90
LLM_REQUEST_TIMEOUT=30
LLM_MAX_RETRIES=3
PORT=7860
```

**Note:** We'll update `CORS_ORIGINS` after deploying the frontend.

#### 2.4: Verify Deployment
1. Wait for the Space to build (check the "Logs" tab)
2. Once running, test the health endpoint:
   ```bash
   curl https://ubushra-todo-chatbot-backend.hf.space/health
   ```
3. Check API docs:
   ```
   https://ubushra-todo-chatbot-backend.hf.space/docs
   ```

---

## Step 3: Deploy Frontend to Vercel

### Prerequisites
- Vercel account
- Vercel CLI installed (optional) or use web interface

### Deployment Steps

#### 3.1: Update Environment Variables
Before deploying, we need to know the production URLs. Let's assume:
- Main Backend: `https://ubushra-todo-app-backend.hf.space`
- Chatbot Backend: `https://ubushra-todo-chatbot-backend.hf.space`
- Frontend: Will be assigned by Vercel (e.g., `https://evolution-of-todo.vercel.app`)

#### 3.2: Deploy via Vercel Dashboard (Easiest)

1. Go to: https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Import from GitHub:
   - Select repository: `Bushraturk/evolution-of-todo`
   - Select branch: `004-ai-chatbot`
4. Configure project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
5. Add Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://ubushra-todo-app-backend.hf.space
   NEXT_PUBLIC_CHAT_API_URL=https://ubushra-todo-chatbot-backend.hf.space
   NEXT_PUBLIC_AUTH_URL=https://YOUR-VERCEL-URL.vercel.app
   ```
   **Note:** You'll need to update `NEXT_PUBLIC_AUTH_URL` after the first deployment.
6. Click **"Deploy"**

#### 3.3: Deploy via Vercel CLI (Alternative)

```bash
cd frontend

# Install Vercel CLI if not installed
npm i -g vercel

# Login to Vercel
vercel login

# Deploy to production
vercel --prod

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? evolution-of-todo
# - Directory? ./
# - Override settings? No
```

#### 3.4: Update Environment Variables After First Deploy

1. Note your Vercel URL (e.g., `https://evolution-of-todo.vercel.app`)
2. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
3. Update `NEXT_PUBLIC_AUTH_URL` to your actual Vercel URL
4. Redeploy the frontend

---

## Step 4: Update CORS Origins

After both deployments are complete, update CORS settings on both backends.

### 4.1: Update Main Backend (Port 8001)
1. Go to your main backend Hugging Face Space settings
2. Update `CORS_ORIGINS` environment variable:
   ```
   CORS_ORIGINS=https://YOUR-VERCEL-URL.vercel.app,http://localhost:3000
   ```
3. Restart the Space

### 4.2: Update Chatbot Backend (Port 8002)
1. Go to: https://huggingface.co/spaces/Ubushra/todo-chatbot-backend/settings
2. Update `CORS_ORIGINS` environment variable:
   ```
   CORS_ORIGINS=https://YOUR-VERCEL-URL.vercel.app,http://localhost:3000
   ```
3. Restart the Space

---

## Step 5: Verify Complete Deployment

### 5.1: Health Checks
```bash
# Main Backend
curl https://ubushra-todo-app-backend.hf.space/health

# Chatbot Backend
curl https://ubushra-todo-chatbot-backend.hf.space/health

# Frontend (should return HTML)
curl https://YOUR-VERCEL-URL.vercel.app
```

### 5.2: End-to-End Testing

1. **Open Frontend**
   - Go to: `https://YOUR-VERCEL-URL.vercel.app`
   - Verify page loads without errors

2. **Test Authentication**
   - Register a new account or login
   - Verify you're redirected to dashboard

3. **Test Task Management**
   - Add a task manually
   - Verify it appears in the list
   - Mark it complete
   - Delete it

4. **Test Chatbot**
   - Look for purple robot icon (bottom-right corner)
   - Click to open chat modal
   - Send message: "Add a task to test deployment"
   - Verify chatbot responds
   - Check if task appears in main task list
   - Test other commands:
     - "List all my tasks"
     - "Complete the deployment test task"
     - "Delete the deployment test task"

5. **Test Conversation Persistence**
   - Close chat modal
   - Reopen it
   - Verify conversation history is preserved

6. **Test Multi-User Isolation**
   - Open incognito window
   - Register different user
   - Add tasks via chatbot
   - Verify tasks don't appear in first user's list

### 5.3: Check Browser Console
- Open Developer Tools (F12)
- Check Console tab for errors
- Check Network tab for failed requests

---

## Step 6: Merge Pull Request

After successful deployment verification:

1. Go to your Pull Request on GitHub
2. Review the changes one final time
3. Click **"Merge pull request"**
4. Select merge method: **"Squash and merge"** (recommended)
5. Confirm merge

---

## Step 7: Tag Release

```bash
# Switch to main branch
git checkout 002-fullstack-webapp

# Pull latest changes
git pull origin 002-fullstack-webapp

# Create release tag
git tag -a v1.4.0 -m "Phase IV: AI-Powered Todo Chatbot

Features:
- Natural language task management
- Google Gemini 2.0 Flash integration
- 5 MCP tools (add, list, complete, update, delete)
- Conversation history persistence
- Multi-user support with data isolation
- Real-time chat interface with purple robot icon

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

# Push tag to GitHub
git push origin v1.4.0
```

---

## Troubleshooting

### Chatbot Backend Won't Start
**Symptoms:** Space shows "Building" or "Error" status

**Solutions:**
1. Check Hugging Face Spaces logs
2. Verify all environment variables are set
3. Ensure `Dockerfile` is in root directory
4. Check `requirements.txt` has all dependencies
5. Verify `DATABASE_URL` is correct

### Frontend Can't Connect to Backend
**Symptoms:** Network errors in browser console

**Solutions:**
1. Verify `NEXT_PUBLIC_CHAT_API_URL` is correct
2. Check CORS_ORIGINS includes frontend URL
3. Verify chatbot backend is running
4. Check browser network tab for exact error

### Chatbot Doesn't Respond
**Symptoms:** Messages send but no response

**Solutions:**
1. Check chatbot backend logs
2. Verify `GEMINI_API_KEY` is valid
3. Check database connection
4. Verify JWT token is being sent
5. Test health endpoint

### Tasks Don't Appear in List
**Symptoms:** Chatbot creates tasks but they don't show

**Solutions:**
1. Verify main backend is running
2. Check JWT token is valid
3. Verify user_id matches
4. Check database for task records
5. Refresh the page

---

## Production URLs (Update After Deployment)

```
Main Backend: https://ubushra-todo-app-backend.hf.space
Chatbot Backend: https://ubushra-todo-chatbot-backend.hf.space
Frontend: https://YOUR-VERCEL-URL.vercel.app
Database: Neon DB (already configured)
```

---

## Next Steps After Successful Deployment

1. ✅ Update README.md with production URLs
2. ✅ Add screenshots/demo GIF
3. ✅ Monitor error logs for first 24 hours
4. ✅ Test with real users
5. ✅ Gather feedback
6. ✅ Plan Phase V (Kubernetes Deployment)

---

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review logs in Hugging Face Spaces
3. Check Vercel deployment logs
4. Verify all environment variables
5. Test each component individually

**Documentation:**
- `DEPLOYMENT_READY.md` - Quick deployment guide
- `CHATBOT_TESTING_GUIDE.md` - Testing instructions
- `phase4-chatbot/README.md` - Phase IV overview

---

**Ready to deploy! Follow the steps above in order.**
