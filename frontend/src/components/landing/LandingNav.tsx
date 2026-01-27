'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { slideInFromLeft } from '@/lib/animations';
import { useSession } from '@/lib/auth-client';
import UserNav from '@/components/UserNav';

export default function LandingNav() {
  const { data: session, isPending } = useSession();

  return (
    <motion.nav
      initial="hidden"
      animate="visible"
      variants={slideInFromLeft}
      className="fixed top-0 left-0 right-0 z-50 glass-strong"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo/Brand */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-violet-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">T</span>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-violet-600 to-purple-600 bg-clip-text text-transparent">
              TodoApp
            </span>
          </Link>

          {/* Auth Buttons or User Nav */}
          <div className="flex items-center space-x-4">
            {isPending ? (
              // Loading state
              <div className="w-8 h-8 bg-purple-200 dark:bg-purple-800 rounded-full animate-pulse"></div>
            ) : session?.user ? (
              // Authenticated - show user nav with dashboard link
              <div className="flex items-center gap-4">
                <Link
                  href="/dashboard"
                  className="px-4 py-2 text-purple-700 dark:text-purple-300 hover:text-purple-900 dark:hover:text-purple-100 font-medium transition-colors"
                >
                  Dashboard
                </Link>
                <UserNav />
              </div>
            ) : (
              // Not authenticated - show sign in buttons
              <>
                <Link
                  href="/login"
                  className="px-4 py-2 text-purple-700 dark:text-purple-300 hover:text-purple-900 dark:hover:text-purple-100 font-medium transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  href="/register"
                  className="px-6 py-2 bg-gradient-to-r from-violet-500 to-purple-600 text-white rounded-lg font-medium hover:from-violet-600 hover:to-purple-700 transition-all shadow-md hover:shadow-lg"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </motion.nav>
  );
}
