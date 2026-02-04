# Database Migration Guide - Phase IV AI Chatbot

**Last Updated**: 2026-02-01
**Migration**: 001_add_chatbot_tables.sql
**Status**: Ready for execution

## Overview

This guide provides step-by-step instructions for running the database migration that adds the conversation and message tables required for the Phase IV AI Chatbot feature.

---

## Migration Summary

**What This Migration Does:**
- Creates `conversation` table for chat sessions
- Creates `message` table for chat messages
- Adds indexes for query optimization
- Adds table/column comments for documentation

**What This Migration Does NOT Do:**
- Does not modify existing tables (task, user, category)
- Does not require downtime
- Does not affect existing data

---

## Prerequisites

### Required Access
- PostgreSQL database connection string
- Database user with CREATE TABLE privileges
- Database user with CREATE INDEX privileges

### Required Tools
- `psql` command-line tool (PostgreSQL client)
- OR database GUI tool (pgAdmin, DBeaver, etc.)

### Backup Recommendation
```bash
# Create backup before migration (recommended)
pg_dump $DATABASE_URL > backup_before_chatbot_migration_$(date +%Y%m%d).sql
```

---

## Migration Files

### Forward Migration
**File**: `phase4-chatbot/backend/migrations/001_add_chatbot_tables.sql`

**Contents:**
- CREATE TABLE conversation
- CREATE TABLE message
- CREATE INDEX statements (6 indexes)
- COMMENT statements for documentation

### Rollback Migration
**File**: `phase4-chatbot/backend/migrations/001_rollback_chatbot_tables.sql`

**Contents:**
- DROP TABLE message CASCADE
- DROP TABLE conversation CASCADE

---

## Local Database Migration

### Step 1: Verify Database Connection

```bash
# Test connection
psql $DATABASE_URL -c "SELECT version();"

# Should output PostgreSQL version
```

### Step 2: Review Migration Script

```bash
# View the migration script
cat phase4-chatbot/backend/migrations/001_add_chatbot_tables.sql

# Verify:
# - user_id is VARCHAR(255) not UUID
# - No foreign key constraints to user table
# - All indexes are present
```

### Step 3: Run Migration

```bash
# Navigate to migration directory
cd phase4-chatbot/backend/migrations

# Run migration
psql $DATABASE_URL -f 001_add_chatbot_tables.sql

# Expected output:
# CREATE EXTENSION
# CREATE TABLE
# CREATE INDEX
# CREATE INDEX
# ... (multiple index creation messages)
# COMMENT
```

### Step 4: Verify Tables Created

```bash
# Check conversation table
psql $DATABASE_URL -c "\d conversation"

# Expected output:
# Table "public.conversation"
# Column      | Type                     | Collation | Nullable | Default
# ------------+--------------------------+-----------+----------+-------------------
# id          | uuid                     |           | not null | uuid_generate_v4()
# user_id     | character varying(255)   |           | not null |
# created_at  | timestamp without time zone |        | not null | now()
# updated_at  | timestamp without time zone |        | not null | now()
# archived_at | timestamp without time zone |        |          |

# Check message table
psql $DATABASE_URL -c "\d message"

# Expected output:
# Table "public.message"
# Column          | Type                     | Collation | Nullable | Default
# ----------------+--------------------------+-----------+----------+-------------------
# id              | uuid                     |           | not null | uuid_generate_v4()
# conversation_id | uuid                     |           | not null |
# user_id         | character varying(255)   |           | not null |
# role            | character varying(20)    |           | not null |
# content         | text                     |           | not null |
# created_at      | timestamp without time zone |        | not null | now()
```

### Step 5: Verify Indexes Created

```bash
# List all indexes on conversation table
psql $DATABASE_URL -c "\di idx_conversation_*"

# Expected output:
# idx_conversation_archived_at
# idx_conversation_updated_at
# idx_conversation_user_id

# List all indexes on message table
psql $DATABASE_URL -c "\di idx_message_*"

# Expected output:
# idx_message_conversation_id
# idx_message_conv_created
# idx_message_created_at
```

### Step 6: Verify Constraints

```bash
# Check conversation constraints
psql $DATABASE_URL -c "SELECT conname, contype FROM pg_constraint WHERE conrelid = 'conversation'::regclass;"

# Check message constraints
psql $DATABASE_URL -c "SELECT conname, contype FROM pg_constraint WHERE conrelid = 'message'::regclass;"

# Expected: Primary key constraints and CHECK constraint on role
```

---

## Production Database Migration (Neon)

### Step 1: Access Neon Console

