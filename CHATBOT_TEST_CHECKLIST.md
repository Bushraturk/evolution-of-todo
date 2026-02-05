# Chatbot Testing Checklist - Phase IV

**Date:** 2026-02-01
**Status:** Ready for Testing

## Prerequisites
- ✅ All servers running (8001, 8002, 3000)
- ✅ UUID conversion bugs fixed
- ✅ Database connected
- ✅ Gemini API configured

---

## Test Environment
- **Frontend:** http://localhost:3000
- **Main Backend:** http://localhost:8001
- **Chatbot Backend:** http://localhost:8002

---

## Testing Instructions

### Before You Start
1. Open browser and go to http://localhost:3000
2. Login with your account
3. Open Browser Console (F12) to see any errors
4. Click the purple robot icon (🤖) in bottom-right corner

---

## User Story 1: Create Task via Chat

**Command:**
```
Add a task to buy groceries
```

**Expected Result:**
- [ ] Chatbot responds with confirmation
- [ ] Response includes: "I've created a task titled 'Buy groceries'"
- [ ] Task appears in main task list
- [ ] Tool call shown: `add_task`
- [ ] No errors in console

**Actual Result:**
```
[Write what actually happened]
```

**Status:** ⬜ Pass / ⬜ Fail

---

## User Story 2: List Tasks via Chat

**Command:**
```
Show me all my tasks
```

**Expected Result:**
- [ ] Chatbot lists all tasks
- [ ] Shows task titles and status (pending/completed)
- [ ] Tool call shown: `list_tasks`
- [ ] Count matches actual task list

**Actual Result:**
```
[Write what actually happened]
```

**Status:** ⬜ Pass / ⬜ Fail

---

## User Story 3: Complete Task via Chat

**Command:**
```
Mark task 1 as complete
```

**Expected Result:**
- [ ] Chatbot confirms task completion
- [ ] Task shows as completed in main list
- [ ] Tool call shown: `complete_task`
- [ ] Task has checkmark or strikethrough

**Actual Result:**
```
[Write what actually happened]
```

**Status:** ⬜ Pass / ⬜ Fail

---

## User Story 4: Maintain Conversation Context

**Test Sequence:**
```
1. "Add a task to buy milk"
2. "Also add eggs"
3. "And bread too"
4. "Show me what I just added"
```

**Expected Result:**
- [ ] First message creates "Buy milk" task
- [ ] Second message creates "Buy eggs" (understands "also")
- [ ] Third message creates "Buy bread" (understands context)
- [ ] Fourth message lists the 3 new tasks
- [ ] Conversation flows naturally

**Actual Result:**
```
[Write what actually happened]
```

**Status:** ⬜ Pass / ⬜ Fail

---

## User Story 5: Update Task via Chat

**Command:**
```
Change task 1 to 'Buy groceries and fruits'
```

**Expected Result:**
- [ ] Chatbot confirms update
- [ ] Task title changes in main list
- [ ] Tool call shown: `update_task`
- [ ] Change persists after refresh

**Actual Result:**
```
[Write what actually happened]
```

**Status:** ⬜ Pass / ⬜ Fail

---

## User Story 6: Delete Task via Chat

**Command:**
```
Delete task 2
```

**Expected Result:**
- [ ] Chatbot confirms deletion
- [ ] Task disappears from main list
- [ ] Tool call shown: `delete_task`
- [ ] Deletion persists after refresh

**Actual Result:**
```
[Write what actually happened]
```

**Status:** ⬜ Pass / ⬜ Fail

---

## Additional Tests

### Test 7: Conversation Persistence
1. Send a few messages
2. Close browser completely
3. Reopen and login
4. Open chatbot

**Expected:** Previous conversation visible

**Status:** ⬜ Pass / ⬜ Fail

---

### Test 8: Error Handling
**Command:**
```
Delete task 999
```

**Expected:** Graceful error message (task not found)

**Status:** ⬜ Pass / ⬜ Fail

---

### Test 9: Natural Language Variations

Try these variations:
- "I need to remember to call mom"
- "What's on my todo list?"
- "I finished task 3"
- "Remove the meeting task"

**Expected:** Chatbot understands variations

**Status:** ⬜ Pass / ⬜ Fail

---

## Summary

**Total Tests:** 9
**Passed:** ___
**Failed:** ___
**Success Rate:** ___%

---

## Issues Found

1.
2.
3.

---

## Notes

[Add any observations, suggestions, or comments here]

---

**Tested By:** _______________
**Date:** _______________
**Time:** _______________
