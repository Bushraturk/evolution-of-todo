/**
 * PostgreSQL database connection pool.
 * Used by Better Auth for database operations.
 */

import { Pool } from "pg";

export const pool = new Pool({
  connectionString: process.env.DATABASE_URL || "postgresql://localhost:5432/todo_app",
  max: 10,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});
