# Data Model: AI-Powered Todo Chatbot

**Feature**: 004-ai-chatbot
**Date**: 2026-01-29
**Purpose**: Define database schema for conversation and message storage

## Overview

This document defines the data model for the AI-powered chatbot feature. The model introduces two new entities (Conversation and Message) while reusing existing entities (Task and User) from Phase II/III.

---

## Entity Relationship Diagram

```
┌─────────────────┐
│      User       │ (Existing - Phase III)
│─────────────────│
│ id: UUID (PK)   │
│ email: String   │
│ name: String    │
│ ...             │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────┴────────────────┐
    │                     │
    │                     │
┌───▼──────────────┐  ┌──▼──────────────┐
│   Conversation   │  │      Task       │ (Existing - Phase II)
│──────────────────│  │─────────────────│
│ id: UUID (PK)    │  │ id: UUID (PK)   │
│ user_id: UUID    │  │ user_id: UUID   │
│ created_at       │  │ title: String   │
│ updated_at       │  │ description     │
│ archived_at      │  │ completed: Bool │
└────────┬─────────┘  │ priority        │
         │            │ category_id     │
         │ 1:N        │ created_at      │
         │            │ updated_at      │
    ┌────▼─────────┐  └─────────────────┘
    │   Message    │
    │──────────────│
    │ id: UUID (PK)│
    │ conv_id: UUID│
    │ user_id: UUID│
    │ role: Enum   │
    │ content: Text│
    │ created_at   │
    └──────────────┘
```

---

## New Entities

### 1. Conversation

Represents a chat session between a user and the AI assistant.

**Table Name**: `conversation`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique conversation identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY → user(id) | Owner of the conversation |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When conversation started |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last message timestamp |
| archived_at | TIMESTAMP | NULL | When conversation was archived (NULL = active) |

