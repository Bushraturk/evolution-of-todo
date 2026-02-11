# Data Model: Advanced Cloud Deployment

**Feature**: 006-advanced-cloud-deployment
**Date**: 2026-02-11
**Purpose**: Database schema and entity definitions for advanced features

## Overview

This document extends the existing Phase IV data model with support for:
- Recurring tasks (daily, weekly, monthly)
- Due dates and reminders
- Task events for event-driven architecture
- Scheduled notifications

## Entity Relationship Diagram

```
┌─────────────────┐       ┌──────────────────┐
│     User        │       │   Task           │
│  (existing)     │──────<│  (extended)      │
└─────────────────┘       └──────────────────┘
                                   │
                                   │ 1:1
                                   ▼
                          ┌──────────────────┐
                          │ RecurringPattern │
                          └──────────────────┘
                                   │
                                   │ 1:N
                                   ▼
                          ┌──────────────────┐
                          │   Reminder       │
                          └──────────────────┘
                                   │
                                   │ 1:N
                                   ▼
                          ┌──────────────────┐
                          │ ScheduledNotif   │
                          └──────────────────┘

┌─────────────────┐
│   TaskEvent     │  (Audit log - optional if using Kafka retention)
└─────────────────┘

┌─────────────────┐
│   Tag           │  (Many-to-many with Task)
└─────────────────┘
```

## Core Entities

### 1. Task (Extended)

**Purpose**: Extends existing Task entity with advanced features

**Schema**:
```sql
CREATE TABLE tasks (
    -- Existing fields from Phase IV
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    category_id UUID REFERENCES categories(id),
    user_id VARCHAR(255) NOT NULL,  -- Better Auth CUID
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- NEW: Advanced features
    priority VARCHAR(10) CHECK (priority IN ('HIGH', 'MEDIUM', 'LOW')),
    due_date TIMESTAMP WITH TIME ZONE,
    is_recurring BOOLEAN DEFAULT FALSE,
    parent_task_id UUID REFERENCES tasks(id),  -- For recurring task chains
    recurrence_id UUID REFERENCES recurring_patterns(id),

    -- Indexes
    INDEX idx_tasks_user_id (user_id),
    INDEX idx_tasks_due_date (due_date),
    INDEX idx_tasks_priority (priority),
    INDEX idx_tasks_parent (parent_task_id),
    INDEX idx_tasks_completed_due (completed, due_date)  -- For overdue queries
);
```

**Validation Rules**:
- `title`: Required, max 200 characters
- `description`: Optional, max 1000 characters
- `priority`: Must be HIGH, MEDIUM, or LOW (if provided)
- `due_date`: Must be in the future when creating (can be past for overdue tasks)
- `is_recurring`: If true, must have `recurrence_id`
- `parent_task_id`: If provided, must reference an existing task

**State Transitions**:
```
pending → in_progress → completed
pending → completed (direct completion)
completed → pending (reopen)
```

**Business Rules**:
- Recurring tasks cannot be deleted directly (must delete parent or all occurrences)
- Completing a recurring task triggers creation of next occurrence
- Due date changes on recurring tasks only affect current occurrence
- Priority changes propagate to future occurrences (optional behavior)

---

### 2. RecurringPattern (New)

**Purpose**: Stores recurrence configuration for recurring tasks

**Schema**:
```sql
CREATE TABLE recurring_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    frequency VARCHAR(20) NOT NULL CHECK (frequency IN ('DAILY', 'WEEKLY', 'MONTHLY')),
    interval INTEGER DEFAULT 1,  -- Every N days/weeks/months
    day_of_week INTEGER,  -- 0-6 for weekly (0=Sunday)
    day_of_month INTEGER,  -- 1-31 for monthly
    next_occurrence_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE,  -- Optional end date for recurrence
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CHECK (
        (frequency = 'WEEKLY' AND day_of_week IS NOT NULL) OR
        (frequency = 'MONTHLY' AND day_of_month IS NOT NULL) OR
        (frequency = 'DAILY')
    ),

    -- Indexes
    INDEX idx_recurring_next_occurrence (next_occurrence_date)
);
```

