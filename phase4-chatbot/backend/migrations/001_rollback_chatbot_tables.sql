-- Rollback: Remove chatbot conversation and message tables
-- Feature: AI-Powered Todo Chatbot (Phase IV)
-- Date: 2026-01-29

-- Drop tables in reverse order (respects foreign keys)
DROP TABLE IF EXISTS message CASCADE;
DROP TABLE IF EXISTS conversation CASCADE;
