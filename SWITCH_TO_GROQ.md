# 🚀 Fix Chatbot - Switch to Groq (FREE & Reliable)

**Issue**: Gemini requires complex `thought_signature` for function calling
**Solution**: Switch to Groq - FREE, fast, and simple function calling
**Time**: 3-5 minutes

---

## Why Groq?

✅ **Completely FREE** - No credit card required
✅ **Fast inference** - 280 tokens/second
✅ **Simple function calling** - No thought_signature complexity
✅ **OpenAI-compatible** - Works with existing code
✅ **Reliable** - Stable and well-tested

---

## 🎯 Quick Setup

### Step 1: Get Groq API Key (FREE)

1. **Go to Groq Console:**
   ```
   https://console.groq.com/keys
   ```

2. **Sign up / Login:**
   - Use Google, GitHub, or email
   - No credit card required

3. **Create API Key:**
   - Click "Create API Key"
   - Give it a name (e.g., "Todo Chatbot")
   - Copy the key (starts with `gsk_...`)

### Step 2: Update Hugging Face Space Environment Variables

1. **Open your Space settings:**
   ```
   https://huggingface.co/spaces/Ubushra/todo-chatbot-backend/settings
   ```

2. **Click "Variables and secrets"** (left sidebar)

3. **Delete OLD Gemini variables:**
   - `GEMINI_API_KEY` → Delete
   - `GEMINI_BASE_URL` → Delete
   - `GEMINI_MODEL` → Delete

4. **Add NEW Groq variables:**

   Click "New variable" for each:

   **Variable 1:**
   - Name: `GROQ_API_KEY`
   - Value: `gsk_...` (your API key from Step 1)
   - Click "Save"

   **Variable 2:**
   - Name: `GROQ_BASE_URL`
   - Value: `https://api.groq.com/openai/v1`
   - Click "Save"

   **Variable 3:**
   - Name: `GROQ_MODEL`
   - Value: `llama-3.3-70b-versatile`
   - Click "Save"

5. **Verify other required variables exist:**
   - `DATABASE_URL` - Your Neon PostgreSQL connection
   - `JWT_SECRET` - Must match main backend
   - `CORS_ORIGINS` - Your frontend URLs

### Step 3: Trigger Rebuild

**Option A: Sync from GitHub (Recommended)**
- In Space settings, look for "Repository" section
- Click "Sync from GitHub" or "Rebuild"
- Wait 3-5 minutes

**Option B: Manual Restart**
- The Space will auto-restart after saving variables
- Wait 2-3 minutes

### Step 4: Verify the Fix

**Test 1: Health Check**
```bash
curl https://ubushra-todo-chatbot-backend.hf.space/health
```

Expected:
```json
{
  "status": "healthy",
  "service": "todo-chatbot",
  "llm": "llama-3.3-70b-versatile"
}
```

**Test 2: Chatbot**
1. Open: https://frontend-mauve-iota-87.vercel.app
2. Login
3. Click purple robot icon 🤖
4. Test: "update task namaz isha to namaz asar"
5. Expected: ✅ Task updated successfully

---

## 📊 Environment Variables Summary

### Required Variables (Groq Configuration)

| Variable | Value | Description |
|----------|-------|-------------|
| `GROQ_API_KEY` | `gsk_...` | Your Groq API key (FREE) |
| `GROQ_BASE_URL` | `https://api.groq.com/openai/v1` | Groq OpenAI-compatible endpoint |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Llama 3.3 70B model |
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

## 🔍 Why We Switched from Gemini

**Gemini Issues:**
- ❌ Requires `thought_signature` for function calling (complex)
- ❌ Different model names for OpenAI-compatible endpoint
- ❌ More complex error handling
- ❌ Frequent API changes

**Groq Benefits:**
- ✅ Simple function calling (standard OpenAI format)
- ✅ Consistent model names
- ✅ Completely free with generous limits
- ✅ Very fast inference (280 tokens/sec)
- ✅ Stable API

---

## 📝 Available Groq Models

| Model | Speed | Context | Best For |
|-------|-------|---------|----------|
| `llama-3.3-70b-versatile` | 280 tok/s | 131K | **Recommended** - Best balance |
| `llama-3.1-8b-instant` | 560 tok/s | 131K | Faster, less capable |
| `groq/compound` | 450 tok/s | 131K | Built-in tools (web search, code) |

**Current Setup:** Using `llama-3.3-70b-versatile` (best for function calling)

---

## ✅ Success Criteria

After deployment, you should see:
- ✅ No "thought_signature" errors
- ✅ No "model not found" errors
- ✅ Chatbot responds to all commands
- ✅ Tasks can be created, updated, completed, deleted
- ✅ Health check returns `"llm": "llama-3.3-70b-versatile"`

---

## 🆘 Troubleshooting

### Error: "Invalid API key"
- Verify your Groq API key starts with `gsk_`
- Check it's copied correctly (no extra spaces)
- Regenerate key if needed at https://console.groq.com/keys

### Error: "Connection refused"
- Check `GROQ_BASE_URL` is exactly: `https://api.groq.com/openai/v1`
- Don't add extra slashes or modify the URL

### Error: "Model not found"
- Verify `GROQ_MODEL` is exactly: `llama-3.3-70b-versatile`
- Check for typos (no spaces, correct hyphens)

### Space won't restart
- Go to Space settings → "Factory reboot"
- Wait 3-5 minutes
- Check logs for build errors

### Rate limit errors
- Groq has generous free limits (14,400 requests/day)
- If you hit limits, wait a few minutes
- Consider upgrading to paid plan for higher limits

---

## 📈 Groq Free Tier Limits

- **Requests per day**: 14,400
- **Requests per minute**: 30
- **Tokens per minute**: 7,000
- **Cost**: $0 (completely free)

**More than enough for personal projects!**

---

## 🎉 What's Fixed

**Files Updated:**
- ✅ `agent_service.py` - Groq client initialization
- ✅ `chat.py` - Groq configuration
- ✅ `config.py` - Groq settings
- ✅ `main.py` - Health check model name
- ✅ `.env.example` - Groq environment variables
- ✅ `DEPLOYMENT.md` - Groq deployment guide

**Commit:** Ready to push ✅

---

**Next Action:** Update environment variables in Hugging Face Space
**URL:** https://huggingface.co/spaces/Ubushra/todo-chatbot-backend/settings
**Time Required:** 3-5 minutes
**Difficulty:** Easy
**Cost:** FREE (no credit card needed)