**Validation Rules**:
- `frequency`: Required, must be DAILY, WEEKLY, or MONTHLY
- `interval`: Must be positive integer (default 1)
- `day_of_week`: Required for WEEKLY, must be 0-6
- `day_of_month`: Required for MONTHLY, must be 1-31
- `next_occurrence_date`: Required, must be in the future
- `end_date`: Optional, must be after next_occurrence_date

**Examples**:
```json
// Daily recurrence
{
  "frequency": "DAILY",
  "interval": 1,
  "next_occurrence_date": "2026-02-12T09:00:00Z"
}

// Weekly recurrence (every Monday)
{
  "frequency": "WEEKLY",
  "interval": 1,
  "day_of_week": 1,
  "next_occurrence_date": "2026-02-17T09:00:00Z"
}

// Monthly recurrence (15th of each month)
{
  "frequency": "MONTHLY",
  "interval": 1,
  "day_of_month": 15,
  "next_occurrence_date": "2026-03-15T09:00:00Z"
}
```

---

### 3. Reminder (New)

**Purpose**: Stores reminder configuration for tasks with due dates

**Schema**:
```sql
CREATE TABLE reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    remind_at TIMESTAMP WITH TIME ZONE NOT NULL,
    offset_minutes INTEGER NOT NULL,  -- Minutes before due date
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('EMAIL', 'PUSH', 'BOTH')),
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'SCHEDULED', 'SENT', 'FAILED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes
    INDEX idx_reminders_task (task_id),
    INDEX idx_reminders_user (user_id),
    INDEX idx_reminders_remind_at (remind_at),
    INDEX idx_reminders_status_remind (status, remind_at)  -- For scheduler queries
);
```

**Validation Rules**:
- `task_id`: Required, must reference existing task
- `remind_at`: Required, calculated as task.due_date - offset_minutes
- `offset_minutes`: Must be positive (e.g., 60 for 1 hour before)
- `channel`: Must be EMAIL, PUSH, or BOTH
- `status`: Managed by system, not user-editable

**State Transitions**:
```
PENDING → SCHEDULED (when queued for delivery)
SCHEDULED → SENT (when successfully delivered)
SCHEDULED → FAILED (when delivery fails)
FAILED → SCHEDULED (when retrying)
```

**Business Rules**:
- Reminder is automatically deleted when task is deleted (CASCADE)
- Reminder is marked SENT after successful delivery
- Failed reminders are retried up to 3 times
- Reminders for completed tasks are not sent

---

### 4. ScheduledNotification (New)

**Purpose**: Queue of pending notifications to be delivered

**Schema**:
```sql
CREATE TABLE scheduled_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reminder_id UUID NOT NULL REFERENCES reminders(id) ON DELETE CASCADE,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    scheduled_for TIMESTAMP WITH TIME ZONE NOT NULL,
    delivery_channel VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'QUEUED', 'SENT', 'FAILED')),
    retry_count INTEGER DEFAULT 0,
    last_attempt_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes
    INDEX idx_scheduled_notif_scheduled (scheduled_for),
    INDEX idx_scheduled_notif_status (status),
    INDEX idx_scheduled_notif_user (user_id)
);
```

**Validation Rules**:
- `scheduled_for`: Required, when notification should be sent
- `retry_count`: Max 3 retries
- `status`: Managed by notification service

**Business Rules**:
- Cron job queries for notifications with scheduled_for <= NOW() and status = PENDING
- After 3 failed retries, status remains FAILED and no more retries
- Successful delivery updates reminder.status to SENT

---

### 5. Tag (New)

**Purpose**: Categorization labels for tasks