1. Login to [Neon Console](https://console.neon.tech/)
2. Select your project
3. Navigate to "SQL Editor" tab

### Step 2: Create Backup Branch (Recommended)

1. Go to "Branches" tab
2. Click "Create Branch"
3. Name: "backup-before-chatbot-migration"
4. Source: main branch
5. Click "Create"

This creates a point-in-time backup you can restore if needed.

### Step 3: Run Migration in SQL Editor

1. Open `phase4-chatbot/backend/migrations/001_add_chatbot_tables.sql`
2. Copy entire contents
3. Paste into Neon SQL Editor
4. Click "Run" button
5. Verify "Success" message appears

### Step 4: Verify Tables in Neon

```sql
-- Run in Neon SQL Editor

-- Check tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('conversation', 'message');

-- Should return 2 rows

-- Check row counts (should be 0 initially)
SELECT 'conversation' as table_name, COUNT(*) as row_count FROM conversation
UNION ALL
SELECT 'message' as table_name, COUNT(*) as row_count FROM message;
```

### Step 5: Verify Indexes in Neon

```sql
-- Run in Neon SQL Editor

-- List all indexes
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename IN ('conversation', 'message')
ORDER BY tablename, indexname;

-- Should return 9 rows (3 for conversation, 6 for message including PKs)
```

---

## Rollback Procedure

### When to Rollback
- Migration failed partway through
- Discovered critical issue after migration
- Need to revert to previous state

### Rollback Steps

```bash
# Step 1: Run rollback script
psql $DATABASE_URL -f phase4-chatbot/backend/migrations/001_rollback_chatbot_tables.sql

# Expected output:
# DROP TABLE
# DROP TABLE

# Step 2: Verify tables removed
psql $DATABASE_URL -c "\dt conversation"
# Should return: Did not find any relation named "conversation"

psql $DATABASE_URL -c "\dt message"
# Should return: Did not find any relation named "message"

# Step 3: Restore from backup (if needed)
psql $DATABASE_URL < backup_before_chatbot_migration_YYYYMMDD.sql
```

### Rollback in Neon

1. Go to "Branches" tab
2. Find backup branch created earlier
3. Click "..." menu → "Set as primary"
4. Confirm action

This restores database to state before migration.

---

## Common Issues and Solutions

### Issue: "relation already exists"

**Cause**: Tables already created from previous migration attempt

**Solution**:
```bash
# Check if tables exist
psql $DATABASE_URL -c "\dt conversation"

# If exists, either:
# Option 1: Skip migration (tables already created)
# Option 2: Drop and recreate
psql $DATABASE_URL -f phase4-chatbot/backend/migrations/001_rollback_chatbot_tables.sql
psql $DATABASE_URL -f phase4-chatbot/backend/migrations/001_add_chatbot_tables.sql
```

---

### Issue: "permission denied"

**Cause**: Database user lacks CREATE TABLE privileges

**Solution**:
```sql
-- Grant necessary privileges (run as superuser)
GRANT CREATE ON SCHEMA public TO your_database_user;
GRANT USAGE ON SCHEMA public TO your_database_user;
```

---

### Issue: "extension uuid-ossp does not exist"

**Cause**: UUID extension not available

**Solution**:
```sql
-- Install extension (run as superuser)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Or use gen_random_uuid() instead (PostgreSQL 13+)
-- Modify migration to use gen_random_uuid() instead of uuid_generate_v4()
```

---

### Issue: Migration hangs or times out

**Cause**: Database locked or slow connection

**Solution**:
```bash
# Check for locks
psql $DATABASE_URL -c "SELECT * FROM pg_locks WHERE NOT granted;"

# Kill blocking queries (if safe)
psql $DATABASE_URL -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction';"

# Retry migration
```

---

## Performance Verification

### Check Index Usage

```sql
-- Run after migration and some usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE tablename IN ('conversation', 'message')
ORDER BY idx_scan DESC;

-- Indexes with idx_scan > 0 are being used
-- Indexes with idx_scan = 0 may need review
```

### Check Table Statistics

```sql
-- Run after some usage
SELECT
    schemaname,
    tablename,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE tablename IN ('conversation', 'message');
```

---

## Post-Migration Checklist

✅ **Tables Created**
- [ ] conversation table exists
- [ ] message table exists
- [ ] Both tables have correct columns
- [ ] user_id is VARCHAR(255) not UUID

✅ **Indexes Created**
- [ ] idx_conversation_user_id
- [ ] idx_conversation_updated_at
- [ ] idx_conversation_archived_at
- [ ] idx_message_conversation_id
- [ ] idx_message_created_at
- [ ] idx_message_conv_created

✅ **Constraints Verified**
- [ ] Primary keys on id columns
- [ ] CHECK constraint on message.role
- [ ] Foreign key from message to conversation

✅ **Permissions Set**
- [ ] Application user can INSERT into tables
- [ ] Application user can SELECT from tables
- [ ] Application user can UPDATE conversation.updated_at

✅ **Backup Created**
- [ ] Database backup taken before migration
- [ ] Backup verified and accessible
- [ ] Rollback script tested (optional)

---

## Next Steps

After successful migration:
1. ✅ Verify tables and indexes created
2. ✅ Test chatbot backend can connect to database
3. ✅ Run quick smoke test (create conversation, add message)
4. ✅ Monitor database performance
5. ✅ Proceed with backend deployment

---

## Support

**Questions or Issues?**
- Check "Common Issues and Solutions" section above
- Review PostgreSQL logs for detailed error messages
- Verify database connection string is correct
- Ensure database user has necessary privileges

**Rollback if Needed:**
- Use rollback script to revert changes
- Restore from backup if data corruption occurred
- Contact database administrator for assistance
