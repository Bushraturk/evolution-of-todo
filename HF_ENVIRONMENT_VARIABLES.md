# Hugging Face Space Environment Variables

## 🎯 IMPORTANT: Set These Environment Variables Now

Go to: https://huggingface.co/spaces/Ubushra/todo-chatbot-backend/settings

Click on **"Variables and secrets"** and add the following:

---

## Required Environment Variables

### Database Configuration
```
DATABASE_URL=postgresql://neondb_owner:npg_DJvwsZ97ikxH@ep-delicate-hill-adi5oaai-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
```

### Gemini API Configuration
```
GEMINI_API_KEY=AIzaSyCS7xf51Oyk3E2psbalJaooAtJdc0-2ebs
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
GEMINI_MODEL=gemini-2.5-flash
```

### JWT Authentication
```
JWT_SECRET=complex-secret-key-at-least-32-characters-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7
```

### Server Configuration
```
CORS_ORIGINS=http://localhost:3000
DEBUG=false
LOG_LEVEL=INFO
```

### Application Settings
```
MAX_CONVERSATION_HISTORY=50
CONVERSATION_ARCHIVE_DAYS=90
LLM_REQUEST_TIMEOUT=30
LLM_MAX_RETRIES=3
PORT=7860
```

---

## 📝 How to Add Variables

For each variable above:

1. Click **"New variable"**
2. **Name**: Copy the variable name (e.g., `DATABASE_URL`)
3. **Value**: Copy the value (e.g., `postgresql://...`)
4. Click **"Save"**

Repeat for all 14 variables.

---

## ⚠️ Important Notes

1. **CORS_ORIGINS**: Currently set to `http://localhost:3000`
   - After deploying frontend to Vercel, you'll need to update this to include your Vercel URL
   - Format: `https://your-app.vercel.app,http://localhost:3000`

2. **JWT_SECRET**: This must match the JWT_SECRET in your main backend
   - Current value: `complex-secret-key-at-least-32-characters-here`

3. **PORT**: Must be `7860` for Hugging Face Spaces

---

## 🔄 After Adding Variables

1. The Space will automatically restart
2. Wait for the build to complete (check the "Logs" tab)
3. Once running, test the health endpoint:
   ```
   https://ubushra-todo-chatbot-backend.hf.space/health
   ```
   Should return: `{"status": "healthy"}`

---

## 🚀 Space URL

Your chatbot backend is deployed at:
```
https://ubushra-todo-chatbot-backend.hf.space
```

API Documentation:
```
https://ubushra-todo-chatbot-backend.hf.space/docs
```

---

## ✅ Next Steps After Setting Variables

1. Wait for Space to build and start (5-10 minutes)
2. Check logs for any errors
3. Test health endpoint
4. Proceed with frontend deployment to Vercel

---

**Go to the settings page now and add these variables!**
https://huggingface.co/spaces/Ubushra/todo-chatbot-backend/settings
