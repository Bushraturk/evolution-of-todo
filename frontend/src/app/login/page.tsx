'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import AuthForm, { AuthFormData } from '@/components/AuthForm';
import { authClient } from '@/lib/auth-client';

function LoginContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Check for redirect message (e.g., session expired)
  useEffect(() => {
    const msg = searchParams.get('message');
    if (msg) {
      setMessage(msg);
    }
  }, [searchParams]);

  const handleLogin = async (data: AuthFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await authClient.signIn.email({
        email: data.email,
        password: data.password,
      });

      if (result.error) {
        // Handle specific error messages
        if (
          result.error.message?.toLowerCase().includes('invalid') ||
          result.error.message?.toLowerCase().includes('credentials') ||
          result.error.message?.toLowerCase().includes('password')
        ) {
          setError('Invalid email or password');
        } else {
          setError(result.error.message || 'Login failed. Please try again.');
        }
        return;
      }

      // Login successful - redirect to dashboard
      router.push('/');
    } catch (err) {
      console.error('Login error:', err);
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-violet-50 to-fuchsia-50 dark:from-indigo-950 dark:via-purple-950 dark:to-violet-950 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600 bg-clip-text text-transparent">
            Welcome Back
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Sign in to access your tasks
          </p>
        </div>

        {/* Info Message */}
        {message && (
          <div className="mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <p className="text-sm text-blue-600 dark:text-blue-400">{message}</p>
          </div>
        )}

        {/* Form Card */}
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-8 border border-purple-100 dark:border-purple-900">
          <AuthForm
            mode="login"
            onSubmit={handleLogin}
            error={error}
            isLoading={isLoading}
          />

          {/* Register Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Don&apos;t have an account?{' '}
              <Link
                href="/register"
                className="font-semibold text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300 transition-colors"
              >
                Create one
              </Link>
            </p>
          </div>
        </div>

        {/* Back to App */}
        <div className="mt-8 text-center">
          <Link
            href="/"
            className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 transition-colors"
          >
            &larr; Back to app
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-violet-50 to-fuchsia-50 flex items-center justify-center">
        <div className="animate-pulse text-purple-600">Loading...</div>
      </div>
    }>
      <LoginContent />
    </Suspense>
  );
}