**Schema**:
```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    color VARCHAR(7),  -- Hex color code (e.g., #FF5733)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Unique constraint: user cannot have duplicate tag names
    UNIQUE (user_id, name),

    -- Indexes
    INDEX idx_tags_user (user_id)
);

CREATE TABLE task_tags (
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    PRIMARY KEY (task_id, tag_id),
    INDEX idx_task_tags_task (task_id),
    INDEX idx_task_tags_tag (tag_id)
);
```

**Validation Rules**:
- `name`: Required, max 50 characters, unique per user
- `color`: Optional, must be valid hex color code

**Business Rules**:
- Tags are user-specific (cannot share tags between users)
- Deleting a tag removes it from all tasks (CASCADE)
- Tasks can have multiple tags (many-to-many)

---

### 6. TaskEvent (Optional - Audit Log)

**Purpose**: Audit trail of all task operations (alternative to Kafka retention)

**Schema**:
```sql
CREATE TABLE task_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(20) NOT NULL CHECK (event_type IN ('CREATED', 'UPDATED', 'COMPLETED', 'DELETED', 'REOPENED')),
    task_id UUID NOT NULL,  -- Not FK because task may be deleted
    user_id VARCHAR(255) NOT NULL,
    task_snapshot JSONB NOT NULL,  -- Full task state at time of event
    changes JSONB,  -- For UPDATED events, before/after diff
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes
    INDEX idx_task_events_task (task_id),
    INDEX idx_task_events_user (user_id),
    INDEX idx_task_events_timestamp (timestamp),
    INDEX idx_task_events_type (event_type)
);
```

**Note**: This table is optional if using Kafka with long retention (30+ days). Kafka can serve as the audit log. This table is useful for:
- Long-term audit requirements (years)
- Complex queries on historical data
- Compliance requirements

---

## Event Schemas (Kafka Messages)

### TaskCreatedEvent
```json
{
  "event_type": "task.created",
  "event_id": "uuid",
  "timestamp": "2026-02-11T10:00:00Z",
  "task_id": "uuid",
  "user_id": "cuid",
  "task_data": {
    "title": "Daily standup",
    "description": "Team sync meeting",
    "priority": "HIGH",
    "due_date": "2026-02-12T09:00:00Z",
    "is_recurring": true,
    "recurrence": {
      "frequency": "DAILY",
      "interval": 1
    }
  }
}
```

### TaskCompletedEvent
```json
{
  "event_type": "task.completed",
  "event_id": "uuid",
  "timestamp": "2026-02-11T10:00:00Z",
  "task_id": "uuid",
  "user_id": "cuid",
  "completed_at": "2026-02-11T10:00:00Z",
  "is_recurring": true,
  "recurrence_id": "uuid",
  "next_occurrence_date": "2026-02-12T09:00:00Z"
}
```

### ReminderScheduledEvent
```json
{
  "event_type": "reminder.scheduled",
  "event_id": "uuid",
  "timestamp": "2026-02-11T10:00:00Z",
  "reminder_id": "uuid",
  "task_id": "uuid",
  "user_id": "cuid",
  "remind_at": "2026-02-12T08:00:00Z",
  "channel": "EMAIL",
  "task_title": "Daily standup"
}
```

---

## Migration Strategy

### Phase 1: Schema Extensions (Non-Breaking)
```sql
-- Add new columns to existing tasks table
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10);
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN is_recurring BOOLEAN DEFAULT FALSE;
ALTER TABLE tasks ADD COLUMN parent_task_id UUID;
ALTER TABLE tasks ADD COLUMN recurrence_id UUID;

-- Add indexes
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_completed_due ON tasks(completed, due_date);
```

### Phase 2: New Tables
```sql
-- Create new tables in order (respecting foreign keys)
CREATE TABLE recurring_patterns (...);
CREATE TABLE tags (...);
CREATE TABLE task_tags (...);
CREATE TABLE reminders (...);
CREATE TABLE scheduled_notifications (...);
CREATE TABLE task_events (...);  -- Optional
```

