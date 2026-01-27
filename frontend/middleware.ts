import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Middleware for custom JWT authentication.
 * Since JWT tokens are stored in localStorage (client-side only),
 * we can't check authentication here. Auth checks are handled client-side.
 * This middleware is kept minimal for future server-side auth enhancements.
 */
export function middleware(request: NextRequest) {
  // For now, allow all requests through
  // Client-side code handles authentication checks and redirects
  return NextResponse.next();
}

/**
 * Configure which paths the middleware should run on.
 */
export const config = {
  matcher: [
    /*
     * Match all paths except:
     * - api routes (handled separately)
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico (favicon file)
     * - public files
     */
    '/((?!api|_next/static|_next/image|favicon.ico|.*\\..*$).*)',
  ],
};
