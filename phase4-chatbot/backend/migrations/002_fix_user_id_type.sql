-- Migration: Fix user_id column type from UUID to VARCHAR
-- Issue: user_id should be VARCHAR(255) to store CUID strings from Better Auth
-- Date: 2026-02-04

-- Alter conversation table
ALTER TABLE conversation
ALTER COLUMN user_id TYPE VARCHAR(255);

-- Alter message table
ALTER TABLE message
ALTER COLUMN user_id TYPE VARCHAR(255);

-- Add comments
COMMENT ON COLUMN conversation.user_id IS 'CUID string from Better Auth (not UUID)';
COMMENT ON COLUMN message.user_id IS 'CUID string from Better Auth (not UUID)';
