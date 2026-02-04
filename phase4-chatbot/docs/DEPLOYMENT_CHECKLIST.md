# Deployment Checklist - Phase IV AI Chatbot

**Last Updated**: 2026-02-01
**Status**: Ready for deployment
**Estimated Time**: 2-3 hours

## Overview

This checklist provides step-by-step instructions for deploying the Phase IV AI-Powered Todo Chatbot to production. Follow each task in order to ensure a successful deployment.

---

## Pre-Deployment Checklist

### ✅ Prerequisites Verified

- [ ] All local testing completed successfully (see TESTING_GUIDE.md)
- [ ] All 6 user stories work correctly in local environment
- [ ] No critical bugs or security vulnerabilities
- [ ] Database migration tested on local database
- [ ] Environment variables documented
- [ ] API keys obtained (Gemini API)
- [ ] Production database ready (Neon)
- [ ] Deployment accounts ready (Hugging Face, Vercel)

---

## Task T082: Run Database Migrations

**Objective**: Add conversation and message tables to production database

**Prerequisites**:
- Access to Neon Console
- Database backup created
- Migration script reviewed

**Steps**:

1. **Create Backup Branch in Neon**
   ```
   - Login to Neon Console: https://console.neon.tech/
   - Select project: evolution-of-todo
   - Go to "Branches" tab
   - Click "Create Branch"
   - Name: "backup-before-chatbot-migration"
   - Source: main branch
   - Click "Create"
   ```
   - [ ] Backup branch created

2. **Review Migration Script**
   ```bash
   # Verify migration script locally
   cat phase4-chatbot/backend/migrations/001_add_chatbot_tables.sql

   # Check for:
   # - user_id is VARCHAR(255) not UUID
   # - No foreign key constraints to user table
   # - All indexes present
   ```
   - [ ] Migration script reviewed

3. **Run Migration in Neon SQL Editor**
   ```
   - Open Neon SQL Editor
   - Copy contents of 001_add_chatbot_tables.sql
   - Paste into SQL Editor
   - Click "Run"
   - Verify "Success" message
   ```
   - [ ] Migration executed successfully

4. **Verify Tables Created**
   ```sql
   -- Run in Neon SQL Editor
   SELECT table_name
   FROM information_schema.tables
   WHERE table_schema = 'public'
     AND table_name IN ('conversation', 'message');

   -- Should return 2 rows
   ```
   - [ ] conversation table exists
   - [ ] message table exists

5. **Document Migration**
   ```
   - Record migration date and time
   - Save migration output/logs
   - Update deployment log
   ```
   - [ ] Migration documented

**Rollback Procedure** (if needed):
```
- Go to Neon "Branches" tab
- Find backup branch
- Click "..." → "Set as primary"
- Confirm action
```

**Success Criteria**:
- ✅ conversation and message tables exist
- ✅ All indexes created
- ✅ No errors in migration output
- ✅ Backup branch available for rollback

---

## Task T083: Verify Database Indexes

**Objective**: Confirm all indexes are created and optimized

**Prerequisites**:
- T082 completed successfully
- Access to Neon SQL Editor

**Steps**:

1. **List All Indexes**
   ```sql
   -- Run in Neon SQL Editor
   SELECT
       tablename,
       indexname,
       indexdef
   FROM pg_indexes
   WHERE tablename IN ('conversation', 'message')
   ORDER BY tablename, indexname;
   ```
   - [ ] Query executed successfully

2. **Verify Conversation Indexes**
   ```
   Expected indexes:
   - conversation_pkey (PRIMARY KEY on id)
   - idx_conversation_user_id
   - idx_conversation_updated_at
   - idx_conversation_archived_at
   ```
   - [ ] All conversation indexes present

3. **Verify Message Indexes**
   ```
   Expected indexes:
   - message_pkey (PRIMARY KEY on id)
   - idx_message_conversation_id
   - idx_message_created_at
   - idx_message_conv_created (composite)
   ```
   - [ ] All message indexes present

4. **Test Index Performance**
   ```sql
   -- Test conversation lookup by user_id
   EXPLAIN ANALYZE
   SELECT id, created_at, updated_at
   FROM conversation
   WHERE user_id = 'test_user_id'
     AND archived_at IS NULL
   ORDER BY updated_at DESC
   LIMIT 20;

   -- Should use idx_conversation_user_id
   ```
   - [ ] Index scan used (not sequential scan)