**Indexes**:
- `idx_conversation_user_id` on `user_id` (for user's conversation list)
- `idx_conversation_updated_at` on `updated_at` (for sorting by recency)
- `idx_conversation_archived_at` on `archived_at` (for filtering active conversations)

**Relationships**:
- **User** (Many-to-One): Each conversation belongs to one user
- **Message** (One-to-Many): Each conversation has multiple messages

**Business Rules**:
- Conversations are soft-deleted via `archived_at` timestamp
- Active conversations have `archived_at = NULL`
- Conversations archived after 90 days of inactivity (no new messages)
- `updated_at` is updated whenever a new message is added

**SQLModel Definition**:
```python
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship

class Conversation(SQLModel, table=True):
    """Chat session between user and AI assistant."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    archived_at: Optional[datetime] = Field(default=None, index=True)

    # Relationships
    messages: list["Message"] = Relationship(back_populates="conversation")
```

---

### 2. Message

Represents a single message in a conversation (from user or assistant).

**Table Name**: `message`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique message identifier |
| conversation_id | UUID | NOT NULL, FOREIGN KEY → conversation(id) | Parent conversation |
| user_id | UUID | NOT NULL, FOREIGN KEY → user(id) | Message owner (for data isolation) |
| role | VARCHAR(20) | NOT NULL, CHECK IN ('user', 'assistant') | Message sender role |
| content | TEXT | NOT NULL | Message text content |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When message was sent |

**Indexes**:
- `idx_message_conversation_id` on `conversation_id` (for loading conversation history)
- `idx_message_created_at` on `created_at` (for chronological ordering)
- Composite index: `idx_message_conv_created` on `(conversation_id, created_at)` (optimized history queries)

**Relationships**:
- **Conversation** (Many-to-One): Each message belongs to one conversation
- **User** (Many-to-One): Each message belongs to one user (for data isolation)

**Business Rules**:
- `role` must be either 'user' or 'assistant'
- User messages represent user input
- Assistant messages represent AI responses
- Messages are immutable (no updates, only inserts)
- Messages are never deleted (conversation history preserved)
- `user_id` must match conversation's `user_id` (enforced in application layer)

**SQLModel Definition**:
```python
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship

class MessageRole(str, Enum):
    """Message sender role."""
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    """Single message in a conversation."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversation.id", index=True)
    user_id: UUID = Field(foreign_key="user.id")
    role: MessageRole = Field(sa_column_kwargs={"nullable": False})
    content: str = Field(sa_column_kwargs={"type_": "TEXT"})
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
```

---

## Existing Entities (Reused)

### 3. User (Phase III)

**Table Name**: `user`

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | User identifier |
| email | VARCHAR | User email (unique) |
| name | VARCHAR | User display name |
| hashed_password | VARCHAR | Bcrypt password hash |
| created_at | TIMESTAMP | Account creation time |
| updated_at | TIMESTAMP | Last profile update |

**Usage in Chatbot**:
- `user_id` links conversations and messages to users
- Authentication validates user identity before chat operations
- User isolation ensures users only see their own conversations

---

### 4. Task (Phase II)

**Table Name**: `task`

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Task identifier |
| user_id | UUID | Task owner |
| title | VARCHAR | Task title |
| description | TEXT | Task details |
| completed | BOOLEAN | Completion status |
| priority | VARCHAR | Priority level (high/medium/low) |
| category_id | UUID | Category reference |
| created_at | TIMESTAMP | Task creation time |
| updated_at | TIMESTAMP | Last modification time |

**Usage in Chatbot**:
- MCP tools perform CRUD operations on tasks
- Chatbot enables natural language task management
- No schema changes required (backward compatible)

---

## Data Access Patterns

### 1. Create New Conversation
```sql
INSERT INTO conversation (id, user_id, created_at, updated_at)
VALUES (uuid_generate_v4(), :user_id, NOW(), NOW())
RETURNING id;
```

**Frequency**: Once per new chat session
**Performance**: Fast (single insert)

---

### 2. Load Conversation History (Last 50 Messages)
```sql
SELECT id, role, content, created_at
FROM message
WHERE conversation_id = :conversation_id
  AND user_id = :user_id
ORDER BY created_at DESC
LIMIT 50;
```

**Frequency**: Every chat request
**Performance**: Fast with composite index on (conversation_id, created_at)
**Optimization**: Limit to 50 messages for performance

---

### 3. Add Message to Conversation
```sql
-- Insert message
INSERT INTO message (id, conversation_id, user_id, role, content, created_at)
VALUES (uuid_generate_v4(), :conversation_id, :user_id, :role, :content, NOW());

-- Update conversation timestamp
UPDATE conversation
SET updated_at = NOW()
WHERE id = :conversation_id;
```

**Frequency**: Twice per chat request (user message + assistant response)
**Performance**: Fast (two simple inserts/updates)

---

### 4. List User's Active Conversations
```sql
SELECT id, created_at, updated_at
FROM conversation
WHERE user_id = :user_id
  AND archived_at IS NULL
ORDER BY updated_at DESC
LIMIT 20;
```

**Frequency**: When user opens chat interface
**Performance**: Fast with index on (user_id, archived_at, updated_at)

---

### 5. Archive Old Conversations (Background Job)
```sql
UPDATE conversation
SET archived_at = NOW()
WHERE updated_at < NOW() - INTERVAL '90 days'
  AND archived_at IS NULL;
```

**Frequency**: Daily background job
**Performance**: Batch update, runs during low-traffic hours

---

## Database Migration

### Migration Script: `001_add_chatbot_tables.sql`

```sql
-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create conversation table
CREATE TABLE conversation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    archived_at TIMESTAMP NULL
);

-- Create indexes for conversation
CREATE INDEX idx_conversation_user_id ON conversation(user_id);
CREATE INDEX idx_conversation_updated_at ON conversation(updated_at);
CREATE INDEX idx_conversation_archived_at ON conversation(archived_at);

-- Create message table
CREATE TABLE message (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for message
CREATE INDEX idx_message_conversation_id ON message(conversation_id);
CREATE INDEX idx_message_created_at ON message(created_at);
CREATE INDEX idx_message_conv_created ON message(conversation_id, created_at);

-- Add comments for documentation
COMMENT ON TABLE conversation IS 'Chat sessions between users and AI assistant';
COMMENT ON TABLE message IS 'Individual messages in conversations';
COMMENT ON COLUMN conversation.archived_at IS 'NULL for active conversations, timestamp for archived';
COMMENT ON COLUMN message.role IS 'Either user or assistant';
```

### Rollback Script: `001_rollback_chatbot_tables.sql`

```sql
-- Drop tables in reverse order (respects foreign keys)
DROP TABLE IF EXISTS message CASCADE;
DROP TABLE IF EXISTS conversation CASCADE;
```

---

## Storage Estimates

### Assumptions
- 10,000 active users
- Average 10 conversations per user
- Average 20 messages per conversation
- Average message size: 200 bytes

### Calculations

**Conversation Table**:
- Row size: ~100 bytes (UUID + timestamps)
- Total rows: 10,000 users × 10 conversations = 100,000
- Storage: 100,000 × 100 bytes = 10 MB

**Message Table**:
- Row size: ~300 bytes (UUIDs + text content)
- Total rows: 100,000 conversations × 20 messages = 2,000,000
- Storage: 2,000,000 × 300 bytes = 600 MB

**Total Storage**: ~610 MB (well within PostgreSQL capacity)

**Growth Rate**:
- New messages: ~10,000 per day (1,000 active users × 10 messages/day)
- Daily growth: ~3 MB
- Annual growth: ~1 GB (manageable)

---

## Data Retention Policy

### Active Conversations
- **Retention**: Indefinite
- **Criteria**: `archived_at IS NULL`
- **Access**: Full read/write access

### Archived Conversations
- **Retention**: 1 year after archival
- **Criteria**: `archived_at IS NOT NULL AND archived_at > NOW() - INTERVAL '1 year'`
- **Access**: Read-only, can be restored

### Deleted Conversations
- **Retention**: Permanent deletion after 1 year of archival
- **Criteria**: `archived_at < NOW() - INTERVAL '1 year'`
- **Process**: Background job runs monthly

---

## Security Considerations

### Data Isolation
- All queries filtered by `user_id`
- Users cannot access other users' conversations
- Foreign key constraints enforce referential integrity

### Sensitive Data
- Message content may contain personal information
- No encryption at rest (relies on database-level encryption)
- Conversation history private to each user

### Audit Trail
- `created_at` timestamps provide audit trail
- Immutable messages preserve conversation history
- Archived conversations retained for compliance

---

## Performance Optimization

### Indexes
- Composite index on `(conversation_id, created_at)` for history queries
- Index on `user_id` for user's conversation list
- Index on `archived_at` for filtering active conversations

### Query Optimization
- Limit conversation history to 50 messages
- Use `ORDER BY created_at DESC LIMIT 50` for recent messages
- Batch archive operations during low-traffic hours

### Connection Pooling
- Reuse existing SQLModel connection pool from Phase II/III
- Configure pool size based on concurrent users (default: 20)

---

## Testing Considerations

### Unit Tests
- Test conversation creation with valid user_id
- Test message insertion with role validation
- Test conversation archival logic

### Integration Tests
- Test conversation history retrieval with pagination
- Test concurrent message insertion
- Test user isolation (cannot access other users' data)

### Performance Tests
- Load test with 100 concurrent conversations
- Measure query time for 50-message history retrieval
- Test database performance with 1M+ messages

---

**Status**: ✅ Complete
**Next Step**: Generate API contracts (contracts/)
