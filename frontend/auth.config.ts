/**
 * Better Auth CLI configuration file.
 * This file is used by the Better Auth CLI for migrations.
 */

import { betterAuth } from "better-auth";
import { Pool } from "pg";

export default betterAuth({
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
  }),
});
