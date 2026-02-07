# 🚨 Fix Gemini Deployment Error

**Error**: `Error code: 400 - unexpected model name format`
**Cause**: Hugging Face Space has old Groq environment variables, but code uses Gemini
**Fix**: Update environment variables to Gemini configuration
**Time**: 3-5 minutes

---

## 🎯 Quick Fix Steps

### Step 1: Get Your Gemini API Key

1. **Go to Google AI Studio:**
   ```
   https://aistudio.google.com/app/apikey
   ```

2. **Create API Key:**
   - Click "Create API Key"
   - Select a Google Cloud project (or create new)
   - Copy the API key (starts with `AIzaSy...`)

### Step 2: Update Hugging Face Space Environment Variables

1. **Open your Space settings:**
   ```
   https://huggingface.co/spaces/Ubushra/todo-chatbot-backend/settings
   ```

2. **Click "Variables and secrets" (left sidebar)**

3. **Delete OLD Groq variables (if they exist):**
   - `GROQ_API_KEY` - Click "Delete"
   - `GROQ_BASE_URL` - Click "Delete"
   - `GROQ_MODEL` - Click "Delete"

4. **Add NEW Gemini variables:**

   Click "New variable" for each:

   **Variable 1:**
   - Name: `GEMINI_API_KEY`
   - Value: `AIzaSy...` (your API key from Step 1)
   - Click "Save"

   **Variable 2:**
   - Name: `GEMINI_BASE_URL`
   - Value: `https://generativelanguage.googleapis.com/v1beta/openai/`
   - Click "Save"

   **Variable 3:**
   - Name: `GEMINI_MODEL`
   - Value: `gemini-3-flash-preview`
   - Click "Save"

5. **Verify other required variables exist:**
   - `DATABASE_URL` - Your Neon PostgreSQL connection string
   - `JWT_SECRET` - Must match your main backend
   - `CORS_ORIGINS` - Your frontend URLs

### Step 3: Restart the Space

1. **The Space will auto-restart after saving variables**
2. **Wait 2-3 minutes for rebuild**
3. **Check "Logs" tab for any errors**

### Step 4: Verify the Fix

**Test 1: Health Check**
```bash
curl https://ubushra-todo-chatbot-backend.hf.space/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "todo-chatbot",
  "llm": "gemini-3-flash-preview"
}
```

**Test 2: Chatbot Functionality**

1. Open: https://frontend-mauve-iota-87.vercel.app
2. Login to your account
3. Click purple robot icon 🤖
4. Send: "update task namaz isha to namaz asar"
5. Expected: Task updated successfully ✅

---

## 📊 Environment Variables Summary

### Required Variables (Gemini Configuration)

| Variable | Value | Description |
|----------|-------|-------------|
| `GEMINI_API_KEY` | `AIzaSy...` | Your Google Gemini API key |
| `GEMINI_BASE_URL` | `https://generativelanguage.googleapis.com/v1beta/openai/` | Gemini OpenAI-compatible endpoint |
| `GEMINI_MODEL` | `gemini-3-flash-preview` | Gemini model name |
| `DATABASE_URL` | `postgresql://...` | Neon DB connection string |
| `JWT_SECRET` | `your-secret` | Must match main backend |
| `CORS_ORIGINS` | `http://localhost:3000,...` | Allowed frontend origins |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_CONVERSATION_HISTORY` | `50` | Messages to load per conversation |
| `CONVERSATION_ARCHIVE_DAYS` | `90` | Days before archiving |
| `LLM_REQUEST_TIMEOUT` | `30` | API timeout in seconds |
| `LLM_MAX_RETRIES` | `3` | Max retry attempts |
| `DEBUG` | `false` | Enable debug logging |
| `LOG_LEVEL` | `INFO` | Logging level |

---

## 🔍 Why This Happened

**Timeline:**
1. ✅ Originally used Gemini
2. ❌ Switched to Groq (commit 33f24f1)
3. ❌ Groq had function calling issues
4. ✅ Switched back to Gemini (commit 40ef1c3)
5. ❌ **Forgot to update HF Space environment variables**

**The Fix:**
- Code now uses Gemini (correct)
- Environment variables updated to match (this fix)

---

## ✅ Success Criteria

After deployment, you should see:
- ✅ No "unexpected model name format" errors
- ✅ Chatbot responds to all commands
- ✅ Tasks can be created, updated, completed, deleted
- ✅ Health check returns `"llm": "gemini-3-flash-preview"`

---

## 🆘 Troubleshooting

### Error: "API key not valid"
- Verify your Gemini API key is correct
- Check it starts with `AIzaSy`
- Regenerate key if needed at https://aistudio.google.com/app/apikey

### Error: "Connection refused"
- Check `GEMINI_BASE_URL` is exactly: `https://generativelanguage.googleapis.com/v1beta/openai/`
- Don't add extra slashes or modify the URL

### Error: "Model not found"
- Verify `GEMINI_MODEL` is exactly: `gemini-3-flash-preview`
- Check for typos (no spaces, correct hyphens)
- Alternative: Use `gemini-3-pro-preview` for more capable model

### Space won't restart
- Go to Space settings → "Factory reboot"
- Wait 3-5 minutes
- Check logs for build errors

---

## 📝 Next Steps After Fix

1. **Test all chatbot commands:**
   - Add task
   - List tasks
   - Complete task
   - Update task
   - Delete task

2. **Update frontend configuration:**
   - Ensure `NEXT_PUBLIC_CHAT_API_URL` points to HF Space
   - Verify CORS allows your frontend domain

3. **Clean up old documentation:**
   - Delete `DEPLOY_GROQ_FIX_NOW.md`
   - Delete `FIX_GROQ_MODEL.md`
   - Delete `test-groq-fix.sh`

4. **Commit changes:**
   - Commit updated `.env.example`
   - Commit this deployment guide

---

**Next Action:** Update environment variables in Hugging Face Space
**URL:** https://huggingface.co/spaces/Ubushra/todo-chatbot-backend/settings
**Time Required:** 3-5 minutes
**Difficulty:** Easy
