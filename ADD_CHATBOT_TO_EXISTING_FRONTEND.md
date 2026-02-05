# Add Chatbot to Existing Frontend: https://evolution-of-todo-1wvs.vercel.app/

## 🎯 Goal
Add chatbot components to your existing deployment without creating a new URL.

---

## 📋 Step-by-Step Instructions

### Step 1: Find Your Vercel Project

1. **Open Vercel Dashboard:**
   ```
   https://vercel.com/dashboard
   ```

2. **Find the project** that deploys to `evolution-of-todo-1wvs.vercel.app`
   - Look through your projects list
   - Click on each project to check its production URL
   - Find the one that matches `evolution-of-todo-1wvs.vercel.app`

3. **Note the project name** (you'll need it)

---

### Step 2: Change Production Branch

1. **In your project, go to "Settings"** tab

2. **Click "Git"** in the left sidebar

3. **Find "Production Branch"** section

4. **Change the branch:**
   - Current: Probably `002-fullstack-webapp` or `main`
   - **Change to:** `004-ai-chatbot`

5. **Click "Save"**

---

### Step 3: Update Environment Variables

1. **Still in Settings, click "Environment Variables"**

2. **Add/Update these variables for Production:**

   **Add if not exists:**
   ```
   NEXT_PUBLIC_CHAT_API_URL = https://ubushra-todo-chatbot-backend.hf.space
   ```

   **Verify these exist:**
   ```
   NEXT_PUBLIC_API_URL = https://ubushra-todo-app-backend.hf.space
   NEXT_PUBLIC_AUTH_URL = https://evolution-of-todo-1wvs.vercel.app
   ```

3. **Save all changes**

---

### Step 4: Trigger Redeploy

1. **Go to "Deployments"** tab

2. **Find the latest deployment**

3. **Click the three dots (⋮)** on the right

4. **Click "Redeploy"**

5. **Select:**
   - ✅ Use existing Build Cache (optional, makes it faster)
   - Click "Redeploy"

6. **Wait 2-3 minutes** for build to complete

---

### Step 5: Verify Chatbot is Added

After deployment completes:

1. **Open:** https://evolution-of-todo-1wvs.vercel.app/

2. **Login** to your account

3. **Look for purple robot icon 🤖** in bottom-right corner

4. **If you see the icon:** ✅ Chatbot successfully added!

5. **Click the icon** to test:
   - Send: "Add a task to buy groceries"
   - Should respond and create task

---

## 🔧 Then Update CORS

After chatbot is added, update CORS on both backends:

### Main Backend:
1. Go to: https://huggingface.co/spaces/Ubushra/todo-app-backend/settings
2. Variables → Edit `CORS_ORIGINS`
3. Make sure it includes: `https://evolution-of-todo-1wvs.vercel.app`
4. Should be:
   ```
   https://evolution-of-todo-1wvs.vercel.app,http://localhost:3000
   ```
5. Save and restart

### Chatbot Backend:
1. Go to: https://huggingface.co/spaces/Ubushra/todo-chatbot-backend/settings
2. Variables → Edit `CORS_ORIGINS`
3. Set to:
   ```
   https://evolution-of-todo-1wvs.vercel.app,http://localhost:3000
   ```
4. Save and restart

---

## ✅ Success Checklist

After completing all steps:

- [ ] Found Vercel project
- [ ] Changed production branch to `004-ai-chatbot`
- [ ] Added `NEXT_PUBLIC_CHAT_API_URL` environment variable
- [ ] Redeployed successfully
- [ ] Purple robot icon appears after login
- [ ] Updated CORS on main backend
- [ ] Updated CORS on chatbot backend
- [ ] Tested chatbot - it responds
- [ ] Tasks created by chatbot appear in main list

---

## 🆘 If You Can't Find the Project

If you can't find which Vercel project deploys to `evolution-of-todo-1wvs.vercel.app`:

**Option 1: Check URL in each project**
- Go through each project
- Click on it
- Check the production URL

**Option 2: Use the new deployment**
- Use: https://frontend-mauve-iota-87.vercel.app
- Already has chatbot included
- Just update CORS to use this URL

**Option 3: Ask me for help**
- Tell me the project name if you find it
- Or tell me if you want to use the new deployment instead

---

## 💡 What's in the 004-ai-chatbot Branch

The `004-ai-chatbot` branch includes:
- ✅ All existing features (Auth, Tasks, Categories)
- ✅ ChatbotButton component (purple robot icon)
- ✅ ChatInterface component (chat modal)
- ✅ Chat API integration
- ✅ Conversation history
- ✅ All Phase IV features

---

## ⏱️ Time Required

- Find project: 2 minutes
- Change branch: 1 minute
- Update env vars: 2 minutes
- Redeploy: 3 minutes
- Update CORS: 4 minutes
- Testing: 5 minutes

**Total: ~17 minutes**

---

**Start with Step 1: Find your Vercel project in the dashboard!**

https://vercel.com/dashboard
