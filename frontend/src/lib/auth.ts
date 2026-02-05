/**
 * Better Auth server-side configuration.
 * Used for API routes and server-side auth operations.
 */

import { betterAuth } from "better-auth";
import { pool } from "./db";

export const auth = betterAuth({
  database: pool,
  secret: process.env.BETTER_AUTH_SECRET!,
  emailAndPassword: {
    enabled: true,
  },
  advanced: {
    cookiePrefix: "better-auth",
  },
});
