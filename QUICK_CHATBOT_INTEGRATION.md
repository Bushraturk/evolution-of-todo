# Quick Guide: Add Chatbot to https://evolution-of-todo-1wvs.vercel.app/

## 🎯 5 Simple Steps

### 1. Open Vercel Dashboard
Go to: https://vercel.com/dashboard

### 2. Find Your Project
- Look for the project that deploys to `evolution-of-todo-1wvs.vercel.app`
- Click on it

### 3. Change Production Branch
- Settings → Git → Production Branch
- Change to: `004-ai-chatbot`
- Save

### 4. Add Environment Variable
- Settings → Environment Variables
- Add for Production:
  ```
  NEXT_PUBLIC_CHAT_API_URL = https://ubushra-todo-chatbot-backend.hf.space
  ```
- Save

### 5. Redeploy
- Deployments tab
- Click ⋮ on latest deployment
- Click "Redeploy"
- Wait 3 minutes

---

## ✅ After Deployment

**Update CORS on both backends:**

**Main Backend:**
https://huggingface.co/spaces/Ubushra/todo-app-backend/settings
- CORS_ORIGINS = `https://evolution-of-todo-1wvs.vercel.app,http://localhost:3000`

**Chatbot Backend:**
https://huggingface.co/spaces/Ubushra/todo-chatbot-backend/settings
- CORS_ORIGINS = `https://evolution-of-todo-1wvs.vercel.app,http://localhost:3000`

---

## 🧪 Test

1. Open: https://evolution-of-todo-1wvs.vercel.app/
2. Login
3. Look for purple robot icon 🤖 (bottom-right)
4. Click and send: "Add a task to test"
5. Should work! ✅

---

**Total Time: 15 minutes**

**See detailed guide in:** `ADD_CHATBOT_TO_EXISTING_FRONTEND.md`
