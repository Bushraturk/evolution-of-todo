# Phase IV Deployment - Quick Start Guide

## ✅ What's Been Prepared

1. **Database Migration**: ✅ Completed (tables exist)
2. **Code**: ✅ Committed and pushed to GitHub
3. **Documentation**: ✅ All deployment guides created
4. **Environment Variables**: ✅ Production template ready

## 🚀 Next Steps (Manual Actions Required)

### Step 1: Create Pull Request (5 minutes)

**Quick Method:**
1. Open this URL in your browser:
   ```
   https://github.com/Bushraturk/evolution-of-todo/compare/002-fullstack-webapp...004-ai-chatbot
   ```

2. Click the green **"Create pull request"** button

3. Copy the title and description from `PR_DETAILS.md` (in your project root)

4. Click **"Create pull request"**

**Result:** PR created and ready for review

---

### Step 2: Deploy Chatbot Backend to Hugging Face (15 minutes)

**Option A: Web Upload (Easiest)**

1. Go to: https://huggingface.co/spaces/Ubushra/todo-chatbot-backend
   - If space doesn't exist, create it:
     - Click "New Space"
     - Name: `todo-chatbot-backend`
     - SDK: Docker
     - Hardware: CPU Basic (free)

2. Upload these files from `phase4-chatbot/backend/`:
   - `Dockerfile`
   - `requirements.txt`
   - `src/` folder (entire directory)
   - `README.md`

3. Configure Environment Variables:
   - Go to Settings → Variables and secrets
   - Copy all variables from `phase4-chatbot/backend/.env.production`
   - **Important:** Set `CORS_ORIGINS=http://localhost:3000` for now (will update later)

4. Wait for build to complete (check Logs tab)

5. Test: Open `https://ubushra-todo-chatbot-backend.hf.space/health`
   - Should return: `{"status": "healthy"}`

**Option B: Git Push (Advanced)**
```bash
cd phase4-chatbot/backend
git remote add hf https://huggingface.co/spaces/Ubushra/todo-chatbot-backend
git push hf main
```

**Result:** Chatbot backend running on Hugging Face

---

### Step 3: Deploy Frontend to Vercel (10 minutes)

1. Go to: https://vercel.com/dashboard

2. Click **"Add New..."** → **"Project"**

3. Import from GitHub:
   - Repository: `Bushraturk/evolution-of-todo`
   - Branch: `004-ai-chatbot`

4. Configure:
   - Framework: **Next.js** (auto-detected)
   - Root Directory: **`frontend`**
   - Build Command: `npm run build`
   - Output Directory: `.next`

5. Add Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://ubushra-todo-app-backend.hf.space
   NEXT_PUBLIC_CHAT_API_URL=https://ubushra-todo-chatbot-backend.hf.space
   NEXT_PUBLIC_AUTH_URL=https://YOUR-APP.vercel.app
   ```
   **Note:** For `NEXT_PUBLIC_AUTH_URL`, use the Vercel URL you'll get after deployment

6. Click **"Deploy"**

7. After deployment completes:
   - Note your Vercel URL (e.g., `https://evolution-of-todo.vercel.app`)
   - Go to Settings → Environment Variables
   - Update `NEXT_PUBLIC_AUTH_URL` with your actual Vercel URL
   - Redeploy (Deployments → ... → Redeploy)

**Result:** Frontend running on Vercel

---

### Step 4: Update CORS Origins (5 minutes)

Now that you have your Vercel URL, update both backends:

**Main Backend (Hugging Face):**
1. Go to your main backend space settings
2. Find `CORS_ORIGINS` variable
3. Update to: `https://YOUR-VERCEL-URL.vercel.app,http://localhost:3000`
4. Restart the space

**Chatbot Backend (Hugging Face):**
1. Go to: https://huggingface.co/spaces/Ubushra/todo-chatbot-backend/settings
2. Find `CORS_ORIGINS` variable
3. Update to: `https://YOUR-VERCEL-URL.vercel.app,http://localhost:3000`
4. Restart the space

**Result:** Backends configured to accept requests from your frontend

---

### Step 5: Verify Deployment (10 minutes)

**Automated Check:**
```bash
# Update URLs in verify-deployment.sh first, then run:
bash verify-deployment.sh
```

**Manual Testing:**
1. Open your Vercel URL in browser
2. Register or login
3. Look for purple robot icon (bottom-right corner)
4. Click to open chat
5. Send: "Add a task to test deployment"
6. Verify:
   - ✅ Chatbot responds
   - ✅ Task appears in main task list
   - ✅ No console errors (F12)

**Test Commands:**
- "List all my tasks"
- "Complete the deployment test task"
- "Delete the deployment test task"

**Result:** Everything working in production

---

### Step 6: Merge PR and Tag Release (5 minutes)

1. Go to your Pull Request on GitHub
2. Review changes
3. Click **"Merge pull request"**
4. Select **"Squash and merge"**
5. Confirm merge

**Tag the release:**
```bash
git checkout 002-fullstack-webapp
git pull origin 002-fullstack-webapp
git tag -a v1.4.0 -m "Phase IV: AI-Powered Todo Chatbot"
git push origin v1.4.0
```

**Result:** Phase IV merged and released

---

## 📋 Deployment Checklist

Use `DEPLOYMENT_CHECKLIST.md` to track your progress.

## 📚 Documentation Files

- **DEPLOYMENT_INSTRUCTIONS.md** - Detailed step-by-step guide
- **DEPLOYMENT_CHECKLIST.md** - Track your progress
- **PR_DETAILS.md** - Pull request template
- **verify-deployment.sh** - Automated verification script
- **phase4-chatbot/backend/.env.production** - Environment variables template

## 🆘 Need Help?

If you encounter issues:
1. Check `DEPLOYMENT_INSTRUCTIONS.md` troubleshooting section
2. Review Hugging Face Spaces logs
3. Check Vercel deployment logs
4. Verify all environment variables are set correctly

## ⏱️ Estimated Time

- Total: ~50 minutes
- Can be done in stages (deploy backend, then frontend, etc.)

---

## 🎯 Success Criteria

Your deployment is successful when:
- ✅ Frontend loads without errors
- ✅ Purple robot icon appears after login
- ✅ Chatbot responds to messages
- ✅ Tasks are created and appear in list
- ✅ Conversation history persists
- ✅ No console errors

---

**Ready to start? Begin with Step 1: Create Pull Request**

Open this URL: https://github.com/Bushraturk/evolution-of-todo/compare/002-fullstack-webapp...004-ai-chatbot
