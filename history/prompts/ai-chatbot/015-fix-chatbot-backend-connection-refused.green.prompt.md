---
id: 015
title: Fix Chatbot Backend Connection Refused Error
stage: green
date: 2026-02-04
surface: agent
model: claude-opus-4-5-20251101
feature: ai-chatbot
branch: 004-ai-chatbot
user: admin
command: none
labels: ["troubleshooting", "backend", "connection-error", "phase4-chatbot", "server-startup"]
links:
  spec: specs/004-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - CHATBOT_TESTING_GUIDE.md
tests:
  - Server health check (all 3 servers: PASS)
  - Port verification (8001, 8002, 3000: PASS)
  - Database connection (PASS)
---

## Prompt

mane server band kar phir say start ab yahi error ha Hmmm… can't reach this page
127.0.0.1 refused to connect.
ERR_CONNECTION_REFUSED

## Response snapshot

**Problem Identified:**
User stopped and restarted servers, but the chatbot backend (port 8002) was not running, causing ERR_CONNECTION_REFUSED when trying to access the application.

**Root Cause:**
After stopping all servers, only the main backend (8001) and frontend (3000) were restarted. The chatbot backend (8002) was not started, causing the frontend to fail when trying to connect to the chat API.

**Diagnosis Process:**
1. Checked port status with `netstat` - confirmed 8002 not listening
2. Verified Python processes running - found 3 Python processes but none on 8002
3. Confirmed ports 8001 and 3000 were running correctly
4. Started chatbot backend manually from correct directory

**Solution Implemented:**
1. Started chatbot backend using: `python -m uvicorn src.main:app --port 8002`
2. Verified all three servers running with health checks
3. Confirmed all ports listening (8001, 8002, 3000)
4. Created comprehensive testing guide

**Verification Results:**
- ✓ Main Backend (8001): {"status":"healthy"}
- ✓ Chatbot Backend (8002): {"status":"healthy","service":"todo-chatbot","llm":"gemini-2.0-flash-exp","framework":"openai-agents-sdk"}
- ✓ Frontend (3000): Running and serving pages
- ✓ All ports confirmed listening via netstat

**Testing Guide Created:**
Comprehensive guide with:
- Step-by-step testing instructions
- 6 test scenarios for chatbot functionality
- Troubleshooting tips
- Quick commands for server management

## Outcome

- ✅ Impact: All three servers now running successfully. User can access the application and test the chatbot functionality.
- 🧪 Tests: Health checks PASS for all servers, port verification PASS, database connection PASS
- 📁 Files: Created CHATBOT_TESTING_GUIDE.md with comprehensive testing instructions
- 🔁 Next prompts: Test chatbot functionality end-to-end, commit Phase IV work if tests pass, or proceed with deployment
- 🧠 Reflection: The issue was simply that the chatbot backend wasn't started after the restart. The START_ALL_SERVERS.bat script should handle this automatically, but manual restart requires starting all three servers individually. The testing guide will help verify the chatbot works correctly before committing or deploying.

## Evaluation notes (flywheel)

- Failure modes observed: User manually restarted servers but forgot to start chatbot backend (port 8002)
- Graders run and results (PASS/FAIL): Health check PASS, Port verification PASS, Database connection PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Have user test the chatbot with actual interactions to verify the full agent loop and MCP tools work correctly
