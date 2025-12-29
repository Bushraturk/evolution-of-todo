# Data Model: User Authentication & Multi-User Support

**Feature**: 003-user-authentication
**Date**: 2025-12-28

## Entity Relationship Diagram

```
┌─────────────────────┐       ┌─────────────────────┐
│       User          │       │      Session        │
│  (Better Auth)      │       │   (Better Auth)     │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │◄──────│ userId (FK)         │
│ email (unique)      │       │ id (PK)             │
│ name                │       │ token               │
│ emailVerified       │       │ expiresAt           │
│ image               │       │ createdAt           │
│ createdAt           │       │ updatedAt           │
│ updatedAt           │       │ ipAddress           │
└─────────────────────┘       │ userAgent           │
         │                    └─────────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────────┐       ┌─────────────────────┐
│       Task          │       │     Category        │
│   (Updated)         │       │    (Existing)       │
├─────────────────────┤       ├─────────────────────┤
│ id (PK, UUID)       │       │ id (PK, UUID)       │
│ user_id (FK) ← NEW  │       │ name                │
│ title               │       │ color               │
│ description         │       │ created_at          │
│ completed           │       │ updated_at          │
│ priority            │       └─────────────────────┘
│ category_id (FK)    │───────────────┘
│ created_at          │
│ updated_at          │
└─────────────────────┘
```

## Entities

### User (Managed by Better Auth)

Better Auth automatically creates and manages this table.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | TEXT | PK | Unique identifier (CUID) |
| email | TEXT | UNIQUE, NOT NULL | User's email address |
| name | TEXT | NULL | Display name |
| emailVerified | BOOLEAN | DEFAULT false | Email verification status |
| image | TEXT | NULL | Profile image URL |
| createdAt | TIMESTAMP | NOT NULL | Registration timestamp |
| updatedAt | TIMESTAMP | NOT NULL | Last update timestamp |

**Notes**:
- Better Auth uses TEXT for IDs (CUID format)
- Password is stored hashed in a separate `account` table
- Schema managed by Better Auth CLI

### Session (Managed by Better Auth)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | TEXT | PK | Session identifier |
| userId | TEXT | FK → user.id | Owner of session |
| token | TEXT | UNIQUE | Session token |
| expiresAt | TIMESTAMP | NOT NULL | Expiration time |
| createdAt | TIMESTAMP | NOT NULL | Creation time |
| updatedAt | TIMESTAMP | NOT NULL | Last activity |
| ipAddress | TEXT | NULL | Client IP |
| userAgent | TEXT | NULL | Browser/client info |

### Account (Managed by Better Auth)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | TEXT | PK | Account identifier |
| userId | TEXT | FK → user.id | Owner |
| accountId | TEXT | NOT NULL | Provider account ID |
| providerId | TEXT | NOT NULL | "credential" for email/password |
| accessToken | TEXT | NULL | OAuth token |
| refreshToken | TEXT | NULL | OAuth refresh |
| password | TEXT | NULL | Hashed password (for credential provider) |
| createdAt | TIMESTAMP | NOT NULL | Creation time |
| updatedAt | TIMESTAMP | NOT NULL | Update time |

### Task (Updated - Our Table)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, DEFAULT uuid4 | Task identifier |
| **user_id** | TEXT | FK → user.id, NOT NULL, **NEW** | Task owner |
| title | VARCHAR(200) | NOT NULL | Task title |
| description | TEXT | NULL | Task details |
| completed | BOOLEAN | DEFAULT false | Completion status |
| priority | ENUM | DEFAULT 'medium' | high/medium/low |
| category_id | UUID | FK → category.id, NULL | Category reference |
| created_at | TIMESTAMP | DEFAULT now() | Creation time |
| updated_at | TIMESTAMP | DEFAULT now() | Last update |

**Changes from Phase 2**:
- Added `user_id` column (TEXT to match Better Auth user.id)
- Added foreign key constraint to Better Auth user table
- Added index on `user_id` for query performance

### Category (Existing - No Changes)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, DEFAULT uuid4 | Category identifier |
| name | VARCHAR(100) | NOT NULL | Category name |
| color | VARCHAR(7) | NULL | Hex color code |
| created_at | TIMESTAMP | DEFAULT now() | Creation time |
| updated_at | TIMESTAMP | DEFAULT now() | Last update |

**Note**: Categories remain global (shared across users) in Phase 1. User-specific categories can be added in future phases.

## Indexes

### Existing Indexes
- `task_pkey` - Primary key on task.id
- `category_pkey` - Primary key on category.id

### New Indexes Required
- `idx_task_user_id` - Index on task.user_id for user task queries
- `idx_task_user_completed` - Composite index (user_id, completed) for filtered queries

## Migration Strategy

### Better Auth Tables
Run Better Auth CLI to create auth tables:
```bash
cd frontend
npx @better-auth/cli migrate
```

### Task Table Migration

**Option A: Add column with default (Recommended for existing data)**
```sql
-- Add user_id column as nullable first
ALTER TABLE task ADD COLUMN user_id TEXT;

-- Create index
CREATE INDEX idx_task_user_id ON task(user_id);

-- For existing tasks: assign to a default user or delete
-- Option 1: Delete existing tasks (clean slate)
DELETE FROM task;

-- Option 2: Assign to system user (if keeping data)
-- UPDATE task SET user_id = 'system-user-id' WHERE user_id IS NULL;

-- Make column NOT NULL after data cleanup
ALTER TABLE task ALTER COLUMN user_id SET NOT NULL;

-- Add foreign key (after Better Auth tables exist)
ALTER TABLE task ADD CONSTRAINT fk_task_user
  FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE;
```

**Option B: SQLModel Migration (Using Alembic)**
```python
# alembic/versions/xxx_add_user_id_to_task.py
def upgrade():
    op.add_column('task', sa.Column('user_id', sa.Text(), nullable=True))
    op.create_index('idx_task_user_id', 'task', ['user_id'])
    # Run data migration script
    op.execute("DELETE FROM task")  # or assign to default user
    op.alter_column('task', 'user_id', nullable=False)
    op.create_foreign_key('fk_task_user', 'task', 'user', ['user_id'], ['id'], ondelete='CASCADE')

def downgrade():
    op.drop_constraint('fk_task_user', 'task', type_='foreignkey')
    op.drop_index('idx_task_user_id', 'task')
    op.drop_column('task', 'user_id')
```

## Validation Rules

### User (Better Auth handles)
- Email: Valid format, unique
- Password: Minimum 8 characters (enforced by Better Auth)
- Name: Optional, max 255 characters

### Task (Our validation)
- title: Required, 1-200 characters
- description: Optional, max 1000 characters
- user_id: Required, must reference existing user
- priority: Must be 'high', 'medium', or 'low'
- category_id: Optional, must reference existing category if provided

## Query Patterns

### Get User's Tasks
```sql
SELECT * FROM task
WHERE user_id = :current_user_id
ORDER BY created_at DESC;
```

### Create Task for User
```sql
INSERT INTO task (id, user_id, title, description, priority, category_id)
VALUES (:id, :current_user_id, :title, :description, :priority, :category_id);
```

### Verify Task Ownership
```sql
SELECT id FROM task
WHERE id = :task_id AND user_id = :current_user_id;
-- If no row returned, return 403 Forbidden
```

### Delete User's Tasks (on user deletion)
```sql
-- Handled by ON DELETE CASCADE
DELETE FROM user WHERE id = :user_id;
-- Automatically deletes all tasks with that user_id
```