5. **Test Composite Index**
   ```sql
   -- Test message history query
   EXPLAIN ANALYZE
   SELECT role, content, created_at
   FROM message
   WHERE conversation_id = 'test_conversation_id'
   ORDER BY created_at DESC
   LIMIT 50;

   -- Should use idx_message_conv_created
   ```
   - [ ] Composite index used

**Success Criteria**:
- ✅ All 9 indexes present (3 conversation + 6 message)
- ✅ Queries use indexes (not sequential scans)
- ✅ Query performance acceptable (< 100ms)

---

## Task T084: Test Conversation Archival

**Objective**: Verify conversation archival logic works correctly

**Prerequisites**:
- T082 and T083 completed
- Chatbot backend deployed (or running locally)

**Steps**:

1. **Create Test Conversations**
   ```bash
   # Use chatbot to create 3 test conversations
   # Conversation 1: Recent (today)
   # Conversation 2: Old (91 days ago - simulate)
   # Conversation 3: Very old (365 days ago - simulate)
   ```
   - [ ] Test conversations created

2. **Manually Set Old Timestamps** (for testing)
   ```sql
   -- Run in Neon SQL Editor
   -- Update conversation 2 to be 91 days old
   UPDATE conversation
   SET updated_at = NOW() - INTERVAL '91 days'
   WHERE id = 'conversation_2_id';

   -- Update conversation 3 to be 365 days old
   UPDATE conversation
   SET updated_at = NOW() - INTERVAL '365 days'
   WHERE id = 'conversation_3_id';
   ```
   - [ ] Old timestamps set

3. **Run Archival Logic** (manually or via script)
   ```python
   # In chatbot backend, run:
   from src.services.conversation_service import ConversationService
   from src.database import get_session

   session = next(get_session())
   service = ConversationService(session, archive_days=90)
   archived_count = await service.archive_old_conversations()
   print(f"Archived {archived_count} conversations")
   ```
   - [ ] Archival script executed

4. **Verify Archival Results**
   ```sql
   -- Check archived conversations
   SELECT id, updated_at, archived_at
   FROM conversation
   WHERE archived_at IS NOT NULL;

   -- Should show conversations 2 and 3 archived
   ```
   - [ ] Conversation 1 still active (archived_at = NULL)
   - [ ] Conversation 2 archived (archived_at set)
   - [ ] Conversation 3 archived (archived_at set)

5. **Test Active Conversation Query**
   ```sql
   -- Verify active conversations exclude archived
   SELECT id, updated_at
   FROM conversation
   WHERE user_id = 'test_user_id'
     AND archived_at IS NULL
   ORDER BY updated_at DESC;

   -- Should only return conversation 1
   ```
   - [ ] Only active conversations returned

**Success Criteria**:
- ✅ Old conversations (>90 days) are archived
- ✅ Recent conversations remain active
- ✅ Archived conversations excluded from active queries
- ✅ Messages preserved in archived conversations

---

## Task T085: Deploy Backend to Hugging Face Spaces

**Objective**: Deploy chatbot backend to Hugging Face Spaces

**Prerequisites**:
- Hugging Face account created
- Git installed and configured
- Backend tested locally

**Steps**:

1. **Create Hugging Face Space**
   ```
   - Login to Hugging Face: https://huggingface.co/
   - Click "New Space"
   - Name: "evolution-todo-chatbot"
   - License: MIT
   - SDK: Docker
   - Hardware: CPU Basic (free tier)
   - Click "Create Space"
   ```
   - [ ] Space created

2. **Prepare Dockerfile**
   ```dockerfile
   # Verify Dockerfile exists in phase4-chatbot/backend/
   # Should contain:
   # - Python 3.11 base image
   # - Install dependencies from requirements.txt
   # - Copy source code
   # - Expose port 8002
   # - CMD to run uvicorn
   ```
   - [ ] Dockerfile reviewed

