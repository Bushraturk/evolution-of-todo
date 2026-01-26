# 🌐 DEPLOY FRONTEND - Vercel Deployment Guide

## 📍 Prerequisites

Before starting, you need:
- ✅ Backend deployed on Hugging Face (from DEPLOY_NOW.md)
- ✅ Your backend URL (e.g., `https://username-todo-app-backend.hf.space`)

---

## STEP 1: Create Vercel Account (2 minutes)

1. Go to: **https://vercel.com/signup**

2. Sign up with one of these options:
   - **GitHub** (Recommended - easier integration)
   - **GitLab**
   - **Bitbucket**
   - **Email**

3. Complete verification if required

---

## STEP 2: Import Project (3 minutes)

### Option A: If You Have GitHub Access

1. Click **"Add New..."** → **"Project"**

2. Click **"Import Git Repository"**

3. Find `evolution-of-todo` repository and click **"Import"**

4. If you don't see it, click **"Adjust GitHub App Permissions"** and grant access

### Option B: If GitHub Push Failed (Alternative)

You can deploy by uploading files directly or connecting a different Git provider. For now, let's try Option A first.

---

## STEP 3: Configure Project Settings (2 minutes)

After importing, you'll see the configuration screen:

### Framework Preset:
- Should auto-detect as **"Next.js"**
- If not, select **"Next.js"** from dropdown

### Root Directory:
- Click **"Edit"** next to Root Directory
- Enter: `frontend`
- Click **"Continue"**

### Build Settings (should auto-fill):
```
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

**Don't click Deploy yet!** We need to add environment variables first.

---

## STEP 4: Add Environment Variables (5 minutes)

Click **"Environment Variables"** section to expand it.

Add these 4 variables (click "Add" after each):

### Variable 1: API URL
```
Name: NEXT_PUBLIC_API_URL
Value: [YOUR HUGGING FACE BACKEND URL]
```
**Example:** `https://username-todo-app-backend.hf.space`
**Important:** Use YOUR actual backend URL from Step 1

### Variable 2: Better Auth Secret
```
Name: BETTER_AUTH_SECRET
Value: 84476a02f1a5c65ae889d6bc950a3ec8de250723632c06d17bf547201756e31e
```

### Variable 3: Better Auth URL (Temporary)
```
Name: BETTER_AUTH_URL
Value: https://your-project.vercel.app
```
**Note:** We'll update this with the actual URL after deployment

### Variable 4: Database URL
```
Name: DATABASE_URL
Value: postgresql://neondb_owner:npg_DJvwsZ97ikxH@ep-delicate-hill-adi5oaai-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
```

---

## STEP 5: Deploy (5 minutes)

1. Click **"Deploy"** button

2. Wait for build to complete (3-5 minutes)

3. You'll see:
   - Installing dependencies...
   - Building application...
   - Deploying...
   - ✅ Deployment successful!

4. Vercel will show your live URL:
   ```
   https://your-project-name.vercel.app
   ```

**✏️ IMPORTANT: Write down your frontend URL:**
```
My Frontend URL: https://________________________________.vercel.app
```

---

## STEP 6: Update BETTER_AUTH_URL (2 minutes)

Now that you have your actual Vercel URL, update the environment variable:

1. In Vercel dashboard, go to your project

2. Click **"Settings"** tab

3. Click **"Environment Variables"** in left sidebar

4. Find `BETTER_AUTH_URL` and click **"Edit"**

5. Update value to your actual Vercel URL:
   ```
   https://your-actual-project-name.vercel.app
   ```

6. Click **"Save"**

7. Go to **"Deployments"** tab

8. Click **"..."** menu on the latest deployment

9. Click **"Redeploy"**

10. Wait ~2 minutes for redeployment

---

## STEP 7: Update Backend CORS (3 minutes)

Now update your backend to allow requests from your frontend:

1. Go back to **Hugging Face Space**

2. Click **"Settings"** tab

3. Scroll to **"Repository secrets"**

4. Find `CORS_ORIGINS` and click **"Edit"**

5. Update value to include your Vercel URL:
   ```
   https://your-actual-project-name.vercel.app,http://localhost:3000
   ```
   **Important:** Replace with YOUR actual Vercel URL, keep the comma and localhost

6. Click **"Save"**

7. Your backend will automatically restart (~1 minute)

---

## STEP 8: Test Your Deployed App (5 minutes)

### Test 1: Visit Your App
1. Open your Vercel URL in browser
2. ✅ Should see landing page with "Get Started" button

### Test 2: Register New User
1. Click **"Get Started"** or **"Register"**
2. Fill in:
   ```
   Email: test@example.com
   Password: TestPassword123!
   Name: Test User
   ```
3. Click **"Register"**
4. ✅ Should redirect to dashboard

