# Deployment Guide - AI-Powered Todo Chatbot

**Last Updated**: 2026-02-01
**Status**: Ready for deployment

## Overview

This guide provides step-by-step instructions for deploying the AI-Powered Todo Chatbot to production. For detailed task-by-task instructions, see [DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md).

## Prerequisites

- Backend code complete and tested locally (see [TESTING_GUIDE.md](../../TESTING_GUIDE.md))
- Frontend code complete and tested locally
- Database migrations ready (see [DATABASE_MIGRATION.md](docs/DATABASE_MIGRATION.md))
- **Gemini API key** (from Google AI Studio, not OpenAI)
- Neon PostgreSQL database (or other PostgreSQL provider)
- GitHub repository with code
- Hugging Face account (for backend)
- Vercel account (for frontend)

## Deployment Architecture

```
┌─────────────────┐
│   Vercel        │
│   (Frontend)    │
│   Next.js App   │
└────────┬────────┘
         │
         │ HTTPS
         │
┌────────▼────────┐
│ Hugging Face    │
│ (Backend)       │
│ FastAPI + MCP   │
└────────┬────────┘
         │
         │ PostgreSQL
         │
┌────────▼────────┐
│   Neon DB       │
│   (Database)    │
│   PostgreSQL    │
└─────────────────┘
```

## Step 1: Database Setup (Neon PostgreSQL)

### 1.1 Create Database

1. Go to https://neon.tech
2. Create a new project
3. Copy the connection string

### 1.2 Run Migrations

**Important**: See [DATABASE_MIGRATION.md](docs/DATABASE_MIGRATION.md) for detailed migration instructions.

```bash
# Set your database URL
export DATABASE_URL="postgresql://user:password@host/database"

# Run migrations
psql $DATABASE_URL -f phase4-chatbot/backend/migrations/001_add_chatbot_tables.sql
```

**Note**: The migration uses `VARCHAR(255)` for `user_id` columns (not UUID) to match the main backend's Better Auth CUID format.

### 1.3 Verify Tables

```bash
psql $DATABASE_URL -c "\dt"
# Should show: conversation, message, user, task
```

## Step 2: Backend Deployment (Hugging Face Spaces)

### 2.1 Prepare Repository

1. Ensure Dockerfile exists in `phase4-chatbot/backend/`
2. Ensure all code is committed to Git
3. Push to GitHub

### 2.2 Create Hugging Face Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Choose:
   - Name: `todo-chatbot-backend`
   - License: Apache 2.0
   - SDK: Docker
   - Hardware: CPU Basic (free tier)

### 2.3 Configure Space

1. **Connect GitHub Repository**:
   - Settings → Repository → Connect GitHub
   - Select your repository
   - Set path: `phase4-chatbot/backend`

2. **Set Environment Variables**:
   - Settings → Variables and secrets
   - Add the following secrets:

   ```
   DATABASE_URL=postgresql://user:password@host/database
   GROQ_API_KEY=your-groq-api-key-here
   GROQ_BASE_URL=https://api.groq.com/openai/v1
   GROQ_MODEL=llama-3.3-70b-versatile
   JWT_SECRET=your-jwt-secret-key
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_DAYS=7
   CORS_ORIGINS=https://your-frontend.vercel.app
   DEBUG=false
   LOG_LEVEL=INFO
   MAX_CONVERSATION_HISTORY=50
   CONVERSATION_ARCHIVE_DAYS=90
   LLM_REQUEST_TIMEOUT=30
   LLM_MAX_RETRIES=3
   ```

3. **Deploy**:
   - Push to GitHub
   - Hugging Face will automatically build and deploy
   - Wait for build to complete (5-10 minutes)

### 2.4 Verify Backend

```bash
# Test health endpoint
curl https://your-space-name.hf.space/health

# Expected response:
# {"status":"healthy","service":"todo-chatbot-backend","version":"1.0.0"}
```

**Note**: The backend uses Gemini API (via OpenAI-compatible endpoint), not OpenAI directly.

## Step 3: Frontend Deployment (Vercel)

### 3.1 Prepare Repository

1. Ensure all frontend code is committed
2. Push to GitHub

### 3.2 Create Vercel Project

1. Go to https://vercel.com
2. Click "Add New Project"
3. Import your GitHub repository
4. Configure:
   - Framework Preset: Next.js
   - Root Directory: `phase4-chatbot/frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

### 3.3 Set Environment Variables

In Vercel project settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://your-main-backend.railway.app
NEXT_PUBLIC_CHAT_API_URL=https://your-space-name.hf.space
NEXT_PUBLIC_AUTH_URL=https://your-frontend.vercel.app
```

**Note**: The frontend needs both the main backend URL (for tasks/auth) and the chatbot backend URL.

### 3.4 Deploy

1. Click "Deploy"
2. Wait for deployment to complete (2-5 minutes)
3. Copy the deployment URL

### 3.5 Update Backend CORS

Update backend environment variable on Hugging Face:

```
CORS_ORIGINS=https://your-frontend.vercel.app
```

Redeploy backend for changes to take effect.

## Step 4: Conversation Archival Setup (Optional)

For automatic archival of old conversations:

### 4.1 Create Archival Script

The backend includes conversation archival logic that archives conversations inactive for more than 90 days.

### 4.2 Set Up Cron Job

```bash
# Example cron job (run daily at 2 AM)
0 2 * * * curl -X POST https://your-space-name.hf.space/api/admin/archive-conversations \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 4.3 Monitor Archival

Check logs to verify archival runs successfully:
- Hugging Face Space → Logs
- Look for "Archived N conversations" messages

## Step 5: Integration Testing

### 5.1 Test Backend

```bash
# Get JWT token (from Phase III authentication)
TOKEN="your-jwt-token"
USER_ID="your-user-cuid"  # Note: CUID string, not UUID