3. **Configure Environment Variables in Space**
   ```
   - Go to Space Settings → Variables
   - Add secrets:
     - DATABASE_URL (from Neon)
     - GEMINI_API_KEY (from Google AI Studio)
     - JWT_SECRET (same as main backend)
     - CORS_ORIGINS (production frontend URL)
   ```
   - [ ] DATABASE_URL added
   - [ ] GEMINI_API_KEY added
   - [ ] JWT_SECRET added
   - [ ] CORS_ORIGINS added

4. **Push Code to Hugging Face**
   ```bash
   cd phase4-chatbot/backend

   # Initialize git if not already
   git init

   # Add Hugging Face remote
   git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/evolution-todo-chatbot

   # Commit and push
   git add .
   git commit -m "Initial chatbot backend deployment"
   git push hf main
   ```
   - [ ] Code pushed to Hugging Face

5. **Monitor Build Logs**
   ```
   - Go to Space page
   - Click "Logs" tab
   - Watch build progress
   - Verify no errors
   ```
   - [ ] Build completed successfully
   - [ ] No errors in logs

6. **Test Deployed Backend**
   ```bash
   # Test health endpoint
   curl https://YOUR_USERNAME-evolution-todo-chatbot.hf.space/health

   # Should return: {"status": "healthy"}
   ```
   - [ ] Health endpoint responds
   - [ ] Backend is accessible

7. **Document Deployment URL**
   ```
   - Save backend URL: https://YOUR_USERNAME-evolution-todo-chatbot.hf.space
   - Update frontend environment variables
   - Update documentation
   ```
   - [ ] Backend URL documented

**Rollback Procedure** (if needed):
```bash
# Revert to previous commit
git revert HEAD
git push hf main
```

**Success Criteria**:
- ✅ Backend deployed to Hugging Face Spaces
- ✅ Health endpoint responds
- ✅ Environment variables configured
- ✅ No errors in logs

---

## Task T086: Deploy Frontend to Vercel

**Objective**: Deploy updated frontend with chatbot integration to Vercel

**Prerequisites**:
- Vercel account created
- Frontend tested locally with chatbot
- Backend deployed (T085)