### Test 3: Create Task
1. Use the task form or click "Add Task"
2. Fill in:
   ```
   Title: Production deployment test
   Description: Testing the deployed app
   Priority: High
   ```
3. Click **"Add Task"**
4. ✅ Task should appear in the list

### Test 4: Task Operations
1. ✅ Click checkbox to toggle completion
2. ✅ Click edit icon to modify task
3. ✅ Click delete icon to remove task

### Test 5: Session Persistence
1. Logout from the app
2. Close browser completely
3. Open new browser window
4. Go to your Vercel URL
5. Login with same credentials
6. ✅ Should see your tasks (if you didn't delete them)

### Test 6: Check Browser Console
1. Press **F12** to open Developer Tools
2. Go to **"Console"** tab
3. ✅ Should see NO red errors
4. ✅ Should see NO CORS errors

---

## 🎉 SUCCESS CRITERIA

If all tests pass, your deployment is complete!

- ✅ Frontend accessible at Vercel URL
- ✅ Backend accessible at Hugging Face URL
- ✅ User registration works
- ✅ User login works
- ✅ Tasks can be created, edited, deleted
- ✅ Session persists across browser restarts
- ✅ No CORS errors in console

---

## 🆘 Troubleshooting

### "Failed to fetch" or "Network error"
**Problem:** Frontend can't connect to backend
**Solution:**
1. Check `NEXT_PUBLIC_API_URL` in Vercel settings
2. Make sure it matches your Hugging Face URL exactly
3. Test backend health: `https://YOUR-BACKEND-URL.hf.space/health`

### "CORS policy" error in console
**Problem:** Backend not allowing frontend origin
**Solution:**
1. Go to Hugging Face Space → Settings → Repository secrets
2. Edit `CORS_ORIGINS`
3. Make sure it includes your Vercel URL
4. Format: `https://your-app.vercel.app,http://localhost:3000`
5. No spaces, comma-separated

### "Authentication failed" or "Invalid token"
**Problem:** Auth configuration mismatch
**Solution:**
1. Verify `BETTER_AUTH_SECRET` is set in Vercel
2. Verify `JWT_SECRET` is set in Hugging Face
3. Make sure `BETTER_AUTH_URL` matches your Vercel URL
4. Redeploy frontend after changing env vars

### Build fails with "Module not found"
**Problem:** Dependencies or configuration issue
**Solution:**
1. Check that Root Directory is set to `frontend`
2. Verify Framework Preset is "Next.js"
3. Check build logs for specific missing module
4. Try redeploying

### Page shows but features don't work
**Problem:** Environment variables not set correctly
**Solution:**
1. Go to Vercel → Settings → Environment Variables
2. Verify all 4 variables are present
3. Check for typos in variable names (case-sensitive)
4. Redeploy after fixing

---

## 📱 Optional: Custom Domain

Want to use your own domain instead of `.vercel.app`?

1. Go to Vercel → Project → **"Settings"** → **"Domains"**
2. Click **"Add"**
3. Enter your domain (e.g., `todo.yourdomain.com`)
4. Follow DNS configuration instructions
5. Update `BETTER_AUTH_URL` and backend `CORS_ORIGINS` with new domain

---

## 📊 Monitoring Your App

### Vercel Analytics
- Go to your project → **"Analytics"** tab
- See page views, performance metrics, and user data

### Vercel Logs
- Go to your project → **"Deployments"** tab
- Click on a deployment → **"Logs"** tab
- See real-time application logs

### Hugging Face Logs
- Go to your Space → **"Logs"** tab
- See backend API logs and errors

---

## 🎯 Final Checklist

- [ ] Backend deployed on Hugging Face
- [ ] Frontend deployed on Vercel
- [ ] All environment variables configured
- [ ] CORS updated with Vercel URL
- [ ] BETTER_AUTH_URL updated with actual URL
- [ ] All tests passed
- [ ] No console errors

---

## 🔗 Your Deployment URLs

**Frontend (User-facing app):**
```
https://________________________________.vercel.app
```

**Backend API:**
```
https://________________________________.hf.space
```

**API Documentation:**
```
https://________________________________.hf.space/docs
```

---

## 🎊 Congratulations!

Your full-stack Todo app is now live in production!

**Share your app:**
- Send the Vercel URL to friends/colleagues
- Add it to your portfolio
- Share on social media

**Next steps:**
- Add custom domain (optional)
- Monitor usage and performance
- Add more features
- Scale as needed

---

## 📞 Need Help?

If you encounter any issues:
1. Check the troubleshooting section above
2. Review browser console for errors (F12)
3. Check Vercel deployment logs
4. Check Hugging Face Space logs
5. Verify all environment variables are correct

**Common issues are usually:**
- Typo in environment variable
- Wrong URL in CORS_ORIGINS
- Forgot to redeploy after changing env vars
