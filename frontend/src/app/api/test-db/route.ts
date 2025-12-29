/**
 * Test database connection endpoint.
 */

import { Pool } from "pg";
import { NextResponse } from "next/server";

export async function GET() {
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: {
      rejectUnauthorized: false,
    },
  });

  try {
    // Test connection
    const client = await pool.connect();

    // Check tables
    const result = await client.query(`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public'
    `);

    client.release();
    await pool.end();

    return NextResponse.json({
      success: true,
      database_url_set: !!process.env.DATABASE_URL,
      tables: result.rows.map(r => r.table_name),
    });
  } catch (error: unknown) {
    const err = error as Error & { code?: string };
    return NextResponse.json({
      success: false,
      error: err.message,
      code: err.code,
      database_url_set: !!process.env.DATABASE_URL,
    }, { status: 500 });
  }
}
