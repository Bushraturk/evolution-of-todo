-- Migration: Add chatbot conversation and message tables
-- Feature: AI-Powered Todo Chatbot (Phase IV)
-- Date: 2026-01-29

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create conversation table
CREATE TABLE conversation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
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
    user_id VARCHAR(255) NOT NULL,
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
