# Quick Start Guide - AI Chatbot Integration

## 🚀 Start Everything

### Terminal 1: Backend (Phase IV Chatbot)
```bash
cd C:\Users\admin\Desktop\b-todo-app\evolution-of-todo\phase4-chatbot\backend
uvicorn src.main:app --reload --port 8000
```

### Terminal 2: Frontend
```bash
cd C:\Users\admin\Desktop\b-todo-app\evolution-of-todo\frontend
npm run dev
```

## 🧪 Test the Chatbot

1. Open browser: http://localhost:3000
2. Login with your account
3. Look for **purple robot icon** in bottom-right corner
4. Hover to see "AI Chatbot" tooltip
5. Click to open chat modal
6. Try these commands:

```
"Add a task to buy groceries"
"Show me all my tasks"
"What's pending?"
"Mark task 1 as complete"
"Change task 1 to 'Buy groceries and fruits'"
"Delete task 2"
```

## ✅ What to Expect

### Floating Button
- Purple gradient circle with robot icon
- Pulse animation
- Bottom-right corner
- Hover shows tooltip

### Chat Modal
- Opens on click
- Purple header with "AI Todo Assistant"
- Chat interface with message bubbles
- Input field at bottom
- Close with X, Escape, or backdrop click

### AI Responses
- Creates tasks from natural language
- Lists your tasks
- Completes tasks
- Updates tasks
- Deletes tasks
- Maintains conversation context

## 🐛 If Something Doesn't Work

### Backend not starting?
```bash
cd phase4-chatbot/backend
pip install -r requirements.txt
# Check if .env file exists with DATABASE_URL and OPENAI_API_KEY
```

### Frontend not starting?
```bash
cd frontend
npm install
# Check if .env.local exists
```

### Button not showing?
- Clear browser cache
- Check browser console for errors
- Verify you're logged in

### Chat not working?
- Check backend is running on port 8000
- Verify you're authenticated
- Check browser console for errors

## 📱 Mobile Testing

Open on mobile browser:
- Button should be visible
- Modal should be full screen
- Touch interactions should work

## 🎯 Success Criteria

- ✅ Backend running without errors
- ✅ Frontend running without errors
- ✅ Can login to dashboard
- ✅ Robot icon visible and clickable
- ✅ Modal opens and closes smoothly
- ✅ Can send messages and get responses
- ✅ Tasks are created via natural language
- ✅ Conversation persists

---

**Ready to use!** 🎉
