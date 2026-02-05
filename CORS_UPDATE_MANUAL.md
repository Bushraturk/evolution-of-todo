# CORS Update Instructions for Hugging Face Spaces

## You Need to Manually Update CORS

Since I cannot directly modify environment variables on Hugging Face Spaces, you need to do this manually.

---

## Step 1: Update Main Backend CORS

1. **Open:** https://huggingface.co/spaces/Ubushra/todo-app-backend/settings

2. **Click:** "Variables and secrets" tab

3. **Find:** `CORS_ORIGINS` variable

4. **Click:** Edit (pencil icon)

5. **Update value to:**
   ```
   https://frontend-mauve-iota-87.vercel.app,http://localhost:3000
   ```

6. **Click:** Save

7. **Restart Space:**
   - Go back to main Space page
   - Click three dots menu (⋮)
   - Click "Restart Space"
   - Wait 1-2 minutes

---

## Step 2: Update Chatbot Backend CORS

1. **Open:** https://huggingface.co/spaces/Ubushra/todo-chatbot-backend/settings

2. **Click:** "Variables and secrets" tab

3. **Find:** `CORS_ORIGINS` variable

4. **Click:** Edit (pencil icon)

5. **Update value to:**
   ```
   https://frontend-mauve-iota-87.vercel.app,http://localhost:3000
   ```

6. **Click:** Save

7. **Restart Space:**
   - Go back to main Space page
   - Click three dots menu (⋮)
   - Click "Restart Space"
   - Wait 1-2 minutes

---

## ⏱️ Time Required

- Main Backend CORS: 2 minutes
- Chatbot Backend CORS: 2 minutes
- Total: 4 minutes

---

## ✅ After CORS Update

Test your deployment:

1. **Open:** https://frontend-mauve-iota-87.vercel.app
2. **Register/Login**
3. **Add a task** - Should work ✅
4. **Click purple robot icon** 🤖 (bottom-right)
5. **Send:** "Add a task to buy groceries"
6. **Verify:** Task appears in main list ✅

---

## 🎯 Final Production URLs

```
Frontend:        https://frontend-mauve-iota-87.vercel.app
Main Backend:    https://ubushra-todo-app-backend.hf.space
Chatbot Backend: https://ubushra-todo-chatbot-backend.hf.space
Database:        Neon DB
```

---

**Please update CORS on both backends now. It will take only 4 minutes!**

After updating, tell me: "CORS updated" and I'll help you test everything.
