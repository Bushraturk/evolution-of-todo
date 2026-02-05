# Vercel Environment Variables Update

## Required Environment Variables for Production

Go to: https://vercel.com/ahmed-raza-turks-projects/frontend/settings/environment-variables

### Update/Add These Variables:

1. **NEXT_PUBLIC_API_URL**
   - Value: `https://ubushra-todo-app-backend.hf.space`
   - Environment: Production

2. **NEXT_PUBLIC_CHAT_API_URL**
   - Value: `https://ubushra-todo-chatbot-backend.hf.space`
   - Environment: Production

3. **NEXT_PUBLIC_AUTH_URL**
   - Value: `https://frontend-mauve-iota-87.vercel.app`
   - Environment: Production

After updating, click "Redeploy" on the latest deployment.

---

## CORS Update for Main Backend

The main backend needs to allow requests from the Vercel URL.

**Main Backend Space:** https://huggingface.co/spaces/Ubushra/todo-app-backend/settings

Update `CORS_ORIGINS` environment variable to:
```
https://frontend-mauve-iota-87.vercel.app,http://localhost:3000
```

Then restart the Space.

---

## Quick Commands

### Update Vercel Env Vars via CLI:
```bash
cd frontend
vercel env add NEXT_PUBLIC_AUTH_URL production
# Enter: https://frontend-mauve-iota-87.vercel.app

vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://ubushra-todo-app-backend.hf.space

vercel env add NEXT_PUBLIC_CHAT_API_URL production
# Enter: https://ubushra-todo-chatbot-backend.hf.space
```

### Redeploy:
```bash
vercel --prod
```
