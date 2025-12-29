import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Middleware to protect routes that require authentication.
 * Redirects unauthenticated users to the login page.
 */
export function middleware(request: NextRequest) {
  // Get the session token from cookies
  // Better Auth uses 'better-auth.session_token' cookie
  const sessionToken = request.cookies.get('better-auth.session_token');

  // Define protected paths
  const protectedPaths = ['/'];
  const isProtectedPath = protectedPaths.some(
    (path) => request.nextUrl.pathname === path
  );

  // Define auth paths (login, register)
  const authPaths = ['/login', '/register'];
  const isAuthPath = authPaths.some((path) =>
    request.nextUrl.pathname.startsWith(path)
  );

  // Redirect authenticated users away from auth pages
  if (isAuthPath && sessionToken) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  // Redirect unauthenticated users to login
  if (isProtectedPath && !sessionToken) {
    const loginUrl = new URL('/login', request.url);
    // Add a message parameter for better UX
    loginUrl.searchParams.set('message', 'Please sign in to continue');
    return NextResponse.redirect(loginUrl);
  }

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