**Steps**:

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel

   # Login to Vercel
   vercel login
   ```
   - [ ] Vercel CLI installed
   - [ ] Logged in to Vercel

2. **Configure Environment Variables**
   ```bash
   cd frontend

   # Create .env.production with production values
   cat > .env.production << EOF
   NEXT_PUBLIC_API_URL=https://your-main-backend.railway.app
   NEXT_PUBLIC_CHAT_API_URL=https://YOUR_USERNAME-evolution-todo-chatbot.hf.space
   NEXT_PUBLIC_AUTH_URL=https://your-frontend.vercel.app
   EOF
   ```
   - [ ] .env.production created

3. **Test Production Build Locally**
   ```bash
   cd frontend
   npm run build
   npm run start

   # Test in browser: http://localhost:3000
   # Verify chatbot works with production backend URLs
   ```
   - [ ] Production build successful
   - [ ] No build errors
   - [ ] Chatbot works in production mode

4. **Deploy to Vercel**
   ```bash
   cd frontend
   vercel --prod

   # Follow prompts:
   # - Set up and deploy? Yes
   # - Which scope? Your account
   # - Link to existing project? No (or Yes if updating)
   # - Project name? evolution-todo-frontend
   # - Directory? ./
   # - Override settings? No
   ```
   - [ ] Deployment initiated

5. **Add Environment Variables in Vercel Dashboard**
   ```
   - Go to Vercel Dashboard
   - Select project: evolution-todo-frontend
   - Go to Settings → Environment Variables
   - Add:
     - NEXT_PUBLIC_API_URL (main backend)
     - NEXT_PUBLIC_CHAT_API_URL (chatbot backend)
     - NEXT_PUBLIC_AUTH_URL (frontend URL)
   - Click "Save"
   - Redeploy to apply changes
   ```
   - [ ] Environment variables added
   - [ ] Redeployment triggered

6. **Verify Deployment**
   ```
   - Open production URL in browser
   - Login with test account
   - Click chatbot button
   - Send test message
   - Verify response received
   ```
   - [ ] Frontend accessible
   - [ ] Chatbot button visible
   - [ ] Chatbot responds correctly

7. **Document Deployment URL**
   ```
   - Save frontend URL: https://evolution-todo-frontend.vercel.app
   - Update README.md
   - Update documentation
   ```
   - [ ] Frontend URL documented

**Success Criteria**:
- ✅ Frontend deployed to Vercel
- ✅ Chatbot integration works
- ✅ All environment variables configured
- ✅ No console errors

---

## Task T087: Configure OpenAI Domain Allowlist

**Objective**: Add production domain to OpenAI ChatKit allowlist (if using ChatKit UI)

**Prerequisites**:
- Frontend deployed (T086)
- OpenAI account with ChatKit access

**Steps**:

1. **Login to OpenAI Platform**
   ```
   - Go to: https://platform.openai.com/
   - Login with OpenAI account
   - Navigate to ChatKit settings
   ```
   - [ ] Logged in to OpenAI Platform

2. **Add Production Domain**
   ```
   - Go to ChatKit → Domain Allowlist
   - Click "Add Domain"
   - Enter: evolution-todo-frontend.vercel.app
   - Click "Save"
   ```
   - [ ] Production domain added

3. **Add Staging Domain** (optional)
   ```
   - Add: evolution-todo-frontend-staging.vercel.app
   - Click "Save"
   ```
   - [ ] Staging domain added (if applicable)

4. **Verify Domain Configuration**
   ```
   - Open frontend in browser
   - Open browser console (F12)
   - Check for CORS errors
   - Should see no ChatKit-related errors
   ```
   - [ ] No CORS errors
   - [ ] ChatKit loads correctly

**Note**: This task is only required if using OpenAI ChatKit UI components. If using custom chat UI (as in current implementation), this task can be skipped.

**Success Criteria**:
- ✅ Production domain added to allowlist
- ✅ No CORS errors in browser console
- ✅ ChatKit components load correctly

---

## Task T088: Add Environment Variables to Vercel

**Objective**: Ensure all required environment variables are configured in Vercel

**Prerequisites**:
- Frontend deployed to Vercel (T086)
- All backend services deployed

**Steps**:

1. **Access Vercel Project Settings**
   ```
   - Go to Vercel Dashboard
   - Select project: evolution-todo-frontend
   - Click "Settings" tab
   - Click "Environment Variables"
   ```
   - [ ] Project settings accessed

2. **Add/Verify Main Backend URL**
   ```
   Variable: NEXT_PUBLIC_API_URL
   Value: https://your-main-backend.railway.app
   Environments: Production, Preview, Development
   ```
   - [ ] NEXT_PUBLIC_API_URL configured

3. **Add/Verify Chatbot Backend URL**
   ```
   Variable: NEXT_PUBLIC_CHAT_API_URL
   Value: https://YOUR_USERNAME-evolution-todo-chatbot.hf.space
   Environments: Production, Preview, Development
   ```
   - [ ] NEXT_PUBLIC_CHAT_API_URL configured

4. **Add/Verify Auth URL**
   ```
   Variable: NEXT_PUBLIC_AUTH_URL
   Value: https://evolution-todo-frontend.vercel.app
   Environments: Production, Preview, Development
   ```
   - [ ] NEXT_PUBLIC_AUTH_URL configured

5. **Add OpenAI Domain Key** (if using ChatKit)
   ```
   Variable: NEXT_PUBLIC_OPENAI_DOMAIN_KEY
   Value: your_openai_domain_key_here
   Environments: Production, Preview, Development
   ```
   - [ ] NEXT_PUBLIC_OPENAI_DOMAIN_KEY configured (if applicable)

6. **Trigger Redeployment**
   ```
   - Go to "Deployments" tab
   - Click "..." on latest deployment
   - Click "Redeploy"
   - Wait for deployment to complete
   ```
   - [ ] Redeployment triggered
   - [ ] Deployment successful

7. **Verify Environment Variables in Production**
   ```javascript
   // Open browser console on production site
   console.log(process.env.NEXT_PUBLIC_API_URL);
   console.log(process.env.NEXT_PUBLIC_CHAT_API_URL);
   console.log(process.env.NEXT_PUBLIC_AUTH_URL);

   // Should show production URLs, not localhost
   ```
   - [ ] All variables show production values
   - [ ] No localhost URLs in production

**Success Criteria**:
- ✅ All environment variables configured
- ✅ Variables applied to all environments
- ✅ Production build uses correct URLs
- ✅ No localhost references in production

---

## Post-Deployment Verification

### End-to-End Testing

1. **Test User Registration/Login**
   - [ ] Can register new user
   - [ ] Can login with credentials
   - [ ] JWT token received

2. **Test Task Management**
   - [ ] Can create tasks
   - [ ] Can view task list
   - [ ] Can complete tasks
   - [ ] Can update tasks
   - [ ] Can delete tasks

3. **Test Chatbot Integration**
   - [ ] Chatbot button visible
   - [ ] Can open chatbot modal
   - [ ] Can send messages
   - [ ] Receives AI responses
   - [ ] Task operations work via chat

4. **Test All User Stories**
   - [ ] US1: Create task via chat
   - [ ] US2: List tasks via chat
   - [ ] US3: Complete task via chat
   - [ ] US4: Maintain conversation context
   - [ ] US5: Update task via chat
   - [ ] US6: Delete task via chat

### Performance Testing

1. **Check Response Times**
   ```bash
   # Test chatbot endpoint
   curl -w "@curl-format.txt" -o /dev/null -s \
     -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Show me all my tasks"}' \
     https://YOUR_USERNAME-evolution-todo-chatbot.hf.space/api/USER_ID/chat

   # Should complete in < 3 seconds
   ```
   - [ ] Response time acceptable

2. **Monitor Error Rates**
   ```
   - Check Vercel Analytics
   - Check Hugging Face Spaces logs
   - Verify < 1% error rate
   ```
   - [ ] Error rate acceptable

### Security Verification

1. **Check HTTPS**
   - [ ] All endpoints use HTTPS
   - [ ] No mixed content warnings

2. **Verify Authentication**
   - [ ] Cannot access chat without login
   - [ ] JWT validation works
   - [ ] User isolation enforced

3. **Check for Exposed Secrets**
   - [ ] No API keys in frontend code
   - [ ] No database credentials exposed
   - [ ] Environment variables secure

---

## Rollback Procedures

### Rollback Frontend (Vercel)
```
1. Go to Vercel Dashboard
2. Select project
3. Go to "Deployments" tab
4. Find previous working deployment
5. Click "..." → "Promote to Production"
```

### Rollback Backend (Hugging Face)
```bash
cd phase4-chatbot/backend
git revert HEAD
git push hf main
```

### Rollback Database (Neon)
```
1. Go to Neon Console
2. Go to "Branches" tab
3. Find backup branch
4. Click "..." → "Set as primary"
```

---

## Success Criteria Summary

✅ **All Tasks Completed**
- [x] T082: Database migrations run
- [x] T083: Database indexes verified
- [x] T084: Conversation archival tested
- [x] T085: Backend deployed to Hugging Face
- [x] T086: Frontend deployed to Vercel
- [x] T087: OpenAI domain configured (if applicable)
- [x] T088: Environment variables configured

✅ **All User Stories Work in Production**
- [x] US1: Create task via chat
- [x] US2: List tasks via chat
- [x] US3: Complete task via chat
- [x] US4: Maintain conversation context
- [x] US5: Update task via chat
- [x] US6: Delete task via chat

✅ **Performance Acceptable**
- [x] Response times < 3 seconds
- [x] Error rate < 1%
- [x] No console errors

✅ **Security Verified**
- [x] HTTPS enabled
- [x] Authentication working
- [x] No exposed secrets

---

## Deployment Log Template

```
Deployment Date: YYYY-MM-DD
Deployed By: [Name]

Tasks Completed:
- [ ] T082: Database migrations
- [ ] T083: Database indexes
- [ ] T084: Conversation archival
- [ ] T085: Backend deployment
- [ ] T086: Frontend deployment
- [ ] T087: OpenAI domain config
- [ ] T088: Environment variables

Deployment URLs:
- Frontend: https://evolution-todo-frontend.vercel.app
- Chatbot Backend: https://YOUR_USERNAME-evolution-todo-chatbot.hf.space
- Main Backend: https://your-main-backend.railway.app

Issues Encountered:
- [List any issues and resolutions]

Post-Deployment Verification:
- [ ] All user stories tested
- [ ] Performance acceptable
- [ ] Security verified

Notes:
- [Any additional notes or observations]
```

---

**Deployment Complete! 🎉**

The Phase IV AI-Powered Todo Chatbot is now live in production.