### Phase 3: Add Foreign Keys
```sql
ALTER TABLE tasks ADD CONSTRAINT fk_tasks_recurrence
  FOREIGN KEY (recurrence_id) REFERENCES recurring_patterns(id);

ALTER TABLE tasks ADD CONSTRAINT fk_tasks_parent
  FOREIGN KEY (parent_task_id) REFERENCES tasks(id);
```

### Phase 4: Data Migration (if needed)
```sql
-- No data migration needed for new features
-- Existing tasks remain unchanged (NULL for new fields)
```

---

## Query Patterns

### Get Overdue Tasks
```sql
SELECT * FROM tasks
WHERE user_id = $1
  AND completed = FALSE
  AND due_date < NOW()
ORDER BY due_date ASC;
```

### Get Tasks Due Today
```sql
SELECT * FROM tasks
WHERE user_id = $1
  AND completed = FALSE
  AND due_date::DATE = CURRENT_DATE
ORDER BY due_date ASC;
```

### Get Recurring Tasks Needing Next Occurrence
```sql
SELECT t.*, rp.*
FROM tasks t
JOIN recurring_patterns rp ON t.recurrence_id = rp.id
WHERE t.completed = TRUE
  AND rp.next_occurrence_date <= NOW()
  AND NOT EXISTS (
    SELECT 1 FROM tasks t2
    WHERE t2.parent_task_id = t.id
      AND t2.due_date = rp.next_occurrence_date
  );
```

### Get Pending Reminders
```sql
SELECT sn.*, t.title, t.due_date
FROM scheduled_notifications sn
JOIN tasks t ON sn.task_id = t.id
WHERE sn.status = 'PENDING'
  AND sn.scheduled_for <= NOW()
  AND t.completed = FALSE
ORDER BY sn.scheduled_for ASC
LIMIT 100;
```

### Search Tasks with Filters
```sql
SELECT DISTINCT t.*
FROM tasks t
LEFT JOIN task_tags tt ON t.id = tt.task_id
LEFT JOIN tags tag ON tt.tag_id = tag.id
WHERE t.user_id = $1
  AND ($2 IS NULL OR t.priority = $2)  -- Priority filter
  AND ($3 IS NULL OR t.completed = $3)  -- Status filter
  AND ($4 IS NULL OR tag.name = ANY($4))  -- Tag filter (array)
  AND ($5 IS NULL OR t.due_date >= $5)  -- Due date range start
  AND ($6 IS NULL OR t.due_date <= $6)  -- Due date range end
  AND ($7 IS NULL OR t.title ILIKE '%' || $7 || '%' OR t.description ILIKE '%' || $7 || '%')  -- Search
ORDER BY
  CASE WHEN $8 = 'priority' THEN t.priority END DESC,
  CASE WHEN $8 = 'due_date' THEN t.due_date END ASC,
  CASE WHEN $8 = 'created_at' THEN t.created_at END DESC;
```

---

## Performance Considerations

### Indexes
- All foreign keys have indexes
- Composite indexes for common query patterns (completed + due_date)
- Partial indexes for specific queries (e.g., pending notifications)

### Partitioning (Future)
- Consider partitioning `task_events` by timestamp (monthly partitions)
- Consider partitioning `scheduled_notifications` by scheduled_for date

### Caching
- Cache user's active tags (rarely change)
- Cache recurring patterns (rarely change)
- Invalidate task cache on updates

### Archival
- Archive completed tasks older than 1 year
- Archive sent notifications older than 90 days
- Archive task events older than 2 years (if using table)

---

## Data Integrity Rules

1. **Referential Integrity**: All foreign keys use CASCADE on delete where appropriate
2. **Unique Constraints**: Prevent duplicate tags per user, prevent duplicate task occurrences
3. **Check Constraints**: Validate enums (priority, frequency, status)
4. **Triggers**: Update `updated_at` timestamp on row changes
5. **Soft Deletes**: Consider soft deletes for tasks (add `deleted_at` column) for audit trail

---

**Data Model Version**: 1.0.0
**Last Updated**: 2026-02-11
**Status**: Ready for Implementation