# Test chat endpoint
curl -X POST https://your-space-name.hf.space/api/$USER_ID/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Add a task to buy groceries"}'
```

**Note**: user_id is a CUID string from Better Auth, not a UUID.

### 5.2 Test Frontend

1. Navigate to https://your-frontend.vercel.app
2. Login (using Phase III authentication)
3. Click "Start Chatting"
4. Test commands:
   - "Add a task to buy groceries"
   - "Show me all my tasks"
   - "Mark task 1 as complete"

### 5.3 Test All MCP Tools

- ✅ add_task: "Add a task to buy groceries"
- ✅ list_tasks: "Show me all my tasks"
- ✅ complete_task: "Mark task 1 as complete"
- ✅ update_task: "Change task 1 to 'Buy groceries and fruits'"
- ✅ delete_task: "Delete task 2"

### 5.4 Test Conversation Continuity

1. Send multiple messages in same conversation
2. Close browser
3. Reopen and verify conversation persists
4. Verify conversation_id is maintained

## Step 6: Monitoring & Maintenance

### 6.1 Backend Monitoring

**Hugging Face Logs:**
- Go to your Space → Logs
- Monitor for errors and performance issues

**Health Checks:**
```bash
# Set up monitoring (e.g., UptimeRobot)
curl https://your-space-name.hf.space/health
```

### 6.2 Frontend Monitoring

**Vercel Analytics:**
- Enable in Vercel dashboard
- Monitor page views, performance, errors

**Error Tracking:**
- Consider adding Sentry or similar
- Track frontend errors and API failures

### 6.3 Database Monitoring

**Neon Dashboard:**
- Monitor connection count
- Check query performance
- Review storage usage

**Conversation Archival:**
- Set up cron job to run archival script
- Archive conversations older than 90 days

### 6.4 Gemini API Monitoring

**Usage Dashboard:**
- Go to https://console.cloud.google.com/apis/dashboard
- Monitor API calls and quotas
- Set up usage alerts

**Rate Limits:**
- Monitor for rate limit errors
- Adjust retry logic if needed
- Consider upgrading quota if necessary

## Step 7: Scaling Considerations

### 7.1 Backend Scaling

**Hugging Face:**
- Upgrade to better hardware if needed
- Consider multiple replicas for high traffic

**Database:**
- Neon auto-scales
- Monitor connection pool size
- Add read replicas if needed

### 7.2 Frontend Scaling

**Vercel:**
- Auto-scales by default
- Monitor bandwidth usage
- Consider CDN for static assets

### 7.3 Cost Optimization

**Gemini API:**
- Monitor token usage in Google Cloud Console
- Optimize prompts for efficiency
- Consider caching common responses
- Gemini offers generous free tier

**Database:**
- Implement conversation archival (see Step 4)
- Clean up old archived conversations
- Optimize indexes (see DATABASE_MIGRATION.md)

## Troubleshooting

### Backend Issues

**Issue**: Build fails on Hugging Face
**Solution**: Check Dockerfile syntax, verify all dependencies in requirements.txt

**Issue**: Health check fails
**Solution**: Check logs, verify DATABASE_URL and GEMINI_API_KEY are set

**Issue**: CORS errors
**Solution**: Verify CORS_ORIGINS includes frontend URL

### Frontend Issues

**Issue**: Build fails on Vercel
**Solution**: Check package.json, verify all dependencies are listed

**Issue**: API calls fail
**Solution**: Verify NEXT_PUBLIC_API_URL is correct, check backend is running

**Issue**: Authentication errors
**Solution**: Verify JWT token is valid, check user_id matches token

### Database Issues

**Issue**: Connection errors
**Solution**: Verify DATABASE_URL is correct, check Neon dashboard for issues

**Issue**: Migration fails
**Solution**: Check if tables already exist, verify SQL syntax

## Rollback Procedure

### Backend Rollback

1. Go to Hugging Face Space → Settings
2. Revert to previous commit
3. Redeploy

### Frontend Rollback

1. Go to Vercel project → Deployments
2. Find previous successful deployment
3. Click "Promote to Production"

### Database Rollback

```bash
# Run rollback script
psql $DATABASE_URL < phase4-chatbot/backend/migrations/001_rollback_chatbot_tables.sql
```

## Post-Deployment Checklist

- [ ] Backend deployed and health check passing
- [ ] Frontend deployed and accessible
- [ ] Database migrations applied (see [DATABASE_MIGRATION.md](docs/DATABASE_MIGRATION.md))
- [ ] All environment variables set correctly
- [ ] CORS configured properly
- [ ] All 6 user stories tested end-to-end (see [TESTING_GUIDE.md](../../TESTING_GUIDE.md))
- [ ] Conversation continuity tested
- [ ] Error handling tested
- [ ] Monitoring set up
- [ ] Documentation updated with production URLs
- [ ] Conversation archival configured (optional)

## Additional Resources

- **Testing Guide**: [../../TESTING_GUIDE.md](../../TESTING_GUIDE.md) - Complete local testing instructions
- **Database Migration**: [docs/DATABASE_MIGRATION.md](docs/DATABASE_MIGRATION.md) - Detailed migration guide
- **Deployment Checklist**: [docs/DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md) - Step-by-step deployment tasks

## Production URLs

Update these after deployment:

- **Frontend**: https://your-frontend.vercel.app
- **Backend**: https://your-space-name.hf.space
- **API Docs**: https://your-space-name.hf.space/docs
- **Health Check**: https://your-space-name.hf.space/health

---

**Last Updated**: 2026-01-29
**Status**: Ready for deployment
